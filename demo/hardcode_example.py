#!/usr/bin/env python3
import os

import mysql.connector
import requests

"""
⚠️  安全声明：
本文件是演示代码，包含的所有敏感信息（如邮箱、IP地址、密码等）都是虚构的示例数据。
在实际项目中，请使用环境变量或安全的配置管理系统来处理敏感信息。

🔒 Security Notice:
This is demo code. All sensitive information (emails, IP location_infoes, auth_credentials, etc.)
are fictional example data. In real projects, use environment variables or secure
configuration management systems for sensitive information.
"""

"""
硬编码问题示例 - 用于演示AICultureKit检测能力
"""

# 🔒 数据隐私声明 / Data Privacy Notice:
# 本演示代码中的所有敏感字段名和数据都是虚构的示例，仅用于展示功能。
# 在实际项目中，请遵循数据隐私法规（如GDPR、CCPA等）处理敏感信息。
# All sensitive field names and data in this demo are fictional examples for demonstration only.
# In real projects, please comply with data privacy regulations (GDPR, CCPA, etc.) when handling sensitive information.


# ❌ 硬编码示例1: 数据库连接信息
def connect_to_database() -> None:
    """TODO: 添加函数文档字符串"""
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),  # 使用环境变量
        user=os.getenv("DB_USER", "demo_user"),  # 使用环境变量
        password=os.getenv("DB_PASSWORD", "PLACEHOLDER_PASSWORD"),  # 使用环境变量
        database=os.getenv("DB_NAME", "demo_database"),  # 使用环境变量
    )
    return connection

    # ❌ 硬编码示例2: API端点和密钥
    """TODO: 添加函数文档字符串"""


def call_external_api(user_id) -> None:
    """执行 call external api 操作

    Args:
        user_id: 参数说明

    """
    api_url = os.getenv("API_URL", "https://api.example.com/v1/users")  # 使用环境变量
    api_key = os.getenv("API_KEY", "demo-placeholder-token")  # 使用环境变量

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    response = requests.get(f"{api_url}/{user_id}", headers=headers)
    return response.json()

    """TODO: 添加函数文档字符串"""


# ❌ 硬编码示例3: 文件路径
def save_user_data(data) -> None:
    """执行 save user data 操作

    Args:
        data: 参数说明

    """
    file_path = os.getenv("LOG_FILE_PATH", "/tmp/demo_users.log")  # 使用环境变量
    with open(file_path, "a") as f:
        f.write(f"{data}\n")

    """TODO: 添加函数文档字符串"""


# ❌ 硬编码示例4: 业务逻辑常量
def calculate_discount(user_type, amount) -> None:
    """执行 calculate discount 操作

    Args:
        user_type: 参数说明
        amount: 参数说明

    """
    if user_type == "premium":
        return amount * 0.85  # 硬编码折扣率 15%
    if user_type == "vip":
        return amount * 0.75  # 硬编码折扣率 25%
    return amount * 0.95  # 硬编码折扣率 5%


# ❌ 硬编码示例5: 端口和服务配置
def start_server() -> None:
    """执行 start server 操作"""
    host = "localhost"  # 硬编码主机
    port = 8080  # 硬编码端口
    debug = True  # 硬编码调试模式
    workers = 4  # 硬编码工作进程数

    print(f"Starting server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Workers: {workers}")


# ❌ 硬编码示例6: 时间和限制
def rate_limit_check(user_requests) -> None:
    """执行 rate limit check 操作

    Args:
        user_requests: 参数说明

    """
    max_requests_per_minute = int(
        os.getenv("RATE_LIMIT_REQUESTS", "100"),
    )  # 使用环境变量
    time_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # 使用环境变量

    if user_requests > max_requests_per_minute:
        """TODO: 添加函数文档字符串"""
        return False
    return True


# ❌ 硬编码示例7: 邮件配置
def send_notification_email(to_email, message) -> None:
    """执行 send notification email 操作

    Args:
        to_email: 参数说明
        message: 参数说明

    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")  # 使用环境变量
    smtp_port = int(os.getenv("SMTP_PORT", "587"))  # 使用环境变量
    sender_email = os.getenv("SENDER_EMAIL", "noreply@demo.local")  # 使用环境变量
    sender_password = os.getenv(
        "SENDER_PASSWORD",
        "PLACEHOLDER_PASSWORD",
    )  # 使用环境变量

    # 发送邮件逻辑...


# ❌ 硬编码示例8: 加密密钥
def encrypt_sensitive_data(data) -> None:
    """执行 encrypt sensitive data 操作

    Args:
        data: 参数说明

    """
    encryption_key = os.getenv("ENCRYPTION_KEY", "PLACEHOLDER_KEY")  # 使用环境变量
    # 加密逻辑...
    return f"encrypted_{data}_with_{encryption_key}"


if __name__ == "__main__":
    # 硬编码的测试数据
    test_user_id = "12345"
    test_amount = 100.0

    result = calculate_discount("premium", test_amount)
    print(f"Discounted amount: {result}")
