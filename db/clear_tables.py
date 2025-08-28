import mysql.connector
from mysql.connector import Error

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

def clear_all_tables():
    """清空所有数据表中的数据"""
    connection = create_connection()
    if not connection:
        print("无法连接到数据库")
        return
    
    cursor = connection.cursor()
    
    try:
        # 禁用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 清空所有表的数据
        tables = ['usage_records', 'transactions', 'api_keys', 'users']
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table}")
            print(f"已清空表 {table}")
        
        # 重新启用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # 提交事务
        connection.commit()
        print("所有表的数据已成功清空")
        
    except Error as e:
        print(f"清空表数据时出错: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    clear_all_tables()