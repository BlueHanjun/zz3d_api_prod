import mysql.connector
from mysql.connector import Error
import uuid

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
            print("成功连接到MySQL数据库")
            return connection
    except Error as e:
        print(f"连接MySQL时出错: {e}")
        return None


def create_test_user(phone_number):
    """创建测试用户"""
    connection = create_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # 检查用户是否已存在
        check_query = "SELECT id FROM users WHERE phone_number = %s"
        cursor.execute(check_query, (phone_number,))
        result = cursor.fetchone()
        
        if result:
            print(f"用户 {phone_number} 已存在，ID: {result[0]}")
            return True
        
        # 创建新用户
        user_id = str(uuid.uuid4())
        insert_query = """
            INSERT INTO users (id, phone_number, real_name, id_number, balance) 
            VALUES (%s, %s, %s, %s, %s)
        """
        # 使用空的加密值作为默认值
        cursor.execute(insert_query, (user_id, phone_number, b'', b'', 0.00))
        connection.commit()
        
        print(f"成功创建测试用户 {phone_number}，ID: {user_id}")
        return True
        
    except Error as e:
        print(f"创建用户时出错: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL连接已关闭")


def main():
    """主函数"""
    # 测试用户手机号
    test_phone_number = "18694558637"
    
    print(f"开始创建测试用户: {test_phone_number}")
    success = create_test_user(test_phone_number)
    
    if success:
        print("测试用户创建成功！")
    else:
        print("测试用户创建失败！")


if __name__ == "__main__":
    main()