"""
测试aiculture.cli模块
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from aiculture.cli import check, create, main


class TestCLI:
    """测试CLI命令"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self) -> None:
        """清理测试环境"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_main_help(self) -> None:
        """测试主命令帮助信息"""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "AICultureKit" in result.output
        assert "标准化AI主导开发" in result.output

    def test_main_version(self) -> None:
        """测试版本信息"""
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    @patch("aiculture.cli.ProjectTemplate")
    def test_create_command(self, mock_template_class) -> None:
        """测试create命令"""
        # Mock ProjectTemplate
        mock_template = MagicMock()
        mock_template_class.return_value = mock_template
        mock_template.create_project.return_value = True

        result = self.runner.invoke(
            create, ["test-project", "--path", self.temp_dir, "--template", "python"]
        )

        assert result.exit_code == 0
        assert "正在创建项目: test-project" in result.output
        assert "项目创建成功" in result.output

        # 验证ProjectTemplate被正确调用
        mock_template.create_project.assert_called_once_with(
            project_name="test-project",
            target_path=self.temp_dir,
            template_type="python",
        )

    @patch("aiculture.cli.ProjectTemplate")
    def test_create_command_failure(self, mock_template_class) -> None:
        """测试create命令失败情况"""
        # Mock ProjectTemplate失败
        mock_template = MagicMock()
        mock_template_class.return_value = mock_template
        mock_template.create_project.return_value = False

        result = self.runner.invoke(create, ["test-project", "--path", self.temp_dir])

        assert result.exit_code == 0
        assert "项目创建失败" in result.output

    @patch("aiculture.cli.ProjectTemplate")
    def test_create_command_exception(self, mock_template_class) -> None:
        """测试create命令异常情况"""
        # Mock ProjectTemplate抛出异常
        mock_template = MagicMock()
        mock_template_class.return_value = mock_template
        mock_template.create_project.side_effect = Exception("测试异常")

        result = self.runner.invoke(create, ["test-project"])

        assert result.exit_code == 0
        assert "创建过程中出现错误" in result.output
        assert "测试异常" in result.output

    @patch("aiculture.cli.QualityTools")
    def test_check_command(self, mock_tools_class) -> None:
        """测试check命令"""
        # Mock QualityTools
        mock_tools = MagicMock()
        mock_tools_class.return_value = mock_tools
        mock_tools.run_quality_check.return_value = {
            "black": True,
            "flake8": True,
            "mypy": False,
        }

        result = self.runner.invoke(check, ["--path", self.temp_dir])

        assert result.exit_code == 0
        assert "正在检查项目质量" in result.output
        assert "检查结果:" in result.output
        assert "✅ black: 通过" in result.output
        assert "✅ flake8: 通过" in result.output
        assert "❌ mypy: 未通过" in result.output
        assert "部分检查未通过" in result.output

    @patch("aiculture.cli.QualityTools")
    def test_check_command_all_pass(self, mock_tools_class) -> None:
        """测试check命令全部通过情况"""
        # Mock QualityTools - all pass
        mock_tools = MagicMock()
        mock_tools_class.return_value = mock_tools
        mock_tools.run_quality_check.return_value = {
            "black": True,
            "flake8": True,
            "mypy": True,
        }

        result = self.runner.invoke(check, ["--path", self.temp_dir])

        assert result.exit_code == 0
        assert "所有检查均通过" in result.output

    def test_create_command_with_options(self) -> None:
        """测试create命令带选项"""
        with patch("aiculture.cli.ProjectTemplate") as mock_template_class:
            mock_template = MagicMock()
            mock_template_class.return_value = mock_template
            mock_template.create_project.return_value = True

            result = self.runner.invoke(
                create,
                [
                    "my-project",
                    "--path",
                    "/tmp",
                    "--template",
                    "javascript",
                    "--with-docker",
                ],
            )

            assert result.exit_code == 0
            assert "模板: javascript" in result.output

            mock_template.create_project.assert_called_once_with(
                project_name="my-project",
                target_path="/tmp",
                template_type="javascript",
            )

    def test_check_command_with_fix(self) -> None:
        """测试check命令带修复选项"""
        with patch("aiculture.cli.QualityTools") as mock_tools_class:
            mock_tools = MagicMock()
            mock_tools_class.return_value = mock_tools
            mock_tools.run_quality_check.return_value = {
                "black": False,
                "flake8": False,
            }

            result = self.runner.invoke(check, ["--path", self.temp_dir, "--fix"])

            assert result.exit_code == 0
            assert "正在尝试自动修复" in result.output
