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


def test_monthly_query():
    """测试monthly查询SQL"""
    connection = create_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 测试用户ID
        user_id = "03752305-ea60-4857-85d0-f65694dee49f"
        date_param = "2025-08"
        
        # 执行monthly查询SQL
        query = """
            SELECT 
                DATE(timestamp) as date,
                service_name,
                COUNT(*) as count,
                SUM(cost) as total_cost
            FROM usage_records 
            WHERE user_id = %s AND DATE_FORMAT(timestamp, '%Y-%m') = %s
            GROUP BY DATE(timestamp), service_name
            ORDER BY date, service_name
        """
        
        print(f"执行查询: {query}")
        print(f"参数: user_id={user_id}, date_param={date_param}")
        
        cursor.execute(query, (user_id, date_param))
        results = cursor.fetchall()
        
        print(f"\n查询结果 ({len(results)} 条记录):")
        for record in results:
            print(f"  {record}")
        
    except Error as e:
        print(f"执行查询时出错: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL连接已关闭")

if __name__ == "__main__":
    test_monthly_query()