import mysql.connector
from mysql.connector import Error

# 数据库连接配置
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

def execute_query(connection, query: str, params: tuple = ()):
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

def close_connection(connection):
    """关闭数据库连接"""
    if connection and connection.is_connected():
        connection.close()

def check_user_balance(user_id: str):
    """检查用户余额"""
    connection = create_connection()
    if not connection:
        print("数据库连接失败")
        return
    
    try:
        # 查询用户余额
        query = "SELECT balance FROM users WHERE id = %s"
        result = execute_query(connection, query, (user_id,))
        
        if result:
            balance = float(result[0]['balance'])
            print(f"用户 {user_id} 的余额: {balance:.2f}")
        else:
            print(f"未找到用户 {user_id}")
    finally:
        close_connection(connection)

if __name__ == "__main__":
    # 使用之前测试中使用的用户ID
    user_id = "03752305-ea60-4857-85d0-f65694dee49f"
    print(f"检查用户ID: {user_id}")
    check_user_balance(user_id)