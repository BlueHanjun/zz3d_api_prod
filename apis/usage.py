from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 导入数据库模块
from db.database import create_connection, close_connection, execute_query

router = APIRouter()


class UsageSummaryRequest(BaseModel):
    period: str = Query("monthly", description="统计周期 (daily/weekly/monthly)")
    date: str = Query("2023-01", description="日期 (格式: YYYY-MM 或 YYYY-MM-DD)")


class UsageRecord(BaseModel):
    date: str
    service_name: str
    count: int
    total_cost: float


class UsageSummaryResponse(BaseModel):
    period: str
    date: str
    records: List[UsageRecord]


def get_usage_summary_from_db(user_id: str, period: str, date: str) -> List[dict]:
    """从数据库查询用量统计数据"""
    connection = create_connection()
    if not connection:
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
        
        result = execute_query(connection, query, (user_id, date_param))
        
        # 确保total_cost是float类型
        for record in result:
            record['total_cost'] = float(record['total_cost'])
        
        return result
    finally:
        close_connection(connection)


from fastapi import Header, HTTPException

# 导入JWT解码和用户查询函数
from .auth import get_current_user as auth_get_current_user


# 依赖项：获取当前用户
async def get_current_user(authorization: str = Header(None)):
    return await auth_get_current_user(authorization)


@router.get("/summary", response_model=UsageSummaryResponse, summary="获取用量统计数据")
async def usage_summary(
    period: str = Query("monthly", description="统计周期 (daily/weekly/monthly)"),
    date: str = Query("2023-01", description="日期 (格式: YYYY-MM 或 YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取用量统计数据
    - 请求参数：?period=monthly&date=2025-08
    - 逻辑：从 usage_records 表中查询和聚合指定时间范围内的用量数据，格式化后返回给前端用于渲染图表。
    """
    # 查询用量统计数据
    records = get_usage_summary_from_db(current_user["id"], period, date)
    
    # 转换date字段为字符串格式
    for record in records:
        if 'date' in record and hasattr(record['date'], 'strftime'):
            record['date'] = record['date'].strftime('%Y-%m-%d')
    
    return UsageSummaryResponse(
        period=period,
        date=date,
        records=[UsageRecord(**record) for record in records]
    )