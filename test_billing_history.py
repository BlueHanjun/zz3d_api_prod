import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试获取账单历史
def test_billing_history(token: str):
    """测试获取账单历史接口"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # 调用账单历史接口
        response = requests.get(f"{BASE_URL}/api/billing/history", headers=headers)
        print(f"账单历史接口响应状态码: {response.status_code}")
        print(f"账单历史接口响应内容: {response.text}")
        
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
    # 使用之前测试中获取的token
    token = "fake-jwt-token-for-18694558637"
    print(f"使用token: {token}")
    test_billing_history(token)