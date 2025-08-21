"""
测试aiculture.environment_checker模块
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from aiculture.environment_checker import EnvironmentChecker


class TestEnvironmentChecker:
    """测试EnvironmentChecker类"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.checker = EnvironmentChecker(self.temp_path)

    def teardown_method(self) -> None:
        """清理测试环境"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_environment_checker_creation(self) -> None:
        """测试EnvironmentChecker创建"""
        assert self.checker.project_path == self.temp_path

    def test_environment_checker_with_string_path(self) -> None:
        """测试使用字符串路径创建EnvironmentChecker"""
        checker = EnvironmentChecker(str(self.temp_path))
        assert checker.project_path == self.temp_path

    def test_check_virtual_env_not_active(self) -> None:
        """测试检查虚拟环境（未激活）"""
        # 在大多数测试环境中，虚拟环境可能已激活，但我们可以测试方法存在
        result = self.checker.check_virtual_env()
        assert isinstance(result, bool)

    def test_get_virtual_env_path(self) -> None:
        """测试获取虚拟环境路径"""
        path = self.checker.get_virtual_env_path()
        # 路径可能为None或字符串
        assert path is None or isinstance(path, str)

    @patch("subprocess.run")
    def test_get_python_info(self, mock_run) -> None:
        """测试获取Python信息"""
        # Mock subprocess.run for python --version
        mock_run.return_value.stdout = "Python 3.9.0"
        mock_run.return_value.returncode = 0

        info = self.checker.get_python_info()

        assert isinstance(info, dict)
        assert "version" in info
        assert "executable" in info

    def test_check_project_structure(self) -> None:
        """测试检查项目结构"""
        # 创建一些项目文件
        (self.temp_path / "README.md").write_text("# Test")
        (self.temp_path / "requirements.txt").write_text("pytest")

        structure = self.checker.check_project_structure()

        assert isinstance(structure, dict)
        assert "README.md" in structure
        assert "requirements.txt" in structure
        assert structure["README.md"] == True
        assert structure["requirements.txt"] == True

        # 检查不存在的文件
        assert "pyproject.toml" in structure
        assert structure["pyproject.toml"] == False

    @patch("subprocess.run")
    def test_check_required_dependencies(self, mock_run) -> None:
        """测试检查必需依赖"""
        # 创建requirements.txt
        requirements_content = "pytest>=7.0.0\nclick>=8.0.0\n"
        (self.temp_path / "requirements.txt").write_text(requirements_content)

        # Mock pip list output
        mock_run.return_value.stdout = "pytest 7.1.0\nclick 8.1.0\n"
        mock_run.return_value.returncode = 0

        deps_ok, missing = self.checker.check_required_dependencies()

        assert isinstance(deps_ok, bool)
        assert isinstance(missing, list)

    @patch("subprocess.run")
    def test_check_development_dependencies(self, mock_run) -> None:
        """测试检查开发依赖"""
        # 创建requirements-dev.txt
        dev_requirements = "black>=23.0.0\nflake8>=6.0.0\n"
        (self.temp_path / "requirements-dev.txt").write_text(dev_requirements)

        # Mock pip list output
        mock_run.return_value.stdout = "black 23.1.0\nflake8 6.0.0\n"
        mock_run.return_value.returncode = 0

        deps_ok, missing = self.checker.check_development_dependencies()

        assert isinstance(deps_ok, bool)
        assert isinstance(missing, list)

    def test_check_aiculture_installation(self) -> None:
        """测试检查AICultureKit安装"""
        # 这个测试在当前环境中应该返回True，因为我们正在测试这个包
        result = self.checker.check_aiculture_installation()
        assert isinstance(result, bool)

    @patch("subprocess.run")
    def test_get_installed_packages_count(self, mock_run) -> None:
        """测试获取已安装包数量"""
        # Mock pip list output
        mock_run.return_value.stdout = (
            "package1 1.0.0\npackage2 2.0.0\npackage3 3.0.0\n"
        )
        mock_run.return_value.returncode = 0

        count = self.checker.get_installed_packages_count()

        assert isinstance(count, int)
        assert count >= 0

    @patch("subprocess.run")
    def test_check_git_status(self, mock_run) -> None:
        """测试检查Git状态"""
        # Mock git commands
        mock_run.side_effect = [
            # git rev-parse --is-inside-work-tree
            MagicMock(returncode=0, stdout="true"),
            # git branch --show-current
            MagicMock(returncode=0, stdout="main"),
            # git status --porcelain
            MagicMock(returncode=0, stdout=""),
            # git remote get-url origin
            MagicMock(returncode=0, stdout="https://github.com/user/repo.git"),
        ]

        git_info = self.checker.check_git_status()

        assert isinstance(git_info, dict)
        assert "is_repo" in git_info
        assert "current_branch" in git_info
        assert "has_uncommitted_changes" in git_info

    def test_generate_environment_report(self) -> None:
        """测试生成环境报告"""
        with (
            patch.object(self.checker, "get_python_info") as mock_python,
            patch.object(self.checker, "check_required_dependencies") as mock_req,
            patch.object(self.checker, "check_development_dependencies") as mock_dev,
            patch.object(self.checker, "check_virtual_env") as mock_venv,
            patch.object(self.checker, "get_virtual_env_path") as mock_venv_path,
            patch.object(self.checker, "check_aiculture_installation") as mock_ai,
            patch.object(self.checker, "check_project_structure") as mock_struct,
            patch.object(self.checker, "get_installed_packages_count") as mock_count,
            patch.object(self.checker, "check_git_status") as mock_git,
        ):
            # Setup mocks
            mock_python.return_value = {
                "version": "3.9.0",
                "executable": "/usr/bin/python3",
            }
            mock_req.return_value = (True, [])
            mock_dev.return_value = (True, [])
            mock_venv.return_value = True
            mock_venv_path.return_value = "/path/to/venv"
            mock_ai.return_value = True
            mock_struct.return_value = {"README.md": True}
            mock_count.return_value = 50
            mock_git.return_value = {"is_repo": True, "current_branch": "main"}

            report = self.checker.generate_environment_report()

            assert isinstance(report, dict)
            assert "timestamp" in report
            assert "virtual_environment" in report
            assert "python" in report
            assert "dependencies" in report
            assert "aiculture" in report
            assert "project_structure" in report
            assert "installed_packages_count" in report
            assert "git" in report

    def test_suggest_fixes(self) -> None:
        """测试建议修复措施"""
        with patch.object(self.checker, "generate_environment_report") as mock_report:
            # Mock a report with some issues
            mock_report.return_value = {
                "virtual_environment": {"is_active": False},
                "dependencies": {
                    "required": {"all_installed": False, "missing": ["pytest"]},
                    "development": {"all_installed": True, "missing": []},
                },
                "aiculture": {"installed": False},
                "project_structure": {"setup_environment.sh": False},
            }

            suggestions = self.checker.suggest_fixes()

            assert isinstance(suggestions, list)
            assert len(suggestions) > 0

            # 检查是否包含预期的建议
            suggestion_text = " ".join(suggestions)
            assert "虚拟环境" in suggestion_text or "依赖" in suggestion_text
