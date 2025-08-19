import mysql.connector
from mysql.connector import Error
import hashlib
import uuid
from datetime import datetime

def create_connection():
    """创建数据库连接"""
    try:
        connection = mysql.connector.connect(
            host='114.55.226.87',
            port='3306',
            user='root',
            password='MyStr0ng!Passw0rd'
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
            return connection
    except Error as e:
        print(f"连接MySQL时出错: {e}")
        return None

def create_database(connection):
    """创建数据库"""
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS zz3d")
        print("数据库 'zz3d' 创建成功")
    except Error as e:
        print(f"创建数据库时出错: {e}")
    finally:
        cursor.close()

def create_users_table(connection):
    """创建用户表"""
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                phone_number VARCHAR(20) UNIQUE NOT NULL,
                real_name VARBINARY(255) NOT NULL,
                id_number VARBINARY(255) NOT NULL,
                balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_phone_number (phone_number)
            )
        """)
        print("users 表创建成功")
    except Error as e:
        print(f"创建 users 表时出错: {e}")
    finally:
        cursor.close()

def create_api_keys_table(connection):
    """创建API密钥表"""
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                name VARCHAR(100) NOT NULL,
                key_hash VARCHAR(64) NOT NULL,
                key_prefix VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("api_keys 表创建成功")
    except Error as e:
        print(f"创建 api_keys 表时出错: {e}")
    finally:
        cursor.close()

def create_transactions_table(connection):
    """创建交易表"""
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                status ENUM('pending', 'completed', 'failed') NOT NULL,
                payment_method ENUM('wechat_pay', 'alipay') NOT NULL,
                external_transaction_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("transactions 表创建成功")
    except Error as e:
        print(f"创建 transactions 表时出错: {e}")
    finally:
        cursor.close()

def create_usage_records_table(connection):
    """创建使用记录表"""
    cursor = connection.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_records (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                api_key_id VARCHAR(36) NOT NULL,
                service_name VARCHAR(100) NOT NULL,
                cost DECIMAL(10, 2) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
            )
        """)
        print("usage_records 表创建成功")
    except Error as e:
        print(f"创建 usage_records 表时出错: {e}")
    finally:
        cursor.close()

def main():
    """主函数"""
    connection = create_connection()
    if connection:
        create_database(connection)
        connection.database = 'zz3d'  # 切换到新创建的数据库
        create_users_table(connection)
        create_api_keys_table(connection)
        create_transactions_table(connection)
        create_usage_records_table(connection)
        connection.close()
        print("MySQL连接已关闭")

if __name__ == "__main__":
    main()