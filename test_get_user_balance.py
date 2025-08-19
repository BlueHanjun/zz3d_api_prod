import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试获取用户余额接口
def test_get_user_balance():
    """测试获取用户余额接口"""
    # 注意：在实际测试中，您需要使用有效的JWT令牌
    # 这里我们使用一个示例令牌，您需要替换为实际的有效令牌
    headers = {
        "Authorization": "Bearer fake-jwt-token-for-18612345678",
        "Content-Type": "application/json"
    }
    
    try:
        # 调用获取用户余额接口
        response = requests.get(f"{BASE_URL}/api/billing/balance", headers=headers)
        print(f"获取用户余额接口响应状态码: {response.status_code}")
        print(f"获取用户余额接口响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n解析后的JSON数据:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                print(f"响应内容前100字符: {response.text[:100]}")
        else:
            print(f"请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_get_user_balance()