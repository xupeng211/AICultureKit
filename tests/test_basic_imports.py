"""
基础导入和初始化测试
确保核心模块能正常导入，提升模块级别的覆盖率
"""

import pytest


class TestBasicImports:
    """基础导入测试"""

    def test_core_module_import(self):
        """测试核心模块导入"""
        from aiculture import core
        assert core is not None

    def test_cli_module_import(self):
        """测试CLI模块导入"""
        from aiculture import cli
        assert cli is not None

    def test_culture_config_import_and_init(self):
        """测试CultureConfig导入和初始化"""
        from aiculture.core import CultureConfig
        config = CultureConfig()
        assert config is not None
        assert hasattr(config, 'config')

    def test_quality_tools_import_and_init(self):
        """测试QualityTools导入和初始化"""
        from aiculture.core import QualityTools
        tools = QualityTools(".")
        assert tools is not None
        assert hasattr(tools, 'project_path')

    def test_project_template_import_and_init(self):
        """测试ProjectTemplate导入和初始化"""
        from aiculture.core import ProjectTemplate
        template = ProjectTemplate()
        assert template is not None

    def test_main_cli_group_accessible(self):
        """测试主CLI组可访问"""
        from aiculture.cli import main
        assert main is not None
        assert callable(main)

    def test_cli_commands_accessible(self):
        """测试CLI命令可访问"""
        from aiculture.cli import check, create, init
        assert create is not None
        assert check is not None
        assert init is not None
        assert all(callable(cmd) for cmd in [create, check, init])

    def test_package_init(self):
        """测试包初始化"""
        import aiculture
        assert aiculture is not None
        # 检查包是否有版本信息或其他基本属性
        assert hasattr(aiculture, '__path__') or hasattr(aiculture, '__file__')

    def test_basic_functionality_smoke(self):
        """基本功能烟雾测试"""
        from aiculture.core import CultureConfig

        # 创建配置实例
        config = CultureConfig()
        
        # 测试基本方法不会崩溃
        result = config.get_principle("test_principle")
        assert result is None or isinstance(result, dict)
        
        # 测试配置属性存在
        assert isinstance(config.config, dict)

    def test_cli_help_accessibility(self):
        """测试CLI帮助可访问性"""
        from click.testing import CliRunner

        from aiculture.cli import main
        
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        # 帮助命令应该成功执行
        assert result.exit_code == 0
        assert result.output is not None
        assert len(result.output) > 0

    def test_module_attributes(self):
        """测试模块属性"""
        from aiculture import cli, core

        # 检查模块有预期的属性
        assert hasattr(core, 'CultureConfig')
        assert hasattr(core, 'QualityTools') 
        assert hasattr(core, 'ProjectTemplate')
        
        assert hasattr(cli, 'main')
        assert hasattr(cli, 'create')
        assert hasattr(cli, 'check')

    def test_class_instantiation_resilience(self):
        """测试类实例化的健壮性"""
        from aiculture.core import CultureConfig, ProjectTemplate, QualityTools

        # 多次实例化应该都成功
        configs = [CultureConfig() for _ in range(3)]
        tools = [QualityTools(".") for _ in range(3)]
        templates = [ProjectTemplate() for _ in range(3)]
        
        # 所有实例都应该有效
        for config in configs:
            assert hasattr(config, 'config')
            
        for tool in tools:
            assert hasattr(tool, 'project_path')
            
        for template in templates:
            assert template is not None 