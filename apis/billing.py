from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

# 导入数据库模块
from db.database import create_connection, close_connection, execute_query, execute_update

router = APIRouter()


class RechargeRequest(BaseModel):
    amount: float
    payment_method: str


class RechargeResponse(BaseModel):
    id: str
    amount: float
    payment_method: str
    payment_url: str
    created_at: str


class TransactionInfo(BaseModel):
    id: str
    amount: float
    status: str
    payment_method: str
    external_transaction_id: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

    @staticmethod
    def translate_status(status: str) -> str:
        """将英文状态转换为中文状态"""
        status_map = {
            "pending": "待支付",
            "completed": "已完成",
            "failed": "已失败",
            "cancelled": "已取消"
        }
        return status_map.get(status, status)

    class Config:
        # 用于在序列化时修改status字段的值
        @staticmethod
        def json_schema_extra(schema, model):
            pass

    def dict(self, *args, **kwargs):
        # 调用父类的dict方法获取原始字典
        data = super().dict(*args, **kwargs)
        # 将status字段转换为中文
        data["status"] = self.translate_status(data["status"])
        return data


class WebhookRequest(BaseModel):
    transaction_id: str
    status: str
    external_transaction_id: str


def create_transaction_in_db(user_id: str, amount: float, payment_method: str) -> dict:
    """在数据库中创建交易记录"""
    connection = create_connection()
    if not connection:
        raise Exception("数据库连接失败")
    
    try:
        transaction_id = str(uuid.uuid4())
        query = """
            INSERT INTO transactions 
            (id, user_id, amount, status, payment_method, external_transaction_id, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        created_at = datetime.now().isoformat()
        success = execute_update(connection, query, 
                               (transaction_id, user_id, amount, "pending", payment_method, None, created_at))
        
        if not success:
            raise Exception("创建交易记录失败")
        
        # 查询并返回创建的交易记录
        select_query = """
            SELECT id, user_id, amount, status, payment_method, external_transaction_id, created_at, completed_at 
            FROM transactions 
            WHERE id = %s
        """
        result = execute_query(connection, select_query, (transaction_id,))
        
        if result:
            return result[0]
        else:
            raise Exception("查询创建的交易记录失败")
    finally:
        close_connection(connection)


def get_transactions_by_user_id(user_id: str) -> List[dict]:
    """从数据库查询用户的交易记录"""
    connection = create_connection()
    if not connection:
        return []
    
    try:
        query = """
            SELECT id, amount, status, payment_method, external_transaction_id, created_at, completed_at
            FROM transactions 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        result = execute_query(connection, query, (user_id,))
        
        # 将datetime字段转换为字符串格式
        for transaction in result:
            if transaction['created_at'] and hasattr(transaction['created_at'], 'isoformat'):
                transaction['created_at'] = transaction['created_at'].isoformat()
            if transaction['completed_at'] and hasattr(transaction['completed_at'], 'isoformat'):
                transaction['completed_at'] = transaction['completed_at'].isoformat()
        
        return result
    finally:
        close_connection(connection)


def update_transaction_status(transaction_id: str, status: str, external_transaction_id: str = None) -> bool:
    """更新交易状态"""
    connection = create_connection()
    if not connection:
        return False
    
    try:
        # 如果提供了外部交易号，则使用外部交易号更新交易状态
        if external_transaction_id:
            query = """
                UPDATE transactions 
                SET status = %s, external_transaction_id = %s, completed_at = %s 
                WHERE external_transaction_id = %s
            """
            completed_at = datetime.now().isoformat() if status == "completed" else None
            success = execute_update(connection, query, (status, external_transaction_id, completed_at, external_transaction_id))
        else:
            # 否则使用交易ID更新交易状态
            query = """
                UPDATE transactions 
                SET status = %s, completed_at = %s 
                WHERE id = %s
            """
            completed_at = datetime.now().isoformat() if status == "completed" else None
            success = execute_update(connection, query, (status, completed_at, transaction_id))
        return success
    finally:
        close_connection(connection)


def get_user_balance(user_id: str) -> float:
    """获取用户余额"""
    connection = create_connection()
    if not connection:
        return 0.0
    
    try:
        query = "SELECT balance FROM users WHERE id = %s"
        result = execute_query(connection, query, (user_id,))
        
        if result:
            return float(result[0]['balance'])
        return 0.0
    finally:
        close_connection(connection)


