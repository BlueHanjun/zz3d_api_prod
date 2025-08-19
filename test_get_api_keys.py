import requests

# 使用之前测试中获取的JWT令牌
token = "fake-jwt-token-for-18694558637"

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 发送GET请求获取API密钥列表
response = requests.get("http://127.0.0.1:8001/api/keys/", headers=headers)

# 打印响应结果
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")