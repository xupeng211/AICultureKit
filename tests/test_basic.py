"""基本功能测试 - 验证核心模块的基础功能和数据模型的正确性"""

import pytest

from src.core import Config
from src.models import AnalysisResult, Content, ContentType, User, UserProfile, UserRole
from src.utils import CryptoUtils, DataValidator, TimeUtils


class TestConfig:
    """配置类测试 - 验证配置管理的基础功能和数据持久化"""

    def test_config_creation(self):
        """测试配置创建 - 确保Config类能正常实例化并初始化内部状态"""
        cfg = Config()
        assert cfg is not None

    def test_config_get_set(self):
        """测试配置读写 - 验证配置项的设置、获取和默认值处理机制"""
        cfg = Config()
        # 测试设置和获取配置项的基本功能
        cfg.set("test_key", "test_value")
        assert cfg.get("test_key") == "test_value"
        # 测试默认值机制，确保未设置的配置项返回正确的默认值
        assert cfg.get("non_existent_key", "default") == "default"


class TestModels:
    """数据模型测试 - 验证业务数据模型的创建、序列化和类型安全性"""

    def test_user_creation(self):
        """测试用户模型创建 - 验证User模型的实例化和默认值设置"""
        user = User(id="test_id", username="test_user", email="test@example.com")
        assert user.id == "test_id"
        assert user.username == "test_user"
        # 验证默认角色设置，确保用户权限控制的安全性
        assert user.role == UserRole.VIEWER

    def test_user_to_dict(self):
        """测试用户模型转字典 - 验证数据序列化功能，确保API接口数据格式正确"""
        user = User(id="test_id", username="test_user", email="test@example.com")
        user_dict = user.to_dict()
        assert user_dict["id"] == "test_id"
        assert user_dict["username"] == "test_user"
        # 验证枚举值的正确序列化，确保前端能正确解析用户角色
        assert user_dict["role"] == "viewer"

    def test_content_creation(self):
        """测试内容模型创建 - 验证Content模型的实例化和内容类型处理"""
        content = Content(
            id="content_1",
            title="测试内容",
            content_type=ContentType.TEXT,
            content_data="这是测试内容",
            author_id="user_1",
        )
        assert content.id == "content_1"
        assert content.content_type == ContentType.TEXT

    def test_content_to_dict(self):
        """测试内容模型转字典 - 验证数据序列化功能"""
        content = Content(
            id="content_1",
            title="测试内容",
            content_type=ContentType.TEXT,
            content_data="这是测试内容",
            author_id="user_1",
        )
        content_dict = content.to_dict()
        assert content_dict["id"] == "content_1"
        assert content_dict["title"] == "测试内容"
        assert content_dict["content_type"] == "text"
        assert "created_at" in content_dict

    def test_analysis_result_to_dict(self):
        """测试分析结果模型转字典 - 验证数据序列化功能"""
        result = AnalysisResult(
            id="analysis_1",
            content_id="content_1",
            analysis_type="sentiment",
            result_data={"score": 0.9},
            confidence_score=0.95,  # 添加缺失的必填字段
        )
        result_dict = result.to_dict()
        assert result_dict["id"] == "analysis_1"
        assert result_dict["analysis_type"] == "sentiment"
        assert result_dict["result_data"]["score"] == 0.9
        assert result_dict["confidence_score"] == 0.95

    def test_user_profile_to_dict(self):
        """测试用户画像模型转字典 - 验证数据序列化功能"""
        profile = UserProfile(
            user_id="user_1",  # 移除不支持的'id'字段
            interests=["AI", "Culture"],
        )
        profile_dict = profile.to_dict()
        assert profile_dict["user_id"] == "user_1"  # 修正断言
        assert "AI" in profile_dict["interests"]


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
