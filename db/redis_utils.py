import redis
import json
from typing import Optional

# Redis连接配置
REDIS_HOST = '114.55.226.87'  # 替换为您的Redis服务器地址
REDIS_PORT = 6379
REDIS_PASSWORD = '6400347xX'  # 如果有密码的话
REDIS_DB = 0

# 创建Redis连接池
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
    decode_responses=True
)

def get_redis_connection():
    """获取Redis连接"""
    return redis.Redis(connection_pool=redis_pool)

def store_verification_code(phone_number: str, code: str, expire_minutes: int = 5):
    """存储验证码到Redis"""
    redis_conn = get_redis_connection()
    key = f"verification_code:{phone_number}"
    value = json.dumps({"code": code})
    # 设置过期时间（秒）
    redis_conn.setex(key, expire_minutes * 60, value)

def get_verification_code(phone_number: str) -> Optional[dict]:
    """从Redis获取验证码"""
    redis_conn = get_redis_connection()
    key = f"verification_code:{phone_number}"
    value = redis_conn.get(key)
    if value:
        return json.loads(value)
    return None

def delete_verification_code(phone_number: str):
    """从Redis删除验证码"""
    redis_conn = get_redis_connection()
    key = f"verification_code:{phone_number}"
    redis_conn.delete(key)

def add_token_to_blacklist(token: str, expire_minutes: int = 30):
    """将令牌添加到黑名单"""
    redis_conn = get_redis_connection()
    key = f"token_blacklist:{token}"
    redis_conn.setex(key, expire_minutes * 60, "blacklisted")

def is_token_blacklisted(token: str) -> bool:
    """检查令牌是否在黑名单中"""
    redis_conn = get_redis_connection()
    key = f"token_blacklist:{token}"
    return redis_conn.exists(key) > 0