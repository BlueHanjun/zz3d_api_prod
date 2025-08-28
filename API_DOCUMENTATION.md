# zz3d API 接口文档

本文档为前端开发者提供了详细的API接口说明，包括接口地址、请求方法、参数说明、返回示例等，以便进行接口对接。

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: JWT Token，在请求头中添加 `Authorization: Bearer {token}`

## 接口列表

### 认证相关接口

#### 1. 发送登录验证码

- **接口地址**: `/auth/send-code`
- **请求方法**: `POST`
- **请求参数**:

```json
{
  "phone_number": "18612345678"  // 用户手机号
}
```

- **成功响应**:

```json
{
  "message": "验证码已发送"
}
```

- **说明**: 系统会生成一个6位数的验证码，将其存储到Redis中（5分钟过期），并通过短信服务发送到指定的手机号码。短信内容格式为"您的验证码是：123456【微网通联】"。

#### 2. 用户登录

- **接口地址**: `/auth/login`
- **请求方法**: `POST`
- **请求参数**:

```json
{
  "phone_number": "18612345678",  // 用户手机号
  "code": "123456"              // 验证码
}
```

- **成功响应**:

```json
{
  "token": "fake-jwt-token-for-18612345678"  // JWT令牌
}
```

#### 3. 用户登出

- **接口地址**: `/auth/logout`
- **请求方法**: `POST`
- **请求头**: 需要携带JWT令牌
- **成功响应**:

```json
{
  "message": "登出成功"
}
```

### 用户相关接口

#### 1. 获取当前登录用户的信息

- **接口地址**: `/user/me`
- **请求方法**: `GET`
- **请求头**: 需要携带JWT令牌
- **成功响应**:

```json
{
  "id": "user-123",
  "phone_number": "18612345678",
  "real_name": null,
  "id_number": null,
  "balance": 0.0,
  "created_at": "2023-01-01T00:00:00"
}
```

### API密钥相关接口

#### 1. 获取当前用户的所有API密钥

- **接口地址**: `/keys/`
- **请求方法**: `GET`
- **请求头**: 需要携带JWT令牌
- **成功响应**:

```json
[
  {
    "id": "key-123",
    "name": "我的密钥",
    "key_prefix": "zz-abcde",
    "created_at": "2023-01-01T00:00:00",
    "last_used_at": null
  }
]
```

#### 2. 创建一个新的API密钥

- **接口地址**: `/keys/`
- **请求方法**: `POST`
- **请求头**: 需要携带JWT令牌
- **请求参数**:

```json
{
  "name": "我的新密钥"  // 密钥名称
}
```

- **成功响应**:

```json
{
  "id": "key-456",
  "name": "我的新密钥",
  "key": "zz-abcdefghijk1234567890",  // 完整的API密钥（仅此一次显示）
  "key_prefix": "zz-abcde",
  "created_at": "2023-01-01T00:00:00"
}
```

#### 3. 删除一个API密钥

- **接口地址**: `/keys/{key_id}`
- **请求方法**: `DELETE`
- **请求头**: 需要携带JWT令牌
- **路径参数**: `key_id` - 要删除的密钥ID
- **成功响应**:

```json
{
  "message": "API密钥删除成功"
}
```

### 计费和账单相关接口

#### 1. 创建一个充值订单

- **接口地址**: `/billing/recharge`
- **请求方法**: `POST`
- **请求头**: 需要携带JWT令牌
- **请求参数**:

```json
{
  "amount": 100.00,       // 充值金额
  "payment_method": "wechat_pay"  // 支付方式（目前仅支持 wechat_pay）
}
```

- **成功响应**:

```json
{
  "id": "trans-123",
  "amount": 100.00,
  "payment_method": "wechat_pay",
  "payment_url": "weixin://wxpay/bizpayurl?pr=xxxxxx",  // 微信支付链接
  "created_at": "2023-01-01T00:00:00"
}
```

#### 2. 获取用户的账单历史

- **接口地址**: `/billing/history`
- **请求方法**: `GET`
- **请求头**: 需要携带JWT令牌
- **成功响应**:

```json
[
  {
    "id": "trans-123",
    "amount": 100.00,
    "status": "completed",
    "payment_method": "wechat_pay",
    "external_transaction_id": "ext-abc12345",
    "created_at": "2023-01-01T00:00:00",
    "completed_at": "2023-01-01T00:05:00"
  }
]
```

#### 3. 接收支付网关的回调

- **接口地址**: `/billing/webhook`
- **请求方法**: `POST`
- **说明**: 此接口由微信支付服务商调用，用于通知支付结果
- **注意**: 此接口不接收JSON参数，而是接收微信支付服务器发送的加密数据

- **成功响应**:

```json
{
  "code": "SUCCESS",
  "message": "成功"
}
```

#### 4. 获取用户余额

- **接口地址**: `/billing/balance`
- **请求方法**: `GET`
- **请求头**: 需要携带JWT令牌
- **成功响应**:

```json
{
  "balance": 100.00
}
```

### 用量统计相关接口

#### 1. 获取用量统计数据

- **接口地址**: `/usage/summary`
- **请求方法**: `GET`
- **请求头**: 需要携带JWT令牌
- **请求参数**:
  - `period`: 统计周期（daily/weekly/monthly，默认monthly）
  - `date`: 日期（格式: YYYY-MM 或 YYYY-MM-DD，默认2023-01）
- **成功响应**:

```json
{
  "period": "monthly",
  "date": "2023-01",
  "records": [
    {
      "date": "2023-01-01",
      "service_name": "空间灯具点位智能生成",
      "count": 10,
      "total_cost": 50.00
    }
  ]
}
```

### 开放API接口

#### 1. 模拟OpenAPI调用

- **接口地址**: `/openapi/simulate`
- **请求方法**: `GET`
- **请求头**: 需要携带API密钥 `X-API-Key: {your-api-key}`
- **成功响应**:

```json
{
  "message": "调用成功，扣费0.1元。"
}
```

- **说明**: 此接口用于模拟外部OpenAPI调用，需要提供有效的API密钥进行认证。每次成功调用会扣除0.1元费用。
- **安全说明**: API密钥验证采用SHA-256哈希算法，直接使用完整密钥的哈希值进行查询验证，确保了高安全性，避免了前缀碰撞的风险。