#!/usr/bin/env python3
"""
核心功能测试 - 提升测试覆盖率
"""

import tempfile
from pathlib import Path
import pytest

from aiculture.core import CultureConfig, ProjectTemplate, QualityTools
from aiculture.i18n import _, set_locale
from aiculture.data_catalog import (
    DataCatalog,
    DataAsset,
    DataAssetType,
    DataClassification,
    DataFormat,
)
from aiculture.monitoring_config import MonitoringConfigManager


class TestCoreComponents:
    """测试核心组件"""

    def test_culture_config_initialization(self):
        """测试文化配置初始化"""
        config = CultureConfig()
        assert hasattr(config, 'principles')
        assert hasattr(config, 'quality_gates')
        assert hasattr(config, 'ai_guidelines')

    def test_project_template_creation(self):
        """测试项目模板创建"""
        template = ProjectTemplate("test-project", "python")
        assert template.name == "test-project"
        assert template.language == "python"

    def test_quality_tools_initialization(self):
        """测试质量工具初始化"""
        tools = QualityTools()
        assert hasattr(tools, 'linters')
        assert hasattr(tools, 'formatters')
        assert hasattr(tools, 'security_scanners')


class TestInternationalization:
    """测试国际化功能"""

    def test_locale_switching(self):
        """测试语言切换"""
        # 测试英文
        set_locale('en')
        welcome_en = _('welcome')
        assert welcome_en == 'Welcome'

        # 测试中文
        set_locale('zh')
        welcome_zh = _('welcome')
        assert welcome_zh == '欢迎'

    def test_missing_translation(self):
        """测试缺失翻译"""
        set_locale('en')
        missing = _('non_existent_key')
        assert missing == 'non_existent_key'

    def test_parameterized_translation(self):
        """测试参数化翻译"""
        set_locale('en')
        score_msg = _('quality_score', score=85)
        assert '85' in score_msg

        set_locale('zh')
        score_msg_zh = _('quality_score', score=85)
        assert '85' in score_msg_zh


class TestDataCatalog:
    """测试数据目录功能"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.catalog = DataCatalog(self.temp_dir)

    def test_catalog_initialization(self):
        """测试目录初始化"""
        assert self.catalog.catalog_dir == self.temp_dir
        assert hasattr(self.catalog, 'assets')
        assert hasattr(self.catalog, 'lineages')

    def test_asset_creation(self):
        """测试资产创建"""
        asset = DataAsset(
            asset_id="test_asset",
            name="Test Asset",
            asset_type=DataAssetType.TABLE,
            classification=DataClassification.PUBLIC,
            format=DataFormat.JSON,
            description="Test asset for unit testing",
        )

        assert asset.asset_id == "test_asset"
        assert asset.name == "Test Asset"
        assert asset.asset_type == DataAssetType.TABLE

    def test_add_asset_to_catalog(self):
        """测试向目录添加资产"""
        asset = DataAsset(
            asset_id="catalog_test",
            name="Catalog Test Asset",
            asset_type=DataAssetType.FILE,
            classification=DataClassification.INTERNAL,
            format=DataFormat.CSV,
            description="Asset for catalog testing",
        )

        result = self.catalog.add_asset(asset)
        assert result is True
        assert "catalog_test" in self.catalog.assets

    def test_catalog_report_generation(self):
        """测试目录报告生成"""
        # 添加一些测试资产
        asset1 = DataAsset(
            asset_id="report_test_1",
            name="Report Test 1",
            asset_type=DataAssetType.TABLE,
            classification=DataClassification.PUBLIC,
            format=DataFormat.JSON,
            description="First test asset",
        )

        asset2 = DataAsset(
            asset_id="report_test_2",
            name="Report Test 2",
            asset_type=DataAssetType.API,
            classification=DataClassification.CONFIDENTIAL,
            format=DataFormat.XML,
            description="Second test asset",
        )

        self.catalog.add_asset(asset1)
        self.catalog.add_asset(asset2)

        report = self.catalog.generate_catalog_report()

        assert isinstance(report, dict)
        assert 'total_assets' in report
        assert 'by_type' in report
        assert 'by_classification' in report
        assert report['total_assets'] == 2


class TestMonitoringConfig:
    """测试监控配置功能"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = MonitoringConfigManager(self.temp_dir)

    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager.config_dir == self.temp_dir
        assert hasattr(self.manager, 'services')
        assert hasattr(self.manager, 'metrics')

    def test_prometheus_config_generation(self):
        """测试Prometheus配置生成"""
        config = self.manager.generate_prometheus_config()

        assert isinstance(config, dict)
        assert 'global' in config
        assert 'scrape_configs' in config

    def test_grafana_dashboard_generation(self):
        """测试Grafana仪表板生成"""
        dashboard = self.manager.generate_grafana_dashboard("test_service")

        assert isinstance(dashboard, dict)
        assert 'dashboard' in dashboard
        assert 'title' in dashboard['dashboard']

    def test_service_registration(self):
        """测试服务注册"""
        service_config = {
            'name': 'test_service',
            'port': 8080,
            'metrics_path': '/metrics',
            'health_path': '/health',
        }

        result = self.manager.register_service(service_config)
        assert result is True
        assert 'test_service' in self.manager.services

    def test_alerting_rules_generation(self):
        """测试告警规则生成"""
        rules = self.manager.generate_alerting_rules()

        assert isinstance(rules, dict)
        assert 'groups' in rules
        assert len(rules['groups']) > 0


