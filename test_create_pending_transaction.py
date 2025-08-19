import mysql.connector
from mysql.connector import Error
import uuid
from datetime import datetime

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

def execute_update(connection, query: str, params: tuple = ()):
    """执行更新语句并返回是否成功"""
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"执行更新时出错: {e}")
        connection.rollback()
        return False
    finally:
        cursor.close()

def close_connection(connection):
    """关闭数据库连接"""
    if connection and connection.is_connected():
        connection.close()

def create_pending_transaction(user_id: str, amount: float, payment_method: str):
    """创建待处理交易记录"""
    connection = create_connection()
    if not connection:
        print("数据库连接失败")
        return None
    
    try:
        transaction_id = str(uuid.uuid4())
        query = """
            INSERT INTO transactions 
            (id, user_id, amount, status, payment_method, external_transaction_id, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        success = execute_update(connection, query, 
                               (transaction_id, user_id, amount, "pending", payment_method, None, created_at))
        
        if success:
            print(f"成功创建待处理交易记录: {transaction_id}")
            return transaction_id
        else:
            print("创建交易记录失败")
            return None
    finally:
        close_connection(connection)

if __name__ == "__main__":
    # 使用之前测试中使用的用户ID
    user_id = "03752305-ea60-4857-85d0-f65694dee49f"
    amount = 100.00
    payment_method = "wechat_pay"
    
    print(f"为用户 {user_id} 创建金额为 {amount} 的待处理交易记录")
    transaction_id = create_pending_transaction(user_id, amount, payment_method)
    
    if transaction_id:
        print(f"新创建的交易ID: {transaction_id}")