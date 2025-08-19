#!/usr/bin/env python3

import random
from datetime import datetime, timedelta
from db.database import create_connection, close_connection, execute_query

# 获取测试用户ID
from create_test_user import create_test_user

def generate_usage_test_data():
    # 创建测试用户并获取用户ID
    user_id = create_test_user()
    
    # 创建数据库连接
    connection = create_connection()
    if not connection:
        print("无法连接到数据库")
        return
    
    try:
        # 生成30天的测试数据
        base_date = datetime.now() - timedelta(days=30)
        service_names = ["api_service_1", "api_service_2", "api_service_3"]
        
        for i in range(30):
            current_date = base_date + timedelta(days=i)
            
            # 每天生成1-5条记录
            for _ in range(random.randint(1, 5)):
                service_name = random.choice(service_names)
                cost = round(random.uniform(0.01, 0.1), 4)
                
                # 插入数据到usage_records表
                query = """
                    INSERT INTO usage_records (user_id, api_key_id, service_name, cost, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """
                execute_query(connection, query, (
                    user_id,
                    "test-api-key-id",
                    service_name,
                    cost,
                    current_date
                ))
        
        print(f"成功生成测试数据，用户ID: {user_id}")
    
    except Exception as e:
        print(f"生成测试数据时出错: {e}")
    finally:
        close_connection(connection)

if __name__ == "__main__":
    generate_usage_test_data()