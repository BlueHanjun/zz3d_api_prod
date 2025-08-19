from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import uuid
import hashlib
import random
import string
from datetime import datetime

# 导入数据库模块
from db.database import create_connection, close_connection, execute_query, execute_update

router = APIRouter()


class ApiKeyInfo(BaseModel):
    id: str
    name: str
    key_prefix: str
    created_at: str
    last_used_at: str = None


class CreateApiKeyRequest(BaseModel):
    name: str


class CreateApiKeyResponse(BaseModel):
    id: str
    name: str
    key: str  # 完整的API密钥
    key_prefix: str
    created_at: str


def get_api_keys_by_user_id(user_id: str) -> List[dict]:
    """从数据库查询用户的API密钥"""
    connection = create_connection()
    if not connection:
        return []
    
    try:
        query = """
            SELECT id, name, key_prefix, created_at, last_used_at 
            FROM api_keys 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        result = execute_query(connection, query, (user_id,))
        
        # 将datetime对象转换为字符串格式
        for api_key in result:
            if api_key['created_at']:
                api_key['created_at'] = api_key['created_at'].strftime('%Y-%m-%dT%H:%M:%S')
            if api_key['last_used_at'] and isinstance(api_key['last_used_at'], datetime):
                api_key['last_used_at'] = api_key['last_used_at'].strftime('%Y-%m-%dT%H:%M:%S')
        
        return result
    finally:
        close_connection(connection)


def create_api_key_in_db(user_id: str, name: str, key_hash: str, key_prefix: str) -> dict:
    """在数据库中创建API密钥"""
    connection = create_connection()
    if not connection:
        raise Exception("数据库连接失败")
    
    try:
        api_key_id = str(uuid.uuid4())
        query = """
            INSERT INTO api_keys (id, user_id, name, key_hash, key_prefix) 
            VALUES (%s, %s, %s, %s, %s)
        """
        success = execute_update(connection, query, (api_key_id, user_id, name, key_hash, key_prefix))
        
        if not success:
            raise Exception("创建API密钥失败")
        
        # 查询并返回创建的API密钥信息
        select_query = "SELECT id, name, key_prefix, created_at, last_used_at FROM api_keys WHERE id = %s"
        result = execute_query(connection, select_query, (api_key_id,))
        
        if result:
            # 将datetime对象转换为字符串格式
            api_key = result[0]
            if api_key['created_at']:
                api_key['created_at'] = api_key['created_at'].strftime('%Y-%m-%dT%H:%M:%S')
            if api_key['last_used_at']:
                api_key['last_used_at'] = api_key['last_used_at'].strftime('%Y-%m-%dT%H:%M:%S')
            return api_key
        else:
            raise Exception("查询创建的API密钥失败")
    finally:
        close_connection(connection)


def delete_api_key_from_db(key_id: str, user_id: str) -> bool:
    """从数据库删除API密钥"""
    connection = create_connection()
    if not connection:
        return False
    
    try:
        query = "DELETE FROM api_keys WHERE id = %s AND user_id = %s"
        cursor = connection.cursor()
        cursor.execute(query, (key_id, user_id))
        connection.commit()
        success = cursor.rowcount > 0
        cursor.close()
        return success
    except Exception as e:
        print(f"删除API密钥时出错: {e}")
        connection.rollback()
        return False
    finally:
        close_connection(connection)


from fastapi import Header, HTTPException

# 导入JWT解码和用户查询函数
from .user import decode_token, get_user_by_phone_number


# 依赖项：获取当前用户
async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少授权令牌")
    
    try:
        # 提取JWT令牌（去除"Bearer "前缀）
        token = authorization.replace("Bearer ", "")
        # 解码JWT令牌获取用户信息
        token_data = decode_token(token)
        # 根据手机号查询用户信息
        user = get_user_by_phone_number(token_data.phone_number)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="无效的令牌")


@router.get("/", response_model=List[ApiKeyInfo], summary="获取当前用户的所有API密钥")
async def list_api_keys(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户的所有API密钥
    - 逻辑：返回与当前用户关联的所有密钥列表（包含名称、前缀、创建日期等）。
    """
    api_keys = get_api_keys_by_user_id(current_user["id"])
    return [ApiKeyInfo(**key) for key in api_keys]


@router.post("/", response_model=CreateApiKeyResponse, summary="创建一个新的API密钥")
async def create_api_key(request: CreateApiKeyRequest, current_user: dict = Depends(get_current_user)):
    """
    创建一个新的API密钥
    - 请求体：{ "name": "我的新密钥" }
    - 逻辑：生成一个新的、唯一的密钥，计算其哈希值存入数据库。
      在响应中返回完整的、未加密的密钥，并明确告知用户这是唯一一次看到完整密钥的机会。
    """
    # 生成新的API密钥
    key = "zz-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
    
    # 计算密钥哈希值
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    
    # 提取密钥前缀
    key_prefix = key[:7]
    
    # 保存到数据库
    api_key = create_api_key_in_db(current_user["id"], request.name, key_hash, key_prefix)
    
    return CreateApiKeyResponse(
        id=api_key["id"],
        name=api_key["name"],
        key=key,  # 返回完整密钥
        key_prefix=api_key["key_prefix"],
        created_at=api_key["created_at"]
    )


@router.delete("/{key_id}", summary="删除一个API密钥")
async def delete_api_key(key_id: str, current_user: dict = Depends(get_current_user)):
    """
    删除一个API密钥
    - 逻辑：根据 keyId 删除指定的密钥记录。
    """
    success = delete_api_key_from_db(key_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="API密钥不存在")
    
    return {"message": "API密钥删除成功"}