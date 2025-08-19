# zz3d 数据库表结构说明

本文档详细说明了 zz3d 项目的数据库表结构，供后端接口开发者参考。

## 1. users 表（用户表）

存储所有用户的基础信息。

### 表结构

| 字段名 | 数据类型 | 约束 | 描述 |
| --- | --- | --- | --- |
| id | VARCHAR(36) | PRIMARY KEY | 唯一标识符（UUID） |
| phone_number | VARCHAR(20) | UNIQUE, NOT NULL | 用户的手机号，用于登录 |
| real_name | VARBINARY(255) | NOT NULL | 用户的真实姓名（加密存储） |
| id_number | VARBINARY(255) | NOT NULL | 用户的身份证号（加密存储） |
| balance | DECIMAL(10, 2) | NOT NULL, DEFAULT 0.00 | 用户账户余额 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 用户账户创建时间 |

### 索引

- `idx_phone_number`：在 `phone_number` 字段上建立的索引，用于快速查找用户。

### 安全说明

- `real_name` 和 `id_number` 字段为敏感数据，在数据库中以加密形式存储。
- `balance` 字段使用 DECIMAL(10, 2) 类型以精确表示货币金额。

## 2. api_keys 表（API密钥表）

管理用户创建的API密钥。

### 表结构

| 字段名 | 数据类型 | 约束 | 描述 |
| --- | --- | --- | --- |
| id | VARCHAR(36) | PRIMARY KEY | 唯一标识符 |
| user_id | VARCHAR(36) | NOT NULL, FOREIGN KEY | 外键，关联到 users 表的 id |
| name | VARCHAR(100) | NOT NULL | 用户为密钥设置的名称 |
| key_hash | VARCHAR(64) | NOT NULL | API密钥的哈希值（SHA-256） |
| key_prefix | VARCHAR(20) | NOT NULL | 密钥的前几位字符 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 密钥创建时间 |
| last_used_at | TIMESTAMP | NULL | 密钥最后一次使用的时间 |

### 安全说明

- 永远不要在数据库中明文存储API密钥。
- `key_hash` 字段存储密钥的SHA-256哈希值。
- `key_prefix` 字段存储密钥的前缀，用于在界面上安全地展示给用户。

## 3. transactions 表（交易表）

记录所有的充值和账单信息。

### 表结构

| 字段名 | 数据类型 | 约束 | 描述 |
| --- | --- | --- | --- |
| id | VARCHAR(36) | PRIMARY KEY | 唯一标识符 |
| user_id | VARCHAR(36) | NOT NULL, FOREIGN KEY | 外键，关联到 users 表的 id |
| amount | DECIMAL(10, 2) | NOT NULL | 交易金额 |
| status | ENUM('pending', 'completed', 'failed') | NOT NULL | 交易状态 |
| payment_method | ENUM('wechat_pay', 'alipay') | NOT NULL | 支付方式 |
| external_transaction_id | VARCHAR(100) | - | 支付网关返回的外部交易号 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 交易创建时间 |
| completed_at | TIMESTAMP | NULL | 交易完成时间 |

### 状态说明

- `pending`：待支付
- `completed`：已完成
- `failed`：失败

### 支付方式说明

- `wechat_pay`：微信支付
- `alipay`：支付宝

## 4. usage_records 表（使用记录表）

记录每一次API的调用和费用。

### 表结构

| 字段名 | 数据类型 | 约束 | 描述 |
| --- | --- | --- | --- |
| id | VARCHAR(36) | PRIMARY KEY | 唯一标识符 |
| user_id | VARCHAR(36) | NOT NULL, FOREIGN KEY | 外键，关联到 users 表的 id |
| api_key_id | VARCHAR(36) | NOT NULL, FOREIGN KEY | 外键，关联到 api_keys 表的 id |
| service_name | VARCHAR(100) | NOT NULL | 调用的服务名称 |
| cost | DECIMAL(10, 2) | NOT NULL | 本次调用产生的费用 |
| timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 调用发生的时间 |

### 说明

- 每次API调用都会在此表中创建一条记录。
- `cost` 字段表示本次调用产生的费用，会从用户余额中扣除。