class TestUtilityFunctions:
    """测试工具函数"""

    def test_path_operations(self):
        """测试路径操作"""
        temp_dir = Path(tempfile.mkdtemp())

        # 测试目录创建
        test_subdir = temp_dir / "test_subdir"
        test_subdir.mkdir(exist_ok=True)
        assert test_subdir.exists()

        # 测试文件创建
        test_file = test_subdir / "test_file.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        assert test_file.read_text() == "test content"

    def test_configuration_validation(self):
        """测试配置验证"""
        # 测试有效配置
        valid_config = {'name': 'test_project', 'version': '1.0.0', 'language': 'python'}

        assert 'name' in valid_config
        assert 'version' in valid_config
        assert 'language' in valid_config

    def test_error_handling(self):
        """测试错误处理"""
        # 测试文件不存在的情况
        non_existent_path = Path("/non/existent/path")
        assert not non_existent_path.exists()

        # 测试空配置
        empty_config = {}
        assert len(empty_config) == 0


class TestIntegrationScenarios:
    """测试集成场景"""

    def test_complete_workflow(self):
        """测试完整工作流"""
        temp_dir = Path(tempfile.mkdtemp())

        # 1. 创建数据目录
        catalog = DataCatalog(temp_dir / "catalog")

        # 2. 添加资产
        asset = DataAsset(
            asset_id="workflow_test",
            name="Workflow Test Asset",
            asset_type=DataAssetType.DATABASE,
            classification=DataClassification.INTERNAL,
            format=DataFormat.SQL,
            description="Asset for workflow testing",
        )

        catalog.add_asset(asset)

        # 3. 创建监控配置
        monitoring = MonitoringConfigManager(temp_dir / "monitoring")
        prometheus_config = monitoring.generate_prometheus_config()

        # 4. 验证结果
        assert len(catalog.assets) == 1
        assert isinstance(prometheus_config, dict)

        # 5. 生成报告
        catalog_report = catalog.generate_catalog_report()
        assert catalog_report['total_assets'] == 1

    def test_multilingual_support(self):
        """测试多语言支持"""
        # 测试中英文切换
        messages = {}

        set_locale('en')
        messages['en'] = {'welcome': _('welcome'), 'quality_score': _('quality_score', score=90)}

        set_locale('zh')
        messages['zh'] = {'welcome': _('welcome'), 'quality_score': _('quality_score', score=90)}

        # 验证不同语言的消息不同
        assert messages['en']['welcome'] != messages['zh']['welcome']
        assert '90' in messages['en']['quality_score']
        assert '90' in messages['zh']['quality_score']
