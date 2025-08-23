#!/usr/bin/env python3
"""
核心模块测试
"""

import pytest
import tempfile
from pathlib import Path

from aiculture.core import CultureConfig, ProjectTemplate, QualityTools
from aiculture.i18n import _, set_locale, get_current_locale
from aiculture.accessibility_culture import AccessibilityCultureManager


class TestCultureConfig:
    """测试文化配置"""

    def setup_method(self):
        """设置测试"""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        )
        self.temp_file.write("culture:\n  test: true\n")
        self.temp_file.close()
        self.config = CultureConfig(self.temp_file.name)

    def test_config_initialization(self):
        """测试配置初始化"""
        assert self.config.config_path == self.temp_file.name
        assert hasattr(self.config, "config")

    def test_default_config(self):
        """测试默认配置"""
        config = CultureConfig()  # 使用默认路径，会触发默认配置
        assert hasattr(config, "config")
        assert isinstance(config.config, dict)

    def test_config_content(self):
        """测试配置内容"""
        assert isinstance(self.config.config, dict)
        assert "culture" in self.config.config


class TestProjectTemplate:
    """测试项目模板"""

    def setup_method(self):
        """设置测试"""
        self.template = ProjectTemplate()

    def test_template_initialization(self):
        """测试模板初始化"""
        assert hasattr(self.template, "__class__")
        assert self.template.__class__.__name__ == "ProjectTemplate"


class TestQualityTools:
    """测试质量工具"""

    def setup_method(self):
        """设置测试"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.tools = QualityTools(self.temp_dir)

    def test_tools_initialization(self):
        """测试工具初始化"""
        assert hasattr(self.tools, "project_path")
        assert self.tools.project_path == self.temp_dir


class TestI18nFunctionality:
    """测试国际化功能"""

    def test_locale_switching(self):
        """测试语言切换"""
        # 测试中文
        set_locale("zh")
        assert get_current_locale() == "zh"

        # 测试英文
        set_locale("en")
        assert get_current_locale() == "en"

    def test_translation_function(self):
        """测试翻译函数"""
        set_locale("en")
        welcome_msg = _("welcome")
        assert isinstance(welcome_msg, str)
        assert len(welcome_msg) > 0

        # 测试带参数的翻译
        score_msg = _("quality_score", score=85)
        assert isinstance(score_msg, str)
        assert "85" in score_msg

    def test_fallback_behavior(self):
        """测试回退行为"""
        set_locale("nonexistent")
        msg = _("welcome")
        assert isinstance(msg, str)  # 应该返回某种默认值


class TestAccessibilityCulture:
    """测试可访问性文化管理"""

    def setup_method(self):
        """设置测试"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = AccessibilityCultureManager(self.temp_dir)

    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager.project_path == self.temp_dir
        assert hasattr(self.manager, "i18n_checker")
        assert hasattr(self.manager, "accessibility_checker")

    def test_i18n_checker_functionality(self):
        """测试国际化检查器功能"""
        # 创建一个测试文件
        test_file = self.temp_dir / "test.py"
        test_file.write_text('print("Hello, World!")')

        issues = self.manager.i18n_checker.check_file(test_file)
        assert isinstance(issues, list)


class TestCoreIntegration:
    """测试核心模块集成"""

    def test_basic_integration(self):
        """测试基本集成"""
        # 测试配置和模板的基本功能
        config = CultureConfig()
        template = ProjectTemplate()

        assert hasattr(config, "config")
        assert hasattr(template, "__class__")

    def test_i18n_integration(self):
        """测试国际化集成"""
        # 测试语言切换和翻译
        set_locale("en")
        en_msg = _("welcome")

        set_locale("zh")
        zh_msg = _("welcome")

        # 消息应该不同（如果有翻译）或相同（如果没有翻译）
        assert isinstance(en_msg, str)
        assert isinstance(zh_msg, str)


if __name__ == "__main__":
    pytest.main([__file__])
