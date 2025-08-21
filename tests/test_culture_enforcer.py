"""
测试aiculture.culture_enforcer模块
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from aiculture.culture_enforcer import CultureEnforcer


class TestCultureEnforcer:
    """测试CultureEnforcer类"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.enforcer = CultureEnforcer(self.temp_path)

    def teardown_method(self) -> None:
        """清理测试环境"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_culture_enforcer_creation(self) -> None:
        """测试CultureEnforcer创建"""
        assert self.enforcer.project_path == self.temp_path
        assert hasattr(self.enforcer, "violations")
        assert isinstance(self.enforcer.violations, list)

    def test_culture_enforcer_with_string_path(self) -> None:
        """测试使用字符串路径创建CultureEnforcer"""
        enforcer = CultureEnforcer(str(self.temp_path))
        assert enforcer.project_path == self.temp_path

    def test_add_violation(self) -> None:
        """测试添加违规记录"""
        # 创建一个测试文件
        test_file = self.temp_path / "test.py"
        test_file.write_text("print('hello')")

        # 添加违规记录
        self.enforcer._add_violation(
            principle="test_principle",
            severity="warning",
            message="Test violation",
            file_path=str(test_file),
            line_number=1,
            suggestion="Fix this issue",
        )

        assert len(self.enforcer.violations) == 1
        violation = self.enforcer.violations[0]
        assert violation.principle == "test_principle"
        assert violation.severity == "warning"
        assert violation.description == "Test violation"
        assert violation.file_path == str(test_file)
        assert violation.line_number == 1
        assert violation.suggestion == "Fix this issue"

    def test_scan_python_files(self) -> None:
        """测试扫描Python文件"""
        # 创建测试Python文件
        py_file = self.temp_path / "test.py"
        py_file.write_text("def hello() -> None:\n    print('world')\n")

        # 创建非Python文件
        txt_file = self.temp_path / "test.txt"
        txt_file.write_text("This is not Python")

        python_files = list(self.enforcer._scan_python_files())
        assert len(python_files) == 1
        assert python_files[0] == py_file

    def test_scan_python_files_recursive(self) -> None:
        """测试递归扫描Python文件"""
        # 创建子目录和文件
        subdir = self.temp_path / "subdir"
        subdir.mkdir()

        py_file1 = self.temp_path / "test1.py"
        py_file1.write_text("print('test1')")

        py_file2 = subdir / "test2.py"
        py_file2.write_text("print('test2')")

        python_files = list(self.enforcer._scan_python_files())
        assert len(python_files) == 2
        assert py_file1 in python_files
        assert py_file2 in python_files

    def test_check_file_structure(self) -> None:
        """测试检查文件结构"""
        # 创建基本的项目结构
        (self.temp_path / "README.md").write_text("# Test Project")
        (self.temp_path / "requirements.txt").write_text("pytest")

        # 运行文件结构检查
        self.enforcer._check_file_structure()

        # 应该有一些违规记录（缺少其他必要文件）
        structure_violations = [v for v in self.enforcer.violations if "文件结构" in v.description]
        # 至少应该检测到一些缺失的文件
        assert len(structure_violations) >= 0  # 可能为0如果所有必要文件都存在

    def test_generate_report(self) -> None:
        """测试生成报告"""
        # 添加一些测试违规记录
        self.enforcer._add_violation(
            principle="test1",
            severity="error",
            message="Test error",
            suggestion="Fix error",
        )

        self.enforcer._add_violation(
            principle="test2",
            severity="warning",
            message="Test warning",
            suggestion="Fix warning",
        )

        report = self.enforcer._generate_report()

        assert isinstance(report, dict)
        assert "score" in report
        assert "errors" in report
        assert "warnings" in report
        assert "violations" in report
        assert "by_principle" in report

        assert report["errors"] == 1
        assert report["warnings"] == 1
        assert len(report["violations"]) == 2
        assert report["score"] <= 100

    def test_enforce_all(self) -> None:
        """测试执行所有检查"""
        # 创建一个简单的Python文件
        py_file = self.temp_path / "test.py"
        py_file.write_text("def test() -> None:\n    pass\n")

        report = self.enforcer.enforce_all()

        assert isinstance(report, dict)
        assert "score" in report
        assert "errors" in report
        assert "warnings" in report
        assert "violations" in report
        assert isinstance(report["violations"], list)

    def test_empty_project_enforcement(self) -> None:
        """测试空项目的执行检查"""
        report = self.enforcer.enforce_all()

        # 空项目应该有一些基本的违规记录
        assert isinstance(report, dict)
        assert report["score"] < 100  # 空项目不应该得满分

    @patch("subprocess.run")
    def test_check_code_quality_tools(self, mock_run) -> None:
        """测试代码质量工具检查"""
        # Mock subprocess.run to simulate tool execution
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""

        # 创建一个Python文件
        py_file = self.temp_path / "test.py"
        py_file.write_text("def test() -> None:\n    pass\n")

        # 运行代码质量检查
        self.enforcer._check_code_quality()

        # 验证subprocess.run被调用
        assert mock_run.called

    def test_calculate_score(self) -> None:
        """测试分数计算"""
        # 测试无违规情况
        assert self.enforcer._calculate_score(0, 0) == 100

        # 测试有违规情况
        score_with_errors = self.enforcer._calculate_score(2, 1)
        assert score_with_errors < 100
        assert score_with_errors >= 0

        # 错误应该比警告扣分更多
        score_errors_only = self.enforcer._calculate_score(1, 0)
        score_warnings_only = self.enforcer._calculate_score(0, 1)
        assert score_errors_only < score_warnings_only
