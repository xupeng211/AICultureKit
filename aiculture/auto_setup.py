from typing import Any

"""
自动化项目设置脚本

为项目自动配置所有必要的文化规范工具和配置文件。
"""

from pathlib import Path

from .ai_culture_principles import AICulturePrinciples
import re


class AutoCultureSetup:
    """自动化文化设置器"""

    def __init__(self, project_path: str = ".") -> None:
        """内部方法： init"""
        self.project_path = Path(project_path)
        self.principles = AICulturePrinciples()

    def setup_complete_culture(self, project_type: str = "python") -> bool:
        """设置完整的开发文化"""
        try:
            # 1. 创建文化配置文件
            self._create_culture_config()

            # 2. 设置AI助手指导文档
            self._create_ai_guidelines()

            # 3. 配置质量工具
            self._setup_quality_tools(project_type)

            # 4. 设置CI/CD
            self._setup_cicd(project_type)

            # 5. 创建项目模板文件
            self._create_template_files(project_type)

            # 6. 设置预提交钩子
            self._setup_precommit_hooks()

            print("✅ AI开发文化设置完成！")
            return True

        except Exception as e:
            print(f"❌ 设置过程中出现错误: {e}")
            return False

    def _create_culture_config(self) -> Any:
        """创建文化配置文件"""
        config_path = self.project_path / "aiculture.yaml"

        # 导出所有原则到配置文件
        self.principles.export_to_yaml(str(config_path))

        # 添加项目特定配置
        with open(config_path, 'a', encoding='utf-8') as f:
            f.write(
                """
# 项目特定配置
project:
  name: "AI驱动项目"
  ai_assistant_config:
    enforce_principles: true
    auto_fix_violations: true
    generate_suggestions: true
    require_documentation: true

# 质量门禁
quality_gates:
  min_test_coverage: 80
  max_complexity: 10
  security_scan: true
  code_review_required: true

# AI行为配置
ai_behavior:
  code_style_enforcement: "strict"
  documentation_generation: true
  test_generation: true
  refactoring_suggestions: true
"""
            )

    def _create_ai_guidelines(self) -> Any:
        """创建AI助手指导文档"""
        guidelines_content = """# 🤖 AI助手项目指导原则

> 本项目采用严格的AI开发文化标准，请所有AI助手严格遵循以下原则

## 📋 核心指令

### 代码编写指令
1. **强制执行SOLID原则** - 每个类、函数必须职责单一
2. **零容忍重复代码** - 发现重复立即重构
3. **安全优先** - 永远不信任用户输入
4. **测试驱动** - 先写测试再写实现
5. **文档同步** - 代码变更必须更新文档

### 质量检查清单
在提交任何代码前，必须确认：
- [ ] 遵循项目代码风格
- [ ] 通过所有质量检查
- [ ] 测试覆盖率 ≥ 80%
- [ ] 无安全漏洞
- [ ] 文档已更新

### 禁止行为
- ❌ 提交未测试代码
- ❌ 硬编码敏感信息
- ❌ 忽略代码审查
- ❌ 跳过文档更新

## 🔧 当前项目配置

项目已配置以下工具链：
"""

        guidelines_path = self.project_path / "AI_PROJECT_GUIDELINES.md"
        with open(guidelines_path, 'w', encoding='utf-8') as f:
            f.write(guidelines_content)

            # 添加当前项目的具体配置信息
            f.write(
                """
- 代码格式化：Black (行长度88)
- 静态分析：flake8 + mypy
- 安全扫描：bandit
- 测试框架：pytest
- 覆盖率要求：80%
- 预提交检查：已启用

请确保所有代码都符合以上标准！
"""
            )

    def _setup_quality_tools(self, project_type: str) -> Any:
        """设置质量工具配置"""
        if project_type == "python":
            self._setup_python_quality_tools()
        elif project_type in ["javascript", "typescript"]:
            self._setup_js_quality_tools()

    def _setup_python_quality_tools(self) -> Any:
        """设置Python质量工具"""
        # pyproject.toml配置
        pyproject_config = """
[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --cov=. --cov-report=term-missing --cov-report=html"
testpaths = ["tests"]

[tool.bandit]
exclude_dirs = ["tests"]
skips = ["B101"]
"""

        pyproject_path = self.project_path / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, 'a', encoding='utf-8') as f:
                f.write(pyproject_config)
        else:
            with open(pyproject_path, 'w', encoding='utf-8') as f:
                f.write("[build-system]\nrequires = ['setuptools', 'wheel']\n")
                f.write(pyproject_config)

    def _setup_js_quality_tools(self) -> Any:
        """设置JavaScript/TypeScript质量工具"""
        # .eslintrc.js配置
        eslint_config = """{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended"
  ],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "prefer-const": "error"
  }
}"""

        eslint_path = self.project_path / ".eslintrc.json"
        with open(eslint_path, 'w', encoding='utf-8') as f:
            f.write(eslint_config)

    def _setup_cicd(self, project_type: str) -> Any:
        """设置CI/CD流水线"""
        github_dir = self.project_path / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)

        if project_type == "python":
            ci_content = """name: AI Culture CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  culture-check:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
        pip install aiculture-kit

    - name: AI Culture Principles Check
      run: |
        aiculture validate .

    - name: Code Quality Check
      run: |
        black --check .
        isort --check-only .
        flake8 .
        mypy .

    - name: Security Check
      run: bandit -r .

    - name: Test with Coverage
      run: |
        pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
"""

            ci_path = github_dir / "ai-culture-ci.yml"
            with open(ci_path, 'w', encoding='utf-8') as f:
                f.write(ci_content)

    def _create_template_files(self, project_type: str) -> Any:
        """创建项目模板文件"""
        # 创建.gitignore
        gitignore_content = """# AI Culture Kit
.aiculture/
coverage.xml
.coverage
htmlcov/

# Python
__pycache__/
*.py[cod]
*.so
.env
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""

        gitignore_path = self.project_path / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)

        # 创建requirements-dev.txt
        if project_type == "python":
            dev_requirements = """# AI Culture Kit Development Dependencies
aiculture-kit>=0.1.0
black>=22.0.0
isort>=5.0.0
flake8>=4.0.0
mypy>=0.991
pytest>=7.0.0
pytest-cov>=4.0.0
bandit>=1.7.0
pre-commit>=2.20.0
"""

            req_dev_path = self.project_path / "requirements-dev.txt"
            if not req_dev_path.exists():
                with open(req_dev_path, 'w', encoding='utf-8') as f:
                    f.write(dev_requirements)

    def _setup_precommit_hooks(self) -> Any:
        """设置预提交钩子"""
        precommit_config = """repos:
  - repo: local
    hooks:
      - id: ai-culture-check
        name: AI Culture Principles Check
        entry: aiculture validate
        language: system
        pass_filenames: false
        always_run: true

  - repo: https://github.com/psf/black
    rev: 22.12.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
"""

        precommit_path = self.project_path / ".pre-commit-config.yaml"
        with open(precommit_path, 'w', encoding='utf-8') as f:
            f.write(precommit_config)


def setup_ai_culture(project_path: str = ".", project_type: str = "python") -> bool:
    """为项目设置完整的AI开发文化"""
    setup = AutoCultureSetup(project_path)
    return setup.setup_complete_culture(project_type)
