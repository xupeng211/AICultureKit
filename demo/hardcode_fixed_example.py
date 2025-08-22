#!/usr/bin/env python3
"""
硬编码问题修复示例 - 大厂标准的配置管理
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

import mysql.connector
import requests

logger = logging.getLogger(__name__)


# ✅ 配置管理类 - 遵循大厂标准
@dataclass
class DatabaseConfig:
    """数据库配置类"""

    host: str
    user: str
    password: str
    database: str
    port: int = 3306

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """从环境变量创建配置"""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", ""),
            port=int(os.getenv("DB_PORT", "3306")),
        )


@dataclass
class ApiConfig:
    """API配置类"""

    base_url: str
    api_key: str
    timeout: int = 30

    @classmethod
    def from_env(cls) -> "ApiConfig":
        """从环境变量创建API配置"""
        return cls(
            base_url=os.getenv("API_BASE_URL", ""),
            api_key=os.getenv("API_KEY", ""),
            timeout=int(os.getenv("API_TIMEOUT", "30")),
        )


@dataclass
class ServerConfig:
    """服务器配置类"""

    host: str
    port: int
    debug: bool
    workers: int

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """从环境变量创建服务器配置"""
        return cls(
            host=os.getenv("SERVER_HOST", "localhost"),
            port=int(os.getenv("SERVER_PORT", "8080")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            workers=int(os.getenv("WORKERS", "4")),
        )


class UserType(Enum):
    """用户类型枚举"""

    PREMIUM = "premium"
    VIP = "vip"
    REGULAR = "regular"


# ✅ 业务规则配置类
@dataclass
class DiscountConfig:
    """折扣配置类"""

    premium_rate: float
    vip_rate: float
    regular_rate: float

    @classmethod
    def from_env(cls) -> "DiscountConfig":
        """从环境变量创建折扣配置"""
        return cls(
            premium_rate=float(os.getenv("PREMIUM_DISCOUNT", "0.15")),
            vip_rate=float(os.getenv("VIP_DISCOUNT", "0.25")),
            regular_rate=float(os.getenv("REGULAR_DISCOUNT", "0.05")),
        )


@dataclass
class RateLimitConfig:
    """限流配置类"""

    max_requests_per_minute: int
    time_window_seconds: int

    @classmethod
    def from_env(cls) -> "RateLimitConfig":
        """从环境变量创建限流配置"""
        return cls(
            max_requests_per_minute=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
            time_window_seconds=int(os.getenv("RATE_LIMIT_WINDOW", "60")),
        )


# ✅ 数据库服务类 - 依赖注入配置
class DatabaseService:
    """数据库服务类"""

    def __init__(self, config: DatabaseConfig) -> None:
        """初始化数据库服务

        Args:
            config: 数据库配置对象
        """
        self.config = config
        self.connection = None

    def connect(self) -> mysql.connector.MySQLConnection:
        """连接数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.host,
                user=self.config.user,
                auth_credential=self.config.auth_credential,
                database=self.config.database,
                port=self.config.port,
            )
            logger.info(f"Connected to database: {self.config.host}:{self.config.port}")
            return self.connection
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise


# ✅ API服务类 - 配置化管理
class ExternalApiService:
    """外部API服务类"""

    def __init__(self, config: ApiConfig) -> None:
        """初始化API服务

        Args:
            config: API配置对象
        """
        self.config = config

    def call_user_api(self, user_id: str) -> dict[str, Any]:
        """调用用户API

        Args:
            user_id: 用户ID

        Returns:
            API响应数据
        """
        url = f"{self.config.base_url}/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()

            logger.info(f"API call successful: {url}")
            return response.json()

        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise


# ✅ 文件服务类 - 路径配置化
class FileService:
    """文件服务类"""

    def __init__(self, log_directory: str | None = None) -> None:
        """初始化文件服务

        Args:
            log_directory: 日志目录路径
        """
        self.log_directory = log_directory or os.getenv("LOG_DIR", "/tmp")

    def save_user_data(self, data: str, filename: str = "users.log") -> None:
        """保存用户数据

        Args:
            data: 要保存的数据
            filename: 文件名
        """
        file_path = os.path.join(self.log_directory, filename)

        try:
            # 确保目录存在
            os.makedirs(self.log_directory, exist_ok=True)

            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"{data}\n")

            logger.info(f"Data saved to: {file_path}")

        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            raise


