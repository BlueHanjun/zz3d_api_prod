import requests

# 使用之前测试中获取的JWT令牌
token = "fake-jwt-token-for-18694558637"

# 设置请求头
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 要删除的API密钥ID（从获取密钥列表的响应中获取）
key_id = "90f947e0-e210-49ef-aeab-4a99bfd5a0bb"

# 发送DELETE请求删除API密钥
response = requests.delete(f"http://127.0.0.1:8001/api/keys/{key_id}", headers=headers)

# 打印响应结果
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")