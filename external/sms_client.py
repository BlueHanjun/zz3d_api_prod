import hashlib
import time
import random
import requests
from typing import Optional

class SMSClient:
    """外部短信服务商API客户端"""
    
    def __init__(self, account_id: str, password: str, sms_encrypt_key: str, 
                 product_id: int, extend_no: Optional[str] = None):
        """
        初始化短信客户端
        
        Args:
            account_id: 提交账户
            password: 密码原文
            sms_encrypt_key: 固定的加密key
            product_id: 产品编码
            extend_no: 企业代码（可选）
        """
        self.account_id = account_id
        self.password = password
        self.sms_encrypt_key = sms_encrypt_key
        self.product_id = product_id
        self.extend_no = extend_no
        self.api_url = "https://api.51welink.com/EncryptionSubmit/SendSms.ashx"
    
    def _generate_md5_password(self) -> str:
        """生成MD5加密后的密码"""
        md5_input = self.password + self.sms_encrypt_key
        md5_hash = hashlib.md5(md5_input.encode('utf-8')).hexdigest().upper()
        return md5_hash
    
    def _generate_access_key(self, phone_nos: str, random_num: int, timestamp: int) -> str:
        """
        生成AccessKey
        
        Args:
            phone_nos: 接收号码（第一个）
            random_num: 随机数
            timestamp: Unix时间戳
        
        Returns:
            str: 加密后的AccessKey
        """
        # 获取第一个手机号码
        first_phone = phone_nos.split(',')[0]
        
        # 生成MD5密码
        md5_password = self._generate_md5_password()
        
        # 构造加密字符串（注意参数顺序）
        access_key_str = f"AccountId={self.account_id}&PhoneNos={first_phone}&Password={md5_password}&Random={random_num}&Timestamp={timestamp}"
        
        # 生成SHA256哈希
        access_key = hashlib.sha256(access_key_str.encode('utf-8')).hexdigest().lower()
        
        return access_key
    
    def send_sms(self, phone_nos: str, content: str, send_time: Optional[str] = None, 
                 out_id: Optional[str] = None) -> dict:
        """
        发送短信
        
        Args:
            phone_nos: 接收号码，多个号码用英文半角逗号隔开
            content: 短信内容
            send_time: 定时发送时间（可选）
            out_id: 用户自定义参数（可选）
        
        Returns:
            dict: API响应结果
        """
        # 生成时间戳
        timestamp = int(time.time())
        
        # 生成随机数
        random_num = random.randint(1, 9223372036854775807)
        
        # 生成AccessKey
        access_key = self._generate_access_key(phone_nos, random_num, timestamp)
        
        # 构造请求参数
        params = {
            "AccountId": self.account_id,
            "AccessKey": access_key,
            "Timestamp": timestamp,
            "Random": random_num,
            "Productid": self.product_id,
            "PhoneNos": phone_nos,
            "Content": content
        }
        
        # 添加可选参数
        if self.extend_no:
            params["ExtendNo"] = self.extend_no
        if send_time:
            params["SendTime"] = send_time
        if out_id:
            params["Outid"] = out_id
        
        try:
            # 发送请求
            response = requests.post(self.api_url, data=params)
            response.raise_for_status()
            
            # 返回结果
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }


# # 使用示例
# if __name__ == "__main__":
#     # 导入真实账户信息
#     try:
#         from real_account_info import REAL_ACCOUNT_ID, REAL_PASSWORD, REAL_SMS_ENCRYPT_KEY, REAL_PRODUCT_ID, REAL_EXTEND_NO
#     except ImportError:
#         print("请创建real_account_info.py文件并填写真实账户信息")
#         exit(1)
#     
#     # 初始化客户端
#     client = SMSClient(
#         account_id=REAL_ACCOUNT_ID,
#         password=REAL_PASSWORD,
#         sms_encrypt_key=REAL_SMS_ENCRYPT_KEY,
#         product_id=REAL_PRODUCT_ID,
#         extend_no=REAL_EXTEND_NO
#     )
#     
#     # 发送短信
#     result = client.send_sms(
#         phone_nos="18694558637",
#         content="您的验证码是：123456【微网通联】"
#     )
#     
#     print(result)