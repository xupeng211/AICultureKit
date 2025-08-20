"""
测试aiculture.core模块
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aiculture.core import CultureConfig, ProjectTemplate, QualityTools


class TestCultureConfig:
    """测试CultureConfig类"""

    def test_default_config_creation(self) -> None:
        """测试默认配置创建"""
        config = CultureConfig()
        assert "culture" in config.config
        assert "principles" in config.config["culture"]
        assert "YAGNI" in str(config.config["culture"]["principles"])

    def test_get_principle(self) -> None:
        """测试获取文化原则"""
        config = CultureConfig()
        principles = config.get_principle("principles")
        assert isinstance(principles, list)
        assert len(principles) > 0

    def test_save_and_load_config(self) -> None:
        """测试配置保存和加载"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_path = f.name

        try:
            # 创建并保存配置
            config = CultureConfig(config_path)
            config.save_config()

            # 重新加载配置
            config2 = CultureConfig(config_path)
            assert config2.config == config.config
        finally:
            os.unlink(config_path)


class TestQualityTools:
    """测试QualityTools类"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """清理测试环境"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_quality_tools_init(self) -> None:
        """测试QualityTools初始化"""
        tools = QualityTools(str(self.project_path))
        assert tools.project_path == self.project_path

    @patch("subprocess.run")
    def test_run_quality_check(self, mock_run) -> None:
        """测试质量检查执行"""
        mock_run.return_value.returncode = 0

        tools = QualityTools(str(self.project_path))
        results = tools.run_quality_check()

        # 检查所有工具的结果
        expected_tools = ["black", "flake8", "mypy"]
        for tool in expected_tools:
            assert tool in results

    @patch("subprocess.run")
    def test_run_quality_check_with_failures(self, mock_run) -> None:
        """测试质量检查失败情况"""
        mock_run.return_value.returncode = 1  # 模拟失败

        tools = QualityTools(str(self.project_path))
        results = tools.run_quality_check()

        # 所有检查都应该失败
        for tool, passed in results.items():
            if tool in ["black", "flake8", "mypy"]:
                assert not passed

    def test_setup_python_linting(self) -> None:
        """测试Python linting设置"""
        tools = QualityTools(str(self.project_path))
        success = tools._setup_python_linting()
        assert success

        # 检查.flake8配置文件是否被创建
        flake8_config = self.project_path / ".flake8"
        assert flake8_config.exists()
        content = flake8_config.read_text()
        assert "max-line-length = 88" in content


class TestProjectTemplate:
    """测试ProjectTemplate类"""

    def setup_method(self) -> None:
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.target_path = Path(self.temp_dir)
        self.project_name = "test-project"

    def teardown_method(self) -> None:
        """清理测试环境"""
        import shutil

        shutil.rmtree(self.temp_dir)

    @patch("aiculture.core.Repo")
    def test_create_python_project(self, mock_repo_class) -> None:
        """测试创建Python项目"""
        # Mock git repository
        mock_repo = MagicMock()
        mock_repo_class.init.return_value = mock_repo

        template = ProjectTemplate()
        success = template.create_project(
            project_name=self.project_name,
            target_path=str(self.target_path),
            template_type="python",
        )

        assert success

        # 检查项目结构
        project_path = self.target_path / self.project_name
        assert project_path.exists()

        # 检查Python包结构
        package_path = project_path / "test_project"  # - 转换为 _
        assert package_path.exists()
        assert (package_path / "__init__.py").exists()
        assert (package_path / "main.py").exists()

        # 检查测试目录
        assert (project_path / "tests").exists()
        assert (project_path / "tests" / "__init__.py").exists()
        assert (project_path / "tests" / "test_main.py").exists()

        # 检查GitHub Actions
        workflows_path = project_path / ".github" / "workflows"
        assert workflows_path.exists()
        assert (workflows_path / "ci.yml").exists()
        assert (workflows_path / "cd.yml").exists()

    def test_create_python_structure(self) -> None:
        """测试Python项目结构创建"""
        template = ProjectTemplate()
        project_path = self.target_path / self.project_name
        project_path.mkdir(parents=True)

        template._create_python_structure(project_path, self.project_name)

        # 验证目录结构
        expected_dirs = ["test_project", "tests", "docs", "scripts"]
        for dir_name in expected_dirs:
            assert (project_path / dir_name).exists()

        # 验证关键文件
        package_init = project_path / "test_project" / "__init__.py"
        assert package_init.exists()
        content = package_init.read_text()
        assert "__version__" in content
        assert "test-project" in content

    def test_create_js_structure(self) -> None:
        """测试JavaScript项目结构创建"""
        template = ProjectTemplate()
        project_path = self.target_path / self.project_name
        project_path.mkdir(parents=True)

        template._create_js_structure(project_path, self.project_name)

        # 验证目录结构
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()

        # 验证package.json
        package_json = project_path / "package.json"
        assert package_json.exists()

        import json

        package_data = json.loads(package_json.read_text())
        assert package_data["name"] == self.project_name
        assert "scripts" in package_data

    def test_get_ci_workflow_content(self) -> None:
        """测试CI工作流内容生成"""
        template = ProjectTemplate()
        content = template._get_ci_workflow_content()

        assert "name: CI" in content
        assert "python-version:" in content
        assert "pytest" in content
        assert "black" in content
        assert "flake8" in content
        assert "mypy" in content

    def test_get_cd_workflow_content(self) -> None:
        """测试CD工作流内容生成"""
        template = ProjectTemplate()
        content = template._get_cd_workflow_content()

        assert "name: CD" in content
        assert "twine upload" in content
        assert "python -m build" in content


@pytest.fixture
def temp_project_dir() -> None:
    """临时项目目录fixture"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    import shutil

    shutil.rmtree(temp_dir)


def test_integration_create_and_check_project(temp_project_dir) -> None:
    """集成测试：创建项目并检查质量"""
    project_name = "integration-test"

    # 创建项目
    template = ProjectTemplate()
    with patch("aiculture.core.Repo"):  # Mock git
        success = template.create_project(
            project_name=project_name,
            target_path=str(temp_project_dir),
            template_type="python",
        )

    assert success

    project_path = temp_project_dir / project_name
    assert project_path.exists()

    # 检查质量工具能否正常工作
    tools = QualityTools(str(project_path))

    # 测试Python linting设置
    success = tools._setup_python_linting()
    assert success

    # 检查配置文件是否存在
    assert (project_path / ".flake8").exists()
    assert (project_path / ".gitignore").exists()
    assert (project_path / ".github" / "workflows" / "ci.yml").exists()
