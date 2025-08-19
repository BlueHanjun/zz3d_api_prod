#!/usr/bin/env python3

import mysql.connector
from mysql.connector import Error

# 数据库连接配置
DB_CONFIG = {
    'host': '114.55.226.87',
    'port': '3306',
    'user': 'root',
    'password': 'MyStr0ng!Passw0rd',
    'database': 'zz3d'
}

def create_connection():
    """创建数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("成功连接到MySQL数据库")
            return connection
    except Error as e:
        print(f"连接MySQL时出错: {e}")
        return None


def check_user_usage_data(user_id):
    """检查用户的用量数据"""
    connection = create_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 查询用户用量记录总数
        count_query = "SELECT COUNT(*) as count FROM usage_records WHERE user_id = %s"
        cursor.execute(count_query, (user_id,))
        count_result = cursor.fetchone()
        print(f"用户 {user_id} 的用量记录总数: {count_result['count']}")
        
        # 查询最近的10条用量记录
        query = """
            SELECT id, user_id, api_key_id, service_name, cost, timestamp 
            FROM usage_records 
            WHERE user_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 10
        """
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        
        print("\n最近的10条用量记录:")
        for record in results:
            print(f"  ID: {record['id']}, 服务: {record['service_name']}, 费用: {record['cost']}, 时间: {record['timestamp']}")
        
        # 检查是否有本月的数据
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")
        monthly_query = """
            SELECT COUNT(*) as count 
            FROM usage_records 
            WHERE user_id = %s AND DATE_FORMAT(timestamp, '%Y-%m') = %s
        """
        cursor.execute(monthly_query, (user_id, current_month))
        monthly_result = cursor.fetchone()
        print(f"\n用户 {user_id} 在 {current_month} 的用量记录数: {monthly_result['count']}")
        
    except Error as e:
        print(f"查询用量数据时出错: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL连接已关闭")


def main():
    """主函数"""
    # 测试用户ID
    test_user_id = "03752305-ea60-4857-85d0-f65694dee49f"  # 根据之前的输出，这是测试用户的ID
    
    print(f"检查测试用户 {test_user_id} 的用量数据:")
    check_user_usage_data(test_user_id)


if __name__ == "__main__":
    main()