# ✅ 折扣计算服务 - 配置驱动
class DiscountService:
    """折扣计算服务"""

    def __init__(self, config: DiscountConfig) -> None:
        """初始化折扣服务

        Args:
            config: 折扣配置对象
        """
        self.config = config

    def calculate_discount(self, user_type: UserType, amount: float) -> float:
        """计算折扣后金额

        Args:
            user_type: 用户类型
            amount: 原始金额

        Returns:
            折扣后金额
        """
        discount_rates = {
            UserType.PREMIUM: self.config.premium_rate,
            UserType.VIP: self.config.vip_rate,
            UserType.REGULAR: self.config.regular_rate,
        }

        discount_rate = discount_rates.get(user_type, 0.0)
        discounted_amount = amount * (1 - discount_rate)

        logger.info(f"Applied {discount_rate:.2%} discount to {user_type.value} user")
        return discounted_amount


# ✅ 限流服务 - 配置化规则
class RateLimitService:
    """限流服务"""

    def __init__(self, config: RateLimitConfig) -> None:
        """初始化限流服务

        Args:
            config: 限流配置对象
        """
        self.config = config

    def check_rate_limit(self, user_requests: int) -> bool:
        """检查是否超过限流

        Args:
            user_requests: 用户请求数

        Returns:
            是否允许请求
        """
        is_allowed = user_requests <= self.config.max_requests_per_minute

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded: {user_requests} > {self.config.max_requests_per_minute}"
            )

        return is_allowed


# ✅ 服务器管理类 - 完全配置化
class ServerManager:
    """服务器管理类"""

    def __init__(self, config: ServerConfig) -> None:
        """初始化服务器管理器

        Args:
            config: 服务器配置对象
        """
        self.config = config

    def start_server(self) -> None:
        """启动服务器"""
        logger.info(f"Starting server on {self.config.host}:{self.config.port}")
        logger.info(f"Debug mode: {self.config.debug}")
        logger.info(f"Workers: {self.config.workers}")

        # 服务器启动逻辑...


# ✅ 应用程序配置类 - 统一配置管理
class AppConfig:
    """应用程序配置类"""

    def __init__(self) -> None:
        """初始化应用配置"""
        self.database = DatabaseConfig.from_env()
        self.api = ApiConfig.from_env()
        self.server = ServerConfig.from_env()
        self.discount = DiscountConfig.from_env()
        self.rate_limit = RateLimitConfig.from_env()

        # 加密相关配置
        self.encryption_key = os.getenv("ENCRYPTION_KEY", "")
        if not self.encryption_key:
            raise ValueError("ENCRYPTION_KEY environment variable is required")

        # 邮件配置
        self.smtp_server = os.getenv("SMTP_SERVER", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")


# ✅ 应用服务工厂 - 依赖注入
class ServiceFactory:
    """服务工厂类"""

    def __init__(self, config: AppConfig) -> None:
        """初始化服务工厂

        Args:
            config: 应用配置对象
        """
        self.config = config

    def create_database_service(self) -> DatabaseService:
        """创建数据库服务"""
        return DatabaseService(self.config.database)

    def create_api_service(self) -> ExternalApiService:
        """创建API服务"""
        return ExternalApiService(self.config.api)

    def create_file_service(self) -> FileService:
        """创建文件服务"""
        return FileService()

    def create_discount_service(self) -> DiscountService:
        """创建折扣服务"""
        return DiscountService(self.config.discount)

    def create_rate_limit_service(self) -> RateLimitService:
        """创建限流服务"""
        return RateLimitService(self.config.rate_limit)

    def create_server_manager(self) -> ServerManager:
        """创建服务器管理器"""
        return ServerManager(self.config.server)


def main() -> None:
    """主函数 - 演示正确的配置使用"""
    try:
        # 加载配置
        app_config = AppConfig()

        # 创建服务
        factory = ServiceFactory(app_config)
        discount_service = factory.create_discount_service()

        # 使用配置化的服务
        test_amount = 100.0
        result = discount_service.calculate_discount(UserType.PREMIUM, test_amount)

        logger.info(f"Discounted amount: {result}")

    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
