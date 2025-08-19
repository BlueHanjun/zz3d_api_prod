import mysql.connector
from mysql.connector import Error
import hashlib
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

def create_connection():
    """创建数据库连接"""
    try:
        connection = mysql.connector.connect(
            host='114.55.226.87',
            port='3306',
            user='root',
            password='MyStr0ng!Passw0rd',
            database='zz3d'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"连接MySQL时出错: {e}")
        return None

def close_connection(connection):
    """关闭数据库连接"""
    if connection and connection.is_connected():
        connection.close()

def execute_query(connection, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """执行查询语句并返回结果"""
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"执行查询时出错: {e}")
        return []
    finally:
        cursor.close()

def execute_update(connection, query: str, params: tuple = ()) -> bool:
    """执行更新语句（INSERT, UPDATE, DELETE）"""
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        return True
    except Error as e:
        print(f"执行更新时出错: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()