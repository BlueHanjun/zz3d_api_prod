import requests
import json

# 基础URL
BASE_URL = "http://localhost:8000"

# 测试API密钥（需要替换为数据库中存在的有效密钥）
# API密钥格式为: zz-xxxxxxxxxxxxxxxxxxxx (以'zz-'开头的23位字符串)
API_KEY = "zz-4eke64z90x08cz4fxqp1"


def test_openapi():
    """测试模拟OpenAPI接口"""
    url = f"{BASE_URL}/api/openapi/simulate"
    
    # 设置请求头
    headers = {
        "X-API-Key": API_KEY
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, headers=headers)
        
        # 输出响应状态码和内容
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # 检查响应是否成功
        if response.status_code == 200:
            print("OpenAPI接口调用成功！")
        else:
            print(f"OpenAPI接口调用失败: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")


def main():
    """主函数"""
    print("开始测试模拟OpenAPI接口...")
    test_openapi()


if __name__ == "__main__":
    main()