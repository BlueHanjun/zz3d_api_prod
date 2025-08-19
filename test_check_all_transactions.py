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

# 查询所有交易记录
def check_all_transactions():
    """检查所有交易记录"""
    connection = create_connection()
    if not connection:
        print("数据库连接失败")
        return
    
    try:
        # 查询所有交易记录
        transaction_query = "SELECT * FROM transactions ORDER BY created_at DESC"
        transaction_result = execute_query(connection, transaction_query)
        
        print(f"\n所有交易记录 (共 {len(transaction_result)} 条):")
        if transaction_result:
            for i, transaction in enumerate(transaction_result, 1):
                print(f"\n--- 记录 {i} ---")
                print(f"ID: {transaction['id']}")
                print(f"用户ID: {transaction['user_id']}")
                print(f"金额: {transaction['amount']}")
                print(f"状态: {transaction['status']}")
                print(f"支付方式: {transaction['payment_method']}")
                print(f"外部交易号: {transaction['external_transaction_id']}")
                print(f"创建时间: {transaction['created_at']}")
                print(f"完成时间: {transaction['completed_at']}")
        else:
            print("没有任何交易记录")
    
    finally:
        close_connection(connection)

if __name__ == "__main__":
    check_all_transactions()