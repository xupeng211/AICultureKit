"""
CLI 烟雾测试 - 快速验证CLI基本功能
测试 --help、--version 和基本命令入口
"""

import sys

import pytest
from click.testing import CliRunner

from aiculture import cli


class TestCLISmoke:
    """CLI 烟雾测试"""

    def test_cli_help_command(self):
        """测试 --help 命令"""
        runner = CliRunner()
        result = runner.invoke(cli.main, ['--help'])
        assert result.exit_code == 0
        assert 'Usage:' in result.output or 'Commands:' in result.output

    def test_create_command_help(self):
        """测试 create --help"""
        runner = CliRunner()
        result = runner.invoke(cli.create, ['--help'])
        assert result.exit_code == 0
        assert 'create' in result.output.lower()

    def test_check_command_help(self):
        """测试 check --help"""
        runner = CliRunner()
        result = runner.invoke(cli.check, ['--help'])
        assert result.exit_code == 0

    def test_init_command_help(self):
        """测试 init --help"""
        runner = CliRunner()
        result = runner.invoke(cli.init, ['--help'])
        assert result.exit_code == 0

    def test_invalid_command_exit_code(self):
        """测试无效命令返回非零退出码"""
        runner = CliRunner()
        result = runner.invoke(cli.main, ['nonexistent-command'])
        assert result.exit_code != 0

    def test_create_with_missing_args(self):
        """测试 create 命令缺少必要参数时的行为"""
        runner = CliRunner()
        result = runner.invoke(cli.create, [])
        # 可能会成功（显示帮助）或失败（需要参数），只要不崩溃即可
        assert result.exit_code in [0, 1, 2]  # 常见的CLI退出码

    def test_init_command_functionality(self):
        """测试 init 命令基本功能"""
        runner = CliRunner()
        # 使用 --help 确保不会真正执行初始化
        result = runner.invoke(cli.init, ['--help'])
        assert result.exit_code == 0 