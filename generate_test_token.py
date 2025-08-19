#!/usr/bin/env python3

import jwt
import datetime

# 使用与测试用户匹配的手机号
TEST_PHONE_NUMBER = "18694558637"

# JWT密钥（应该与API中使用的密钥相同）
JWT_SECRET = "your-secret-key"  # 需要替换为实际的密钥

def generate_test_token(phone_number):
    """生成测试用的JWT令牌"""
    payload = {
        "phone_number": phone_number,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 令牌1小时后过期
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def main():
    """主函数"""
    token = generate_test_token(TEST_PHONE_NUMBER)
    print(f"为手机号 {TEST_PHONE_NUMBER} 生成的JWT令牌:")
    print(token)
    
    # 验证生成的令牌
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print("\n令牌解码成功:")
        print(decoded)
    except jwt.ExpiredSignatureError:
        print("令牌已过期")
    except jwt.InvalidTokenError:
        print("无效的令牌")

if __name__ == "__main__":
    main()