def update_user_balance(user_id: str, amount: float) -> bool:
    """更新用户余额"""
    connection = create_connection()
    if not connection:
        return False
    
    try:
        query = "UPDATE users SET balance = balance + %s WHERE id = %s"
        success = execute_update(connection, query, (amount, user_id))
        return success
    finally:
        close_connection(connection)


from fastapi import Header, HTTPException, Request
from datetime import datetime

# 导入JWT验证函数
from .auth import get_current_user

# 导入微信支付SDK
from wechatpayv3 import WeChatPay, WeChatPayType
import os

# 导入微信支付配置
from config.wxpay_config import MCHID, PRIVATE_KEY_PATH, CERT_SERIAL_NO, APIV3_KEY, APPID, NOTIFY_URL, CERT_DIR

# 初始化微信支付客户端
with open(PRIVATE_KEY_PATH) as f:
    PRIVATE_KEY = f.read()

wxpay = WeChatPay(
    wechatpay_type=WeChatPayType.NATIVE,
    mchid=MCHID,
    private_key=PRIVATE_KEY,
    cert_serial_no=CERT_SERIAL_NO,
    apiv3_key=APIV3_KEY,
    appid=APPID,
    notify_url=NOTIFY_URL,
    cert_dir=CERT_DIR
)

class PaymentGateway:
    @staticmethod
    def create_payment(amount: float, payment_method: str) -> dict:
        # 调用微信支付Native支付接口
        if payment_method == "wechat_pay":
            # 生成商户订单号
            out_trade_no = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"
            
            # 构造支付请求参数
            payment_data = {
                "description": "商品充值",
                "out_trade_no": out_trade_no,
                "amount": {
                    "total": int(amount * 100),  # 转换为分
                    "currency": "CNY"
                },
                "notify_url": NOTIFY_URL
            }
            
            # 调用微信支付统一下单API
            code, result = wxpay.pay(
                description=payment_data["description"],
                out_trade_no=payment_data["out_trade_no"],
                amount=payment_data["amount"],
                notify_url=payment_data["notify_url"]
            )
            
            # 检查返回状态码
            if code in [200, 201]:  # 成功状态码
                # 解析返回结果，提取支付链接
                import json
                result_data = json.loads(result)
                # 返回支付链接
                return {
                    "external_transaction_id": out_trade_no,
                    "payment_url": result_data["code_url"]
                }
            else:
                # 处理错误情况
                raise Exception(f"微信支付接口调用失败，状态码: {code}，错误信息: {result}")
        else:
            # 其他支付方式保持模拟实现
            return {
                "external_transaction_id": f"ext-{uuid.uuid4().hex[:8]}",
                "payment_url": f"https://payment.example.com/pay/{uuid.uuid4()}"
            }


@router.post("/recharge", response_model=RechargeResponse, summary="创建一个充值订单")
async def recharge(request: RechargeRequest, current_user: dict = Depends(get_current_user)):
    """
    创建一个充值订单
    - 请求体：{ "amount": 100, "paymentMethod": "wechat_pay" }
    - 逻辑：在 transactions 表中创建一条 pending 状态的记录。
      与支付网关交互，生成支付链接或二维码信息，并返回给前端。
    """
    # 创建交易记录
    transaction = create_transaction_in_db(current_user["id"], request.amount, request.payment_method)
    
    # 调用支付网关创建支付
    payment_info = PaymentGateway.create_payment(request.amount, request.payment_method)
    
    # 更新交易记录的外部交易号
    transaction["external_transaction_id"] = payment_info["external_transaction_id"]
    
    # 将外部交易号更新到数据库
    connection = create_connection()
    if connection:
        try:
            update_query = "UPDATE transactions SET external_transaction_id = %s WHERE id = %s"
            execute_update(connection, update_query, (payment_info["external_transaction_id"], transaction["id"]))
        finally:
            close_connection(connection)
    
    return RechargeResponse(
        id=transaction["id"],
        amount=transaction["amount"],
        payment_method=transaction["payment_method"],
        payment_url=payment_info["payment_url"],
        created_at=transaction["created_at"].isoformat() if isinstance(transaction["created_at"], datetime) else transaction["created_at"]
    )


