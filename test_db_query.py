#!/usr/bin/env python3

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apis.usage import get_usage_summary_from_db

def test_db_query():
    """测试数据库查询函数"""
    # 测试用户ID
    user_id = "03752305-ea60-4857-85d0-f65694dee49f"  # 测试用户的ID
    
    # 测试monthly查询
    print("测试monthly查询 (2025-08):")
    monthly_records = get_usage_summary_from_db(user_id, "monthly", "2025-08")
    print(f"返回记录数: {len(monthly_records)}")
    for record in monthly_records:
        print(f"  {record}")
    
    # 测试weekly查询
    print("\n测试weekly查询 (2025-08-18):")
    weekly_records = get_usage_summary_from_db(user_id, "weekly", "2025-08-18")
    print(f"返回记录数: {len(weekly_records)}")
    for record in weekly_records:
        print(f"  {record}")
    
    # 测试daily查询
    print("\n测试daily查询 (2025-08-18):")
    daily_records = get_usage_summary_from_db(user_id, "daily", "2025-08-18")
    print(f"返回记录数: {len(daily_records)}")
    for record in daily_records:
        print(f"  {record}")

if __name__ == "__main__":
    test_db_query()