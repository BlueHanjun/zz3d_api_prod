import requests
import json

# 基础URL
BASE_URL = "http://localhost:8000"

# JWT令牌（需要替换为有效的用户令牌）
JWT_TOKEN = "fake-jwt-token-for-18612345678"


def create_api_key():
    """创建一个新的API密钥用于测试"""
    url = f"{BASE_URL}/api/keys/"
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 请求数据
    data = {
        "name": "OpenAPI测试密钥"
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # 输出响应状态码和内容
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # 检查响应是否成功
        if response.status_code == 200:
            response_data = response.json()
            print(f"创建API密钥成功！")
            print(f"API密钥: {response_data['key']}")
            print(f"请将此密钥用于测试OpenAPI接口")
            return response_data['key']
        else:
            print(f"创建API密钥失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"请求异常: {e}")
        return None


def main():
    """主函数"""
    print("开始创建用于测试的API密钥...")
    api_key = create_api_key()
    if api_key:
        print(f"\n请使用以下API密钥测试OpenAPI接口:")
        print(f"X-API-Key: {api_key}")


if __name__ == "__main__":
    main()