@router.get("/history", response_model=List[TransactionInfo], summary="获取用户的账单历史")
async def billing_history(current_user: dict = Depends(get_current_user)):
    """
    获取用户的账单历史
    - 逻辑：查询 transactions 表，返回当前用户的所有交易记录。
    """
    transactions = get_transactions_by_user_id(current_user["id"])
    return [TransactionInfo(**trans) for trans in transactions]


@router.post("/webhook", summary="接收支付网关的回调")
async def payment_webhook(request: Request):
    """
    接收支付网关的回调
    - 逻辑：这是由支付服务商（微信/支付宝）调用的接口，用于通知后端支付已成功。
      后端需要验证回调的合法性，然后更新对应交易的状态为 completed，并增加用户 users 表中的 balance。
    """
    # 验证微信支付回调的合法性
    try:
        result = wxpay.callback(request.headers, await request.body())
        
        if result and result["event_type"] == "TRANSACTION.SUCCESS":
            # 解析回调数据
            resource = result["resource"]
            transaction_id = resource["transaction_id"]
            out_trade_no = resource["out_trade_no"]
            trade_state = resource["trade_state"]
            
            # 如果支付成功，更新用户余额
            if trade_state == "SUCCESS":
                # 获取交易信息
                connection = create_connection()
                if connection:
                    try:
                        # 先检查是否存在状态为'pending'的交易记录
                        check_query = "SELECT user_id, amount FROM transactions WHERE external_transaction_id = %s AND status = 'pending'"
                        result = execute_query(connection, check_query, (out_trade_no,))
                        if result:
                            transaction = result[0]
                            # 更新交易状态
                            success = update_transaction_status(None, "completed", out_trade_no)
                            if not success:
                                raise HTTPException(status_code=404, detail="交易记录不存在")
                            
                            # 更新用户余额
                            update_user_balance(transaction["user_id"], transaction["amount"])
                        else:
                            raise HTTPException(status_code=404, detail="有效的待处理交易记录不存在")
                    finally:
                        close_connection(connection)
                else:
                    raise HTTPException(status_code=500, detail="数据库连接失败")
        
        return {"code": "SUCCESS", "message": "成功"}
    except Exception as e:
        # 记录错误日志
        print(f"处理回调时出错: {e}")
        # 重新抛出异常
        raise e

@router.post("/test-webhook", summary="测试用的回调端点")
async def test_payment_webhook(request: Request):
    """
    测试用的回调端点，用于模拟支付成功的情况
    """
    # 解析回调数据
    data = await request.json()
    transaction_id = data.get("transaction_id")
    out_trade_no = data.get("out_trade_no")
    trade_state = data.get("trade_state", "SUCCESS")
    
    # 如果支付成功，更新用户余额
    if trade_state == "SUCCESS":
        # 获取交易信息
        connection = create_connection()
        if connection:
            try:
                # 先检查是否存在状态为'pending'的交易记录
                check_query = "SELECT user_id, amount FROM transactions WHERE external_transaction_id = %s AND status = 'pending'"
                result = execute_query(connection, check_query, (out_trade_no,))
                if result:
                    transaction = result[0]
                    # 更新交易状态
                    success = update_transaction_status(None, "completed", out_trade_no)
                    if not success:
                        raise HTTPException(status_code=404, detail="交易记录不存在")
                    
                    # 更新用户余额
                    update_user_balance(transaction["user_id"], transaction["amount"])
                    return {"code": "SUCCESS", "message": "用户余额已更新"}
                else:
                    raise HTTPException(status_code=404, detail="有效的待处理交易记录不存在")
            finally:
                close_connection(connection)
        else:
            raise HTTPException(status_code=500, detail="数据库连接失败")
    
    return {"code": "SUCCESS", "message": "成功"}


@router.get("/balance", summary="获取用户余额")
async def get_balance(current_user: dict = Depends(get_current_user)):
    """
    获取用户余额
    - 逻辑：从 users 表中查询当前用户的余额。
    """
    balance = get_user_balance(current_user["id"])
    return {"balance": balance}