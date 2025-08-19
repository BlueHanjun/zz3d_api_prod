import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试支付回调
def test_payment_webhook(transaction_id: str):
    """测试支付回调接口"""
    # 准备回调数据
    webhook_data = {
        "transaction_id": transaction_id,
        "status": "completed",
        "external_transaction_id": "ext-12345678"
    }
    
    try:
        # 调用支付回调接口
        response = requests.post(f"{BASE_URL}/api/billing/webhook", json=webhook_data)
        print(f"支付回调接口响应状态码: {response.status_code}")
        print(f"支付回调接口响应内容: {response.text}")
        
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
    # 使用新创建的交易ID
    transaction_id = "2b73cb35-6c51-4578-a15e-633ed0255355"
    print(f"测试交易ID: {transaction_id}")
    test_payment_webhook(transaction_id)