from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# 导入数据库模块
from db.database import create_connection, close_connection, execute_query

router = APIRouter()


class UserInfo(BaseModel):
    id: str
    phone_number: str
    real_name: Optional[str] = None
    id_number: Optional[str] = None
    balance: float
    created_at: str


class TokenData(BaseModel):
    phone_number: str


def get_user_by_phone_number(phone_number: str) -> Optional[dict]:
    """从数据库查询用户信息"""
    connection = create_connection()
    if not connection:
        return None
    
    try:
        query = "SELECT id, phone_number, real_name, id_number, balance, created_at FROM users WHERE phone_number = %s"
        result = execute_query(connection, query, (phone_number,))
        
        if result:
            # 将字节类型字段解码为字符串
            user = result[0]
            if isinstance(user['real_name'], bytes):
                user['real_name'] = user['real_name'].decode('utf-8')
            if isinstance(user['id_number'], bytes):
                user['id_number'] = user['id_number'].decode('utf-8')
            return user
        return None
    finally:
        close_connection(connection)


# 模拟JWT解码函数
def decode_token(token: str) -> TokenData:
    # 模拟解码JWT令牌获取用户信息
    # 实际项目中应使用JWT库进行解码
    if token.startswith("fake-jwt-token-for-"):
        phone_number = token.replace("fake-jwt-token-for-", "")
        return TokenData(phone_number=phone_number)
    else:
        raise HTTPException(status_code=401, detail="无效的令牌")


# 依赖项：获取当前用户
def get_current_user(token: str = Depends(lambda: "fake-token")):
    token_data = decode_token(token)
    user = get_user_by_phone_number(token_data.phone_number)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.get("/me", response_model=UserInfo, summary="获取当前登录用户的信息")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前登录用户的信息
    - 逻辑：通过身份令牌解析出用户ID，从 users 表中查询并返回用户信息（手机号、实名信息、余额等）。
    """
    return UserInfo(
        id=current_user["id"],
        phone_number=current_user["phone_number"],
        real_name=current_user["real_name"],
        id_number=current_user["id_number"],
        balance=current_user["balance"],
        created_at=current_user["created_at"]
    )