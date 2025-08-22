"""
核心功能模块

遵循SOLID原则和AICultureKit开发文化标准
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

import yaml
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 配置管理 (遵循配置外部化原则)
@dataclass
class AppConfig:
    """应用配置类 - 使用环境变量"""

    # 基础配置
    app_name: str = "{{project_name}}"
    version: str = "0.1.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # 数据库配置 (如果需要)
    database_url: Optional[str] = os.getenv("DATABASE_URL")

    # API配置 (如果需要)
    api_host: str = os.getenv("API_HOST", "localhost")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # 安全配置
    secret_key: Optional[str] = os.getenv("SECRET_KEY")

    def __post_init__(self) -> None:
        """验证配置 (遵循安全原则)"""
        if self.environment == "production" and not self.secret_key:
            raise ValueError("生产环境必须设置SECRET_KEY")


# 数据模型 (使用Pydantic进行验证)
class BaseEntity(BaseModel):
    """基础实体类"""

    id: Optional[str] = Field(None, description="唯一标识符")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

    class Config:
        """Pydantic配置"""

        validate_assignment = True
        extra = "forbid"  # 禁止额外字段


class UserData(BaseEntity):
    """用户数据模型"""

    name: str = Field(..., min_length=1, max_length=100, description="用户名")
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$', description="邮箱")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")

    def validate_data(self) -> bool:
        """验证用户数据"""
        return bool(self.name and self.email)


# 存储接口 (遵循依赖倒置原则)
class Repository(Protocol):
    """存储接口"""

    def save(self, entity: BaseEntity) -> bool:
        """保存实体"""
        ...

    def find_by_id(self, entity_id: str) -> Optional[BaseEntity]:
        """根据ID查找实体"""
        ...

    def delete(self, entity_id: str) -> bool:
        """删除实体"""
        ...


# 业务逻辑接口
class BusinessService(ABC):
    """业务服务抽象基类"""

    @abstractmethod
    def process(self, data: Any) -> Any:
        """处理业务逻辑"""


# 具体实现
class FileRepository:
    """文件存储实现"""

    def __init__(self, storage_path: Path) -> None:
        """初始化文件存储

        Args:
            storage_path: 存储路径
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def save(self, entity: BaseEntity) -> bool:
        """保存实体到文件"""
        try:
            if not entity.id:
                import uuid

                entity.id = str(uuid.uuid4())

            file_path = self.storage_path / f"{entity.id}.yaml"

            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(
                    entity.dict(), f, default_flow_style=False, allow_unicode=True
                )

            self.logger.info(f"成功保存实体: {entity.id}")
            return True

        except Exception as e:
            self.logger.error(f"保存实体失败: {e}")
            return False

    def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """根据ID查找实体"""
        try:
            file_path = self.storage_path / f"{entity_id}.yaml"

            if not file_path.exists():
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            return data

        except Exception as e:
            self.logger.error(f"查找实体失败: {e}")
            return None

    def delete(self, entity_id: str) -> bool:
        """删除实体"""
        try:
            file_path = self.storage_path / f"{entity_id}.yaml"

            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"成功删除实体: {entity_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"删除实体失败: {e}")
            return False


class UserService(BusinessService):
    """用户业务服务"""

    def __init__(self, repository: Repository, config: AppConfig) -> None:
        """初始化用户服务

        Args:
            repository: 存储仓库
            config: 应用配置
        """
        self.repository = repository
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def process(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户数据"""
        try:
            # 验证输入数据
            user = UserData(**user_data)

            if not user.validate_data():
                raise ValueError("用户数据验证失败")

            # 保存用户
            success = self.repository.save(user)

            if success:
                self.logger.info(f"成功处理用户: {user.email}")
                return {"success": True, "message": "用户创建成功", "user_id": user.id}
            else:
                raise Exception("保存用户失败")

        except Exception as e:
            self.logger.error(f"处理用户数据失败: {e}")
            return {"success": False, "message": str(e), "user_id": None}

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        try:
            user_data = self.repository.find_by_id(user_id)

            if user_data:
                self.logger.info(f"成功获取用户: {user_id}")
                return user_data
            else:
                self.logger.warning(f"用户不存在: {user_id}")
                return None

        except Exception as e:
            self.logger.error(f"获取用户失败: {e}")
            return None


# 应用程序主类 (遵循单一职责原则)
class Application:
    """应用程序主类"""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        """初始化应用程序"""
        self.config = config or AppConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # 初始化组件
        self._setup_logging()
        self._setup_services()

    def _setup_logging(self) -> None:
        """设置日志"""
        level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        logging.getLogger().setLevel(level)

        self.logger.info(f"应用程序启动: {self.config.app_name} v{self.config.version}")
        self.logger.info(f"运行环境: {self.config.environment}")

    def _setup_services(self) -> None:
        """设置服务"""
        # 创建存储
        storage_path = Path("data") / self.config.environment
        self.repository = FileRepository(storage_path)

        # 创建业务服务
        self.user_service = UserService(self.repository, self.config)

        self.logger.info("服务组件初始化完成")

    def run(self) -> None:
        """运行应用程序"""
        self.logger.info("应用程序开始运行")

        # 应用程序主要逻辑
        # 这里可以添加具体的业务逻辑

        return True

    def shutdown(self) -> None:
        """关闭应用程序"""
        self.logger.info("应用程序正在关闭")
        # 清理资源
        return True


# 工厂函数 (遵循依赖注入原则)
def create_app(config: Optional[AppConfig] = None) -> Application:
    """创建应用程序实例

    Args:
        config: 应用配置

    Returns:
        应用程序实例
    """
    return Application(config)


# 导出的API
__all__ = [
    "AppConfig",
    "BaseEntity",
    "UserData",
    "Repository",
    "BusinessService",
    "FileRepository",
    "UserService",
    "Application",
    "create_app",
]
