# zz3d 项目

这个项目包含两个部分：
1. 一个Python脚本，用于连接MySQL数据库并创建所需的表结构
2. 一个FastAPI后端服务，提供RESTful API接口

## 项目结构

### 数据库初始化部分
- `db_create.py`: 数据库初始化脚本，包含数据库连接和表创建逻辑
- `requirements.txt`: 项目依赖文件

### FastAPI后端服务部分
- `apis/main.py`: FastAPI应用入口文件
- `apis/auth.py`: 认证相关接口
- `apis/user.py`: 用户相关接口
- `apis/keys.py`: API密钥相关接口
- `apis/billing.py`: 计费和账单相关接口
- `apis/usage.py`: 用量统计相关接口

## 安装依赖

在运行脚本之前，请确保安装了所需的依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 数据库初始化

1. 修改 `db_create.py` 文件中的数据库连接信息（主机名、用户名、密码）
2. 运行脚本：

```bash
python db_create.py
```

### 配置数据库连接

API服务需要访问数据库来存储和检索数据。数据库连接信息在 `apis/database.py` 文件中配置。
请根据实际情况修改以下参数：

- `host`: 数据库主机名
- `user`: 数据库用户名
- `password`: 数据库密码
- `database`: 数据库名称

### 启动FastAPI服务

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 启动服务：

```bash
uvicorn apis.main:app --reload
```

3. 访问API文档：

打开浏览器访问 http://localhost:8000/docs 查看API文档和测试接口。

数据库初始化脚本将自动创建名为 `zz3d` 的数据库以及以下四张表：

1. `users`: 存储用户基础信息
2. `api_keys`: 管理用户API密钥
3. `transactions`: 记录充值和账单信息
4. `usage_records`: 记录API调用和费用

## 数据库设计说明

### users 表
- `id`: 唯一标识符（UUID），主键
- `phone_number`: 用户手机号，唯一且建立索引
- `real_name`: 用户真实姓名（加密存储）
- `id_number`: 身份证号（加密存储）
- `balance`: 账户余额（DECIMAL类型）
- `created_at`: 账户创建时间

### api_keys 表
- `id`: 唯一标识符，主键
- `user_id`: 外键，关联到users表
- `name`: 密钥名称
- `key_hash`: API密钥的哈希值
- `key_prefix`: 密钥前缀（明文存储）
- `created_at`: 密钥创建时间
- `last_used_at`: 密钥最后使用时间

### transactions 表
- `id`: 唯一标识符，主键
- `user_id`: 外键，关联到users表
- `amount`: 交易金额
- `status`: 交易状态（pending/completed/failed）
- `payment_method`: 支付方式（wechat_pay/alipay）
- `external_transaction_id`: 外部交易号
- `created_at`: 交易创建时间
- `completed_at`: 交易完成时间

### usage_records 表
- `id`: 唯一标识符，主键
- `user_id`: 外键，关联到users表
- `api_key_id`: 外键，关联到api_keys表
- `service_name`: 调用的服务名称
- `cost`: 调用费用
- `timestamp`: 调用时间