from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
import hashlib

# 导入数据库模块
from db.database import create_connection, close_connection, execute_query, execute_update

router = APIRouter()

class ApiResponse(BaseModel):
    message: str

def verify_api_key(api_key: str) -> dict:
    """验证API密钥并返回用户信息"""
    connection = create_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="数据库连接失败")
    
    try:
        # 计算密钥哈希值
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # 直接使用完整密钥哈希查询API密钥信息
        query = "SELECT id, user_id, key_hash FROM api_keys WHERE key_hash = %s"
        result = execute_query(connection, query, (key_hash,))
        
        if not result:
            raise HTTPException(status_code=401, detail="无效的API密钥")
        
        key_info = result[0]
        
        # 验证密钥哈希
        if hashlib.sha256(api_key.encode()).hexdigest() != key_info['key_hash']:
            raise HTTPException(status_code=401, detail="无效的API密钥")
        
        # 更新最后使用时间
        update_query = "UPDATE api_keys SET last_used_at = NOW() WHERE id = %s"
        execute_update(connection, update_query, (key_info['id'],))
        
        # 获取用户信息
        user_query = "SELECT id, balance FROM users WHERE id = %s"
        user_result = execute_query(connection, user_query, (key_info['user_id'],))
        
        if not user_result:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return user_result[0]
    finally:
        close_connection(connection)

def deduct_balance(user_id: str, amount: float) -> bool:
    """扣除用户余额"""
    connection = create_connection()
    if not connection:
        return False
    
    try:
        # 检查余额是否足够
        balance_query = "SELECT balance FROM users WHERE id = %s"
        balance_result = execute_query(connection, balance_query, (user_id,))
        
        if not balance_result or balance_result[0]['balance'] < amount:
            return False
        
        # 扣除余额
        update_query = "UPDATE users SET balance = balance - %s WHERE id = %s"
        success = execute_update(connection, update_query, (amount, user_id))
        
        # 记录使用情况
        if success:
            usage_query = """
                INSERT INTO usage_records (id, user_id, api_key_id, service_name, cost) 
                VALUES (UUID(), %s, (SELECT id FROM api_keys WHERE user_id = %s LIMIT 1), %s, %s)
            """
            execute_update(connection, usage_query, (user_id, user_id, "openapi_simulation", amount))
        
        return success
    finally:
        close_connection(connection)

async def get_api_key_authorization(x_api_key: str = Header(None, alias="X-API-Key")):
    """API密钥认证依赖"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="缺少API密钥")
    
    user_info = verify_api_key(x_api_key)
    return user_info

@router.get("/simulate", response_model=ApiResponse, summary="模拟OpenAPI调用")
async def simulate_openapi(current_user: dict = Depends(get_api_key_authorization)):
    """
    模拟OpenAPI调用接口
    - 需要通过X-API-Key头部提供有效的API密钥
    - 成功调用后扣除0.1元费用
    """
    # 扣除费用
    if not deduct_balance(current_user['id'], 0.1):
        raise HTTPException(status_code=400, detail="余额不足")
    
    return ApiResponse(message="调用成功，扣费0.1元。")