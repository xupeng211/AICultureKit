"""基本功能测试"""

import pytest

from src.core import Config
from src.models import Content, ContentType, User, UserRole
from src.utils import CryptoUtils, DataValidator, TimeUtils


class TestConfig:
    """配置类测试"""

    def test_config_creation(self):
        """测试配置创建"""
        cfg = Config()
        assert cfg is not None

    def test_config_get_set(self):
        """测试配置读写"""
        cfg = Config()
        cfg.set("test_key", "test_value")
        assert cfg.get("test_key") == "test_value"
        assert cfg.get("non_existent_key", "default") == "default"


class TestModels:
    """数据模型测试"""

    def test_user_creation(self):
        """测试用户模型创建"""
        user = User(id="test_id", username="test_user", email="test@example.com")
        assert user.id == "test_id"
        assert user.username == "test_user"
        assert user.role == UserRole.VIEWER

    def test_user_to_dict(self):
        """测试用户模型转字典"""
        user = User(id="test_id", username="test_user", email="test@example.com")
        user_dict = user.to_dict()
        assert user_dict["id"] == "test_id"
        assert user_dict["username"] == "test_user"
        assert user_dict["role"] == "viewer"

    def test_content_creation(self):
        """测试内容模型创建"""
        content = Content(
            id="content_1",
            title="测试内容",
            content_type=ContentType.TEXT,
            content_data="这是测试内容",
            author_id="user_1",
        )
        assert content.id == "content_1"
        assert content.content_type == ContentType.TEXT


class TestUtils:
    """工具类测试"""

    def test_data_validator_email(self):
        """测试邮箱验证"""
        assert DataValidator.is_valid_email("test@example.com") is True
        assert DataValidator.is_valid_email("invalid_email") is False

    def test_data_validator_url(self):
        """测试URL验证"""
        assert DataValidator.is_valid_url("https://example.com") is True
        assert DataValidator.is_valid_url("invalid_url") is False

    def test_crypto_utils_uuid(self):
        """测试UUID生成"""
        uuid1 = CryptoUtils.generate_uuid()
        uuid2 = CryptoUtils.generate_uuid()
        assert uuid1 != uuid2
        assert len(uuid1) == 36  # UUID4标准长度

    def test_crypto_utils_short_id(self):
        """测试短ID生成"""
        short_id = CryptoUtils.generate_short_id(8)
        assert len(short_id) == 8

    def test_string_utils_truncate(self):
        """测试字符串截断"""
        from src.utils import StringUtils

        text = "这是一个很长的测试字符串"
        truncated = StringUtils.truncate(text, 10)
        assert len(truncated) <= 10

    def test_time_utils_now(self):
        """测试时间工具"""
        now = TimeUtils.now_utc()
        assert now is not None


class TestIntegration:
    """集成测试"""

    def test_basic_workflow(self):
        """测试基本工作流"""
        # 创建用户
        user = User(id="user_1", username="test_user", email="test@example.com")

        # 创建内容
        content = Content(
            id="content_1",
            title="测试内容",
            content_type=ContentType.TEXT,
            content_data="这是一个测试内容",
            author_id=user.id,
        )

        # 验证关联
        assert content.author_id == user.id
        assert isinstance(content.created_at, type(user.created_at))


if __name__ == "__main__":
    pytest.main([__file__])
