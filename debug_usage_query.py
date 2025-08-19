#!/usr/bin/env python3

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import create_connection, close_connection, execute_query

def debug_get_usage_summary_from_db(user_id: str, period: str, date: str) -> list:
    """调试版本的用量统计查询函数"""
    print(f"调试查询: user_id={user_id}, period={period}, date={date}")
    
    connection = create_connection()
    if not connection:
        print("无法创建数据库连接")
        return []
    
    try:
        # 根据周期类型构建SQL查询
        if period == "daily":
            # 按天统计，查询指定日期的数据
            date_condition = "DATE(timestamp) = %s"
            date_param = date
        elif period == "weekly":
            # 按周统计，查询指定周的数据
            date_condition = "YEARWEEK(timestamp, 1) = YEARWEEK(%s, 1)"
            date_param = date
        else:  # monthly
            # 按月统计，查询指定月的数据
            date_condition = "DATE_FORMAT(timestamp, '%Y-%m') = %s"
            date_param = date
        
        print(f"构建的SQL条件: {date_condition}")
        print(f"参数值: {date_param}")
        
        query = f"""
            SELECT 
                DATE(timestamp) as date,
                service_name,
                COUNT(*) as count,
                SUM(cost) as total_cost
            FROM usage_records 
            WHERE user_id = %s AND {date_condition}
            GROUP BY DATE(timestamp), service_name
            ORDER BY date, service_name
        """
        
        print(f"完整SQL查询: {query}")
        print(f"查询参数: {(user_id, date_param)}")
        
        result = execute_query(connection, query, (user_id, date_param))
        print(f"查询结果: {result}")
        
        # 确保total_cost是float类型
        for record in result:
            record['total_cost'] = float(record['total_cost'])
        
        return result
    finally:
        close_connection(connection)


def main():
    """主函数"""
    # 测试用户ID
    user_id = "03752305-ea60-4857-85d0-f65694dee49f"  # 测试用户的ID
    
    # 测试monthly查询
    print("=== 测试monthly查询 ===")
    monthly_records = debug_get_usage_summary_from_db(user_id, "monthly", "2025-08")
    print(f"最终返回结果: {monthly_records}")

if __name__ == "__main__":
    main()