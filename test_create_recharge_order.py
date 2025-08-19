import requests
import json

# 测试手机号
PHONE_NUMBER = "18694558637"

# 发送验证码
print("正在发送验证码...")
send_code_response = requests.post("http://localhost:8000/api/auth/send-code", json={"phone_number": PHONE_NUMBER})
print(f"发送验证码响应: {send_code_response.status_code} {send_code_response.text}")

# 检查发送验证码是否成功
if send_code_response.status_code != 200:
    print(f"发送验证码失败，状态码: {send_code_response.status_code}")
    print(f"错误信息: {send_code_response.text}")
    exit(1)

# 获取用户输入的验证码
verification_code = input("请输入您收到的验证码: ")

# 登录获取JWT令牌
print("正在登录获取JWT令牌...")
login_response = requests.post("http://localhost:8000/api/auth/login", json={
    "phone_number": PHONE_NUMBER,
    "code": verification_code
})

if login_response.status_code != 200:
    print(f"登录失败，状态码: {login_response.status_code}")
    print(f"错误信息: {login_response.text}")
    exit(1)

# 提取JWT令牌
jwt_token = login_response.json()["token"]
print(f"获取到的JWT令牌: {jwt_token}")

# 创建充值订单
print("正在创建充值订单...")
recharge_response = requests.post(
    "http://localhost:8000/api/billing/recharge",
    headers={"Authorization": f"Bearer {jwt_token}"},
    json={
        "amount": 100.00,
        "payment_method": "wechat_pay"
    }
)

# 输出响应
print(f"创建充值订单响应状态码: {recharge_response.status_code}")
print(f"创建充值订单响应内容: {recharge_response.text}")

# 尝试解析JSON响应
try:
    response_data = recharge_response.json()
    print(f"解析后的响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
except json.JSONDecodeError:
    print("响应不是有效的JSON格式")
    # 尝试打印部分内容以诊断问题
    print(f"响应内容前100字符: {recharge_response.text[:100]}")