import requests
import json

# API端点
url = "http://127.0.0.1:8001/api/keys/"

# 请求头
headers = {
    "Authorization": "Bearer fake-jwt-token-for-18694558637",
    "Content-Type": "application/json"
}

# 请求体
data = {
    "name": "测试密钥"
}

# 发送POST请求
response = requests.post(url, headers=headers, data=json.dumps(data))

# 打印响应
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")