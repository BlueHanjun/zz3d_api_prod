from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
import random
import string
from datetime import datetime, timedelta
from typing import Dict
import uuid

# JWT相关导入
from jose import jwt
import os

# 导入数据库模块
from db.database import create_connection, close_connection, execute_query, execute_update

# 导入Redis工具模块
from db.redis_utils import store_verification_code, get_verification_code, delete_verification_code, add_token_to_blacklist, is_token_blacklisted

# 导入短信客户端模块
from external.sms_client import SMSClient
from external.real_account_info import REAL_ACCOUNT_ID, REAL_PASSWORD, REAL_SMS_ENCRYPT_KEY, REAL_PRODUCT_ID, REAL_EXTEND_NO

router = APIRouter()

# JWT配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class SendCodeRequest(BaseModel):
    phone_number: str


class LoginRequest(BaseModel):
    phone_number: str
    code: str


class LoginResponse(BaseModel):
    token: str


@router.post("/send-code", summary="发送登录验证码")
async def send_code(request: SendCodeRequest):
    """
    发送登录验证码
    - 请求体：{ "phoneNumber": "186..." }
    - 逻辑：生成一个验证码，与手机号关联后临时存储（例如在 Redis 中设置5分钟过期），然后通过短信服务商发送给用户。
    """
    # 生成6位随机数字验证码
    code = ''.join(random.choices(string.digits, k=6))
    
    # 存储验证码到Redis（5分钟过期）
    store_verification_code(request.phone_number, code, 5)
    
    # 初始化短信客户端
    sms_client = SMSClient(
        account_id=REAL_ACCOUNT_ID,
        password=REAL_PASSWORD,
        sms_encrypt_key=REAL_SMS_ENCRYPT_KEY,
        product_id=REAL_PRODUCT_ID,
        extend_no=REAL_EXTEND_NO
    )
    
    # 发送短信验证码
    content = f"您的验证码是：{code}【杭州三分之七科技】"
    result = sms_client.send_sms(
        phone_nos=request.phone_number,
        content=content
    )
    
    # 记录短信发送结果
    print(f"短信发送结果: {result}")
    
    # 检查短信发送结果
    if not result["success"]:
        raise HTTPException(status_code=500, detail=f"短信发送失败: {result.get('error', '未知错误')}")
    
    return {"message": "验证码已发送"}


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(request: LoginRequest):
    """
    用户登录
    - 请求体：{ "phoneNumber": "186...", "code": "123456" }
    - 逻辑：验证手机号和验证码是否匹配且未过期。成功后，生成一个身份令牌（如 JWT），并返回给客户端。
    """
    # 从Redis获取存储的验证码信息
    stored_code_info = get_verification_code(request.phone_number)
    
    # 检查验证码是否存在
    if not stored_code_info:
        raise HTTPException(status_code=400, detail="验证码不存在或已过期")
    
    # 验证验证码
    if request.code != stored_code_info["code"]:
        raise HTTPException(status_code=400, detail="验证码错误")
    
    # 删除已使用的验证码
    delete_verification_code(request.phone_number)
    
    # 检查用户是否存在于数据库中，如果不存在则创建用户
    connection = create_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        # 查询用户是否存在
        query = "SELECT id FROM users WHERE phone_number = %s"
        result = execute_query(connection, query, (request.phone_number,))
        
        if not result:
            # 用户不存在，创建新用户
            user_id = str(uuid.uuid4())
            insert_query = """
                INSERT INTO users (id, phone_number, real_name, id_number, balance) 
                VALUES (%s, %s, %s, %s, %s)
            """
            # 使用空的加密值作为默认值
            success = execute_update(connection, insert_query, 
                                   (user_id, request.phone_number, b'', b'', 0.00))
            
            if not success:
                raise HTTPException(status_code=500, detail="创建用户失败")
    finally:
        close_connection(connection)
    
    # 生成JWT令牌
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": request.phone_number,
        "exp": expire
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return LoginResponse(token=token)


# JWT令牌验证依赖
async def get_current_user(authorization: str = Header(None, alias="Authorization")):
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供访问令牌")
    
    # 从Authorization头部提取Bearer令牌
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="无效的认证方案")
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的认证头部格式")
    
    # 检查令牌是否在黑名单中
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="令牌已失效")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise HTTPException(status_code=401, detail="令牌无效")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="令牌无效")
    
    # 查询用户信息
    connection = create_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        query = "SELECT id, phone_number, real_name, id_number, balance, created_at FROM users WHERE phone_number = %s"
        result = execute_query(connection, query, (phone_number,))
        
        if not result:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        user_info = {
            "id": result[0]["id"],
            "phone_number": result[0]["phone_number"],
            "real_name": result[0]["real_name"],
            "id_number": result[0]["id_number"],
            "balance": float(result[0]["balance"]),
            "created_at": result[0]["created_at"].isoformat()
        }
    finally:
        close_connection(connection)
    
    return user_info


@router.post("/logout", summary="用户登出")
async def logout(authorization: str = Header(None, alias="Authorization")):
    """
    用户登出
    - 逻辑：使当前用户的令牌失效（例如通过黑名单机制）。
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供访问令牌")
    
    # 从Authorization头部提取Bearer令牌
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="无效的认证方案")
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的认证头部格式")
    
    # 将令牌加入黑名单（存储到Redis中）
    add_token_to_blacklist(token, 30)  # 30分钟过期
    
    return {"message": "登出成功"}