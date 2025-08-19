#!/usr/bin/env python3

# 测试用量统计接口

import requests

# 基础URL
BASE_URL = "http://localhost:8000/api"

# JWT令牌 (用于测试用户 18694558637)
JWT_TOKEN = "fake-jwt-token-for-18694558637"

# 请求头
HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}


def test_usage_summary():
    # 测试 monthly - 使用2025年8月，因为数据库中有这个月的数据
    response = requests.get(f"{BASE_URL}/usage/summary", params={"period": "monthly", "date": "2025-08"}, headers=HEADERS)
    print("Monthly:", response.status_code, response.json())
    
    # 测试 weekly - 使用2025年第34周
    response = requests.get(f"{BASE_URL}/usage/summary", params={"period": "weekly", "date": "2025-08-18"}, headers=HEADERS)
    print("Weekly:", response.status_code, response.json())
    
    # 测试 daily - 使用2025年8月18日
    response = requests.get(f"{BASE_URL}/usage/summary", params={"period": "daily", "date": "2025-08-18"}, headers=HEADERS)
    print("Daily:", response.status_code, response.json())

if __name__ == "__main__":
    test_usage_summary()