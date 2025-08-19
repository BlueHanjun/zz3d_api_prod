import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000"

# 测试用户手机号
TEST_PHONE_NUMBER = "18694558637"

# 根据user.py中的实现，JWT令牌格式为fake-jwt-token-for-{手机号}
JWT_TOKEN = f"fake-jwt-token-for-{TEST_PHONE_NUMBER}"


def test_usage_summary(period, date):
    """测试用量统计接口"""
    url = f"{BASE_URL}/api/usage/summary"
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 设置查询参数
    params = {
        "period": period,
        "date": date
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, headers=headers, params=params)
        
        # 输出响应状态码和内容
        print(f"用量统计接口 ({period}, {date}) 响应状态码: {response.status_code}")
        print(f"用量统计接口 ({period}, {date}) 响应内容: {response.text}")
        
        # 检查响应是否成功
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"解析后的JSON数据:")
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
                return response_data
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"请求异常: {e}")
        return None


def main():
    """主函数"""
    print(f"开始测试用量统计接口，使用手机号: {TEST_PHONE_NUMBER}")
    
    # 测试monthly周期
    print("\n=== 测试monthly周期 ===")
    test_usage_summary("monthly", "2023-01")
    
    # 测试weekly周期
    print("\n=== 测试weekly周期 ===")
    test_usage_summary("weekly", "2023-01-01")
    
    # 测试daily周期
    print("\n=== 测试daily周期 ===")
    test_usage_summary("daily", "2023-01-01")


if __name__ == "__main__":
    main()