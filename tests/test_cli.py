"""
测试aiculture.cli模块
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from aiculture.cli import main, create, setup, check, culture, guide


class TestCLI:
    """测试CLI命令"""
    
    def setup_method(self):
        """设置测试环境"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_main_help(self):
        """测试主命令帮助信息"""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "AICultureKit" in result.output
        assert "标准化AI主导开发" in result.output
    
    def test_main_version(self):
        """测试版本信息"""
        result = self.runner.invoke(main, ['--version'])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
    
    @patch('aiculture.cli.ProjectTemplate')
    def test_create_command(self, mock_template_class):
        """测试create命令"""
        # Mock ProjectTemplate
        mock_template = MagicMock()
        mock_template_class.return_value = mock_template
        mock_template.create_project.return_value = True
        
        result = self.runner.invoke(create, [
            'test-project',
            '--path', self.temp_dir,
            '--template', 'python'
        ])
        
        assert result.exit_code == 0
        assert "正在创建项目: test-project" in result.output
        assert "项目创建成功" in result.output
        
        # 验证ProjectTemplate被正确调用
        mock_template.create_project.assert_called_once_with(
            project_name='test-project',
            target_path=self.temp_dir,
            template_type='python'
        )
    
    @patch('aiculture.cli.ProjectTemplate')
    def test_create_command_failure(self, mock_template_class):
        """测试create命令失败情况"""
        # Mock ProjectTemplate失败
        mock_template = MagicMock()
        mock_template_class.return_value = mock_template
        mock_template.create_project.return_value = False
        
        result = self.runner.invoke(create, [
            'test-project',
            '--path', self.temp_dir
        ])
        
        assert result.exit_code == 0
        assert "项目创建失败" in result.output
    
    @patch('aiculture.cli.ProjectTemplate')
    def test_create_command_exception(self, mock_template_class):
        """测试create命令异常情况"""
        # Mock ProjectTemplate抛出异常
        mock_template = MagicMock()
        mock_template_class.return_value = mock_template
        mock_template.create_project.side_effect = Exception("测试异常")
        
        result = self.runner.invoke(create, ['test-project'])
        
        assert result.exit_code == 0
        assert "创建过程中出现错误" in result.output
        assert "测试异常" in result.output
    
    @patch('aiculture.cli.QualityTools')
    @patch('aiculture.cli.CultureConfig')
    def test_setup_command(self, mock_config_class, mock_tools_class):
        """测试setup命令"""
        # Mock QualityTools
        mock_tools = MagicMock()
        mock_tools_class.return_value = mock_tools
        mock_tools.setup_pre_commit.return_value = True
        mock_tools.setup_linting.return_value = True
        
        # Mock CultureConfig
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        
        result = self.runner.invoke(setup, [
            '--path', self.temp_dir,
            '--language', 'python'
        ])
        
        assert result.exit_code == 0
        assert "正在为项目设置质量工具" in result.output
        assert "pre-commit 设置成功" in result.output
        assert "python 质量工具设置成功" in result.output
        assert "项目设置完成" in result.output
        
        # 验证方法调用
        mock_tools.setup_pre_commit.assert_called_once()
        mock_tools.setup_linting.assert_called_once_with('python')
        mock_config.save_config.assert_called_once()
    
    @patch('aiculture.cli.QualityTools')
    def test_setup_command_failures(self, mock_tools_class):
        """测试setup命令部分失败情况"""
        # Mock QualityTools with failures
        mock_tools = MagicMock()
        mock_tools_class.return_value = mock_tools
        mock_tools.setup_pre_commit.return_value = False
        mock_tools.setup_linting.return_value = False
        
        result = self.runner.invoke(setup, ['--path', self.temp_dir])
        
        assert result.exit_code == 0
        assert "pre-commit 设置失败" in result.output
        assert "python 质量工具设置失败" in result.output
    
    @patch('aiculture.cli.QualityTools')
    def test_check_command(self, mock_tools_class):
        """测试check命令"""
        # Mock QualityTools
        mock_tools = MagicMock()
        mock_tools_class.return_value = mock_tools
        mock_tools.run_quality_check.return_value = {
            'black': True,
            'flake8': True,
            'mypy': False
        }
        
        result = self.runner.invoke(check, ['--path', self.temp_dir])
        
        assert result.exit_code == 0
        assert "正在检查项目质量" in result.output
        assert "检查结果:" in result.output
        assert "✅ black: 通过" in result.output
        assert "✅ flake8: 通过" in result.output
        assert "❌ mypy: 未通过" in result.output
        assert "部分检查未通过" in result.output
    
    @patch('aiculture.cli.QualityTools')
    def test_check_command_all_pass(self, mock_tools_class):
        """测试check命令全部通过情况"""
        # Mock QualityTools - all pass
        mock_tools = MagicMock()
        mock_tools_class.return_value = mock_tools
        mock_tools.run_quality_check.return_value = {
            'black': True,
            'flake8': True,
            'mypy': True
        }
        
        result = self.runner.invoke(check, ['--path', self.temp_dir])
        
        assert result.exit_code == 0
        assert "所有检查均通过" in result.output
    
    @patch('aiculture.cli.CultureConfig')
    def test_culture_command(self, mock_config_class):
        """测试culture命令"""
        # Mock CultureConfig
        mock_config = MagicMock()
        mock_config_class.return_value = mock_config
        mock_config.get_principle.side_effect = lambda key: {
            'principles': ['YAGNI', 'KISS', 'SOLID'],
            'code_style': {'python': {'formatter': 'black'}},
            'ai_guidelines': {'context_sharing': True}
        }.get(key)
        
        result = self.runner.invoke(culture, ['--path', self.temp_dir])
        
        assert result.exit_code == 0
        assert "AI开发文化配置" in result.output
        assert "开发原则:" in result.output
        assert "YAGNI" in result.output
        assert "代码风格:" in result.output
        assert "AI协作指南:" in result.output
    
    def test_guide_command_python(self):
        """测试guide命令生成Python指南"""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(guide, ['--template', 'python'])
            
            assert result.exit_code == 0
            assert "正在生成 python AI协作指南" in result.output
            assert "AI协作指南已生成" in result.output
            
            # 检查文件是否生成
            guide_file = Path("AI_GUIDE.md")
            assert guide_file.exists()
            content = guide_file.read_text(encoding='utf-8')
            assert "Python项目AI协作指南" in content
            assert "YAGNI" in content
    
    def test_guide_command_javascript(self):
        """测试guide命令生成JavaScript指南"""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(guide, ['--template', 'javascript'])
            
            assert result.exit_code == 0
            assert "正在生成 javascript AI协作指南" in result.output
            
            # 检查文件内容
            guide_file = Path("AI_GUIDE.md")
            assert guide_file.exists()
            content = guide_file.read_text(encoding='utf-8')
            assert "JavaScript项目AI协作指南" in content
            assert "ESLint" in content
    
    def test_guide_command_full(self):
        """测试guide命令生成完整指南"""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(guide, ['--template', 'full'])
            
            assert result.exit_code == 0
            assert "正在生成 full AI协作指南" in result.output
            
            # 检查文件内容
            guide_file = Path("AI_GUIDE.md")
            assert guide_file.exists()
            content = guide_file.read_text(encoding='utf-8')
            assert "AI协作开发指南" in content
            assert "核心开发哲学" in content
            assert "SOLID原则" in content
    
    def test_create_command_with_options(self):
        """测试create命令带选项"""
        with patch('aiculture.cli.ProjectTemplate') as mock_template_class:
            mock_template = MagicMock()
            mock_template_class.return_value = mock_template
            mock_template.create_project.return_value = True
            
            result = self.runner.invoke(create, [
                'my-project',
                '--path', '/tmp',
                '--template', 'javascript',
                '--with-docker'
            ])
            
            assert result.exit_code == 0
            assert "模板: javascript" in result.output
            
            mock_template.create_project.assert_called_once_with(
                project_name='my-project',
                target_path='/tmp',
                template_type='javascript'
            )
    
    def test_setup_command_javascript(self):
        """测试setup命令支持JavaScript"""
        with patch('aiculture.cli.QualityTools') as mock_tools_class:
            with patch('aiculture.cli.CultureConfig') as mock_config_class:
                mock_tools = MagicMock()
                mock_tools_class.return_value = mock_tools
                mock_tools.setup_pre_commit.return_value = True
                mock_tools.setup_linting.return_value = True
                
                result = self.runner.invoke(setup, [
                    '--path', self.temp_dir,
                    '--language', 'javascript'
                ])
                
                assert result.exit_code == 0
                mock_tools.setup_linting.assert_called_once_with('javascript')
    
    def test_check_command_with_fix(self):
        """测试check命令带修复选项"""
        with patch('aiculture.cli.QualityTools') as mock_tools_class:
            mock_tools = MagicMock()
            mock_tools_class.return_value = mock_tools
            mock_tools.run_quality_check.return_value = {
                'black': False,
                'flake8': False
            }
            
            result = self.runner.invoke(check, [
                '--path', self.temp_dir,
                '--fix'
            ])
            
            assert result.exit_code == 0
            assert "正在尝试自动修复" in result.output 