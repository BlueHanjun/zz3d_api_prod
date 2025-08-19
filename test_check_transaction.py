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

# 测试查询特定用户的交易记录
def check_user_transactions(user_id: str):
    """检查特定用户的交易记录"""
    connection = create_connection()
    if not connection:
        print("数据库连接失败")
        return
    
    try:
        # 查询用户信息
        user_query = "SELECT * FROM users WHERE id = %s"
        user_result = execute_query(connection, user_query, (user_id,))
        
        if user_result:
            print(f"用户信息: {user_result[0]}")
        else:
            print(f"未找到ID为 {user_id} 的用户")
            return
        
        # 查询该用户的所有交易记录
        transaction_query = "SELECT * FROM transactions WHERE user_id = %s ORDER BY created_at DESC"
        transaction_result = execute_query(connection, transaction_query, (user_id,))
        
        print(f"\n用户 {user_id} 的交易记录:")
        if transaction_result:
            for transaction in transaction_result:
                print(transaction)
        else:
            print("该用户没有任何交易记录")
    
    finally:
        close_connection(connection)

def list_all_users():
    """列出所有用户"""
    connection = create_connection()
    if not connection:
        print("数据库连接失败")
        return
    
    try:
        # 查询所有用户
        user_query = "SELECT id, phone_number FROM users"
        user_result = execute_query(connection, user_query)
        
        print("所有用户:")
        for user in user_result:
            print(f"ID: {user['id']}, 手机号: {user['phone_number']}")
    
    finally:
        close_connection(connection)

if __name__ == "__main__":
    # 首先列出所有用户
    list_all_users()
    
    print("\n请输入要查询的用户ID:")
    user_id = input()
    
    check_user_transactions(user_id)