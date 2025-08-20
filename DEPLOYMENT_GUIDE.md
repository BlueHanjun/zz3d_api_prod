# zz3d 项目部署指南

本文档详细说明了如何将 zz3d 项目部署到阿里云ECS服务器上。

## 1. 环境准备

### 1.1 服务器要求

- 操作系统：Linux (推荐 Ubuntu 18.04/20.04 或 CentOS 7/8)
- 内存：至少 2GB
- 存储：至少 20GB 可用磁盘空间
- Python 版本：3.8 或更高版本

### 1.2 依赖服务

- MySQL 8.0
- Redis 5.0 或更高版本

## 2. 部署步骤

### 2.1 连接到ECS服务器

使用SSH连接到您的ECS服务器：

```bash
ssh root@your_server_ip
```

### 2.2 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip mysql-server redis-server git nginx

# CentOS/RHEL
sudo yum update
sudo yum install -y python3 python3-pip mysql-server redis git nginx
```

### 2.3 获取项目代码

```bash
git clone https://github.com/BlueHanjun/zz3d_api_prod.git
cd zz3d_api_prod
```

### 2.4 安装Python依赖

```bash
pip3 install -r requirements.txt
```

根据项目中的requirements.txt，需要安装的依赖包括：
- mysql-connector-python==8.0.33
- fastapi==0.68.0
- uvicorn==0.15.0
- python-jose==3.3.0
- passlib==1.7.4
- redis==4.5.4
- requests==2.31.0

### 2.5 配置数据库

#### 2.5.1 启动MySQL服务

```bash
# Ubuntu/Debian
sudo systemctl start mysql
sudo systemctl enable mysql

# CentOS/RHEL
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

#### 2.5.2 配置MySQL

1. 登录MySQL：

```bash
mysql -u root -p
```

2. 创建数据库：

```sql
CREATE DATABASE zz3d;
```

3. 创建用户并授权：

```sql
CREATE USER 'zz3d_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON zz3d.* TO 'zz3d_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 2.5.3 初始化数据库表

修改 `db/database.py` 文件中的数据库连接信息（主机名、用户名、密码），然后运行：

```bash
python3 db_create.py
```

### 2.6 配置Redis

#### 2.6.1 启动Redis服务

```bash
sudo systemctl start redis
sudo systemctl enable redis
```

#### 2.6.2 配置Redis密码（可选但推荐）

1. 编辑Redis配置文件：

```bash
sudo nano /etc/redis/redis.conf
```

2. 找到 `# requirepass foobared` 行，取消注释并设置密码：

```
requirepass your_redis_password
```

3. 重启Redis服务：

```bash
sudo systemctl restart redis
```

### 2.7 配置项目环境

#### 2.7.1 配置数据库连接

修改 `db/database.py` 文件中的数据库连接信息：

```python
connection = mysql.connector.connect(
    host='localhost',  # 如果MySQL在同一服务器上
    port='3306',
    user='zz3d_user',
    password='your_strong_password',
    database='zz3d'
)
```

#### 2.7.2 配置Redis连接

修改 `db/redis_utils.py` 文件中的Redis连接信息：

```python
# Redis连接配置
REDIS_HOST = 'localhost'  # 如果Redis在同一服务器上
REDIS_PORT = 6379
REDIS_PASSWORD = 'your_redis_password'  # 如果设置了密码
REDIS_DB = 0
```

#### 2.7.3 配置短信服务

修改 `external/real_account_info.py` 文件中的短信服务账户信息：

```python
REAL_ACCOUNT_ID = "your_account_id"
REAL_PASSWORD = "your_password"
REAL_SMS_ENCRYPT_KEY = "your_encrypt_key"
REAL_PRODUCT_ID = your_product_id
REAL_EXTEND_NO = "your_extend_no"  # 可选
```

### 2.8 启动应用程序

#### 2.8.1 直接运行

```bash
uvicorn apis.main:app --host 0.0.0.0 --port 8001
```

或者直接运行main.py（需要设置PYTHONPATH）：

```bash
# 在项目根目录下执行
export PYTHONPATH=/path/to/your/project
python3 apis/main.py

# 或者直接在命令行中设置
PYTHONPATH=/path/to/your/project python3 apis/main.py
```

#### 2.8.2 使用Systemd设置后台运行

1. 创建service文件：

```bash
sudo nano /etc/systemd/system/zz3d-api.service
```

2. 添加以下内容：

```ini
[Unit]
Description=zz3d API Service
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/your/project
Environment=PYTHONPATH=/path/to/your/project
ExecStart=/usr/local/bin/uvicorn apis.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

3. 启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable zz3d-api
sudo systemctl start zz3d-api
```

### 2.9 配置Nginx反向代理（可选）

1. 创建Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/zz3d-api
```

2. 添加以下内容：

```nginx
server {
    listen 80;
    server_name your_domain.com;  # 替换为您的域名

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

3. 创建软链接：

```bash
sudo ln -s /etc/nginx/sites-available/zz3d-api /etc/nginx/sites-enabled/
```

4. 测试配置并重启Nginx：

```bash
sudo nginx -t
sudo systemctl restart nginx
```

## 3. 安全建议

1. 使用防火墙限制对服务器的访问
2. 为MySQL和Redis设置强密码
3. 使用HTTPS保护数据传输
4. 定期更新系统和软件包
5. 定期备份数据库

## 4. 故障排除

### 4.1 查看服务状态

```bash
sudo systemctl status zz3d-api
```

### 4.2 查看服务日志

```bash
sudo journalctl -u zz3d-api -f
```

### 4.3 检查端口监听

```bash
netstat -tlnp | grep :8001
```

### 4.4 模块导入问题

如果遇到 `ModuleNotFoundError: No module named 'apis'` 错误，请确保正确设置了 `PYTHONPATH` 环境变量：

```bash
# 临时设置PYTHONPATH
export PYTHONPATH=/path/to/your/project

# 或者在运行命令时直接设置
PYTHONPATH=/path/to/your/project python3 apis/main.py
```

此外，请确保 `apis` 和 `openapis` 目录下都包含 `__init__.py` 文件。

通过遵循以上步骤，您应该能够成功将zz3d项目部署到阿里云ECS服务器上。