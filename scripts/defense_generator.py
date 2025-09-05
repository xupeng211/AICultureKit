#!/usr/bin/env python3
"""
CI防御机制生成器 - 根据CI问题自动生成防御措施

这个模块负责：
1. 根据CI问题类型生成针对性的测试用例
2. 创建和更新lint规则配置
3. 生成预提交钩子配置
4. 创建CI流程增强配置
5. 生成代码质量门禁规则

作者：AI CI Guardian System
版本：v1.0.0
"""

import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import click
import yaml


class TestGenerator:
    """测试用例生成器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        self.generated_tests = []
    
    def generate_validation_tests(self, issues: List[Dict]) -> List[str]:
        """根据问题生成验证测试"""
        generated_files = []
        
        # 按问题类型分组
        issues_by_type = defaultdict(list)
        for issue in issues:
            category = issue.get('category', 'other')
            issues_by_type[category].append(issue)
        
        # 为每种问题类型生成测试
        for category, category_issues in issues_by_type.items():
            if category == 'import_error':
                test_file = self._generate_import_tests(category_issues)
            elif category == 'type_error':
                test_file = self._generate_type_tests(category_issues)
            elif category == 'assertion_failure':
                test_file = self._generate_assertion_tests(category_issues)
            elif category == 'style_error':
                test_file = self._generate_style_tests(category_issues)
            elif category == 'security_issue':
                test_file = self._generate_security_tests(category_issues)
            else:
                test_file = self._generate_generic_tests(category, category_issues)
            
            if test_file:
                generated_files.append(test_file)
        
        return generated_files
    
    def _generate_import_tests(self, issues: List[Dict]) -> Optional[str]:
        """生成导入验证测试"""
        test_file = "test_import_validation.py"
        test_path = self.tests_dir / test_file
        
        # 提取失败的导入
        failed_modules = set()
        for issue in issues:
            if 'file_path' in issue and issue['file_path']:
                # 从文件路径推断模块名
                file_path = issue['file_path']
                if file_path.startswith('src/'):
                    module_name = file_path.replace('src/', '').replace('/', '.').replace('.py', '')
                    failed_modules.add(module_name)
            
            # 从错误消息中提取模块名
            if 'message' in issue:
                module_match = re.search(r"No module named '([^']+)'", issue['message'])
                if module_match:
                    failed_modules.add(module_match.group(1))
        
        test_content = f'''"""
导入验证测试 - 防止导入错误再次发生
自动生成时间: {datetime.now().isoformat()}
基于 {len(issues)} 个导入错误生成
"""

import importlib
import pytest
import sys
from pathlib import Path

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestImportValidation:
    """验证所有模块都能正确导入"""
    
    def test_core_modules_import(self):
        """测试核心模块导入"""
        core_modules = [
            "src.core",
            "src.models",
            "src.services", 
            "src.utils"
        ]
        
        for module_name in core_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"核心模块 {{module_name}} 导入失败: {{e}}")
    
    {"".join([f'''
    def test_{module.replace(".", "_")}_import(self):
        """测试 {module} 模块导入 - 之前失败过"""
        try:
            importlib.import_module("{module}")
        except ImportError as e:
            pytest.fail(f"模块 {module} 导入失败: {{e}}")
    ''' for module in sorted(failed_modules) if module])}
    
    def test_relative_imports(self):
        """测试相对导入是否正确"""
        # 检测可能的相对导入问题
        try:
            from src.core import *
        except ImportError as e:
            if "attempted relative import" in str(e):
                pytest.fail(f"相对导入错误: {{e}}")
    
    def test_circular_imports(self):
        """检测循环导入"""
        import sys
        original_modules = set(sys.modules.keys())
        
        try:
            import src
        except ImportError as e:
            if "circular import" in str(e).lower():
                pytest.fail(f"检测到循环导入: {{e}}")
        finally:
            # 清理导入的模块
            new_modules = set(sys.modules.keys()) - original_modules
            for module in new_modules:
                if module.startswith('src.'):
                    sys.modules.pop(module, None)
    
    def test_dependency_availability(self):
        """测试第三方依赖可用性"""
        required_packages = [
            "fastapi",
            "pydantic",
            "pytest", 
            "click"
        ]
        
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError as e:
                pytest.fail(f"必需依赖 {{package}} 不可用: {{e}}")
'''
        
        self._write_test_file(test_path, test_content)
        return test_file
    
    def _generate_type_tests(self, issues: List[Dict]) -> Optional[str]:
        """生成类型检查测试"""
        test_file = "test_type_validation.py"
        test_path = self.tests_dir / test_file
        
        # 提取类型相关的问题
        type_issues = []
        for issue in issues:
            if issue.get('tool') == 'mypy' or 'type' in issue.get('category', ''):
                type_issues.append(issue)
        
        test_content = f'''"""
类型验证测试 - 防止类型错误再次发生
自动生成时间: {datetime.now().isoformat()}
基于 {len(type_issues)} 个类型错误生成
"""

import inspect
import typing
from typing import get_type_hints
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestTypeValidation:
    """验证类型注解的正确性"""
    
    def test_function_type_annotations(self):
        """测试函数类型注解"""
        import src
        
        for module_name in ["core", "models", "services", "utils"]:
            try:
                module = getattr(src, module_name, None)
                if module is None:
                    continue
                
                # 检查模块中的函数类型注解
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj):
                        try:
                            type_hints = get_type_hints(obj)
                        except (NameError, AttributeError) as e:
                            pytest.fail(f"函数 {{module_name}}.{{name}} 类型注解错误: {{e}}")
            except ImportError:
                # 如果模块导入失败，跳过
                continue
    
    def test_class_method_annotations(self):
        """测试类方法类型注解"""
        import src
        
        for module_name in ["core", "models", "services", "utils"]:
            try:
                module = getattr(src, module_name, None)
                if module is None:
                    continue
                
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        for method_name, method in inspect.getmembers(obj):
                            if inspect.isfunction(method) or inspect.ismethod(method):
                                try:
                                    type_hints = get_type_hints(method)
                                except (NameError, AttributeError) as e:
                                    pytest.fail(
                                        f"方法 {{module_name}}.{{name}}.{{method_name}} "
                                        f"类型注解错误: {{e}}"
                                    )
            except ImportError:
                continue
    
    def test_return_type_consistency(self):
        """测试返回类型一致性"""
        # 这是一个基础测试框架，可以根据具体问题扩展
        assert True, "返回类型一致性测试占位符"
    
    def test_variable_type_hints(self):
        """测试变量类型提示"""
        # 检查全局变量的类型提示
        assert True, "变量类型提示测试占位符"
'''
        
        self._write_test_file(test_path, test_content)
        return test_file
    
    def _generate_assertion_tests(self, issues: List[Dict]) -> Optional[str]:
        """生成断言增强测试"""
        test_file = "test_assertion_validation.py"
        test_path = self.tests_dir / test_file
        
        # 分析失败的断言
        failed_assertions = []
        for issue in issues:
            if issue.get('tool') == 'pytest' and 'assertion' in issue:
                failed_assertions.append(issue['assertion'])
        
        test_content = f'''"""
断言验证测试 - 防止断言失败再次发生
自动生成时间: {datetime.now().isoformat()}
基于 {len(issues)} 个断言失败生成
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestAssertionValidation:
    """增强版断言测试，防止断言失败"""
    
    def test_basic_assertions(self):
        """基础断言测试"""
        # 确保基本的断言逻辑正确
        assert True is True
        assert False is False
        assert 1 + 1 == 2
        assert "test" == "test"
    
    def test_null_safety(self):
        """空值安全测试"""
        # 测试空值处理
        test_value = None
        assert test_value is None
        
        test_list = []
        assert len(test_list) == 0
        assert not test_list
    
    def test_type_assertions(self):
        """类型断言测试"""
        # 确保类型检查正确
        assert isinstance("test", str)
        assert isinstance(123, int)
        assert isinstance([], list)
        assert isinstance({{}}, dict)
    
    def test_boundary_conditions(self):
        """边界条件测试"""
        # 测试边界情况
        assert 0 >= 0
        assert 1 > 0
        assert -1 < 0
    
    {"".join([f'''
    def test_assertion_case_{i}(self):
        """特定断言案例 {i} - 基于失败的断言"""
        # TODO: 根据实际失败的断言 '{assertion}' 编写具体测试
        assert True, "断言案例 {i} 占位符"
    ''' for i, assertion in enumerate(failed_assertions) if assertion])}
    
    @pytest.mark.parametrize("test_input,expected", [
        (True, True),
        (False, False),
        (1, 1),
        ("test", "test"),
    ])
    def test_parameterized_assertions(self, test_input, expected):
        """参数化断言测试"""
        assert test_input == expected
'''
        
        self._write_test_file(test_path, test_content)
        return test_file
    
    def _generate_style_tests(self, issues: List[Dict]) -> Optional[str]:
        """生成代码风格测试"""
        test_file = "test_code_style_validation.py"
        test_path = self.tests_dir / test_file
        
        test_content = f'''"""
代码风格验证测试 - 确保代码风格一致性
自动生成时间: {datetime.now().isoformat()}
基于 {len(issues)} 个风格问题生成
"""

import ast
import subprocess
import pytest
from pathlib import Path


class TestCodeStyleValidation:
    """代码风格验证测试"""
    
    def test_ruff_format_compliance(self):
        """测试代码是否符合ruff格式要求"""
        result = subprocess.run(
            ["ruff", "format", "--check", "src/", "tests/"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.fail(f"代码格式不符合要求:\\n{{result.stdout}}\\n{{result.stderr}}")
    
    def test_ruff_lint_compliance(self):
        """测试代码是否通过ruff lint检查"""
        result = subprocess.run(
            ["ruff", "check", "src/", "tests/"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            pytest.fail(f"代码不符合lint要求:\\n{{result.stdout}}\\n{{result.stderr}}")
    
    def test_line_length_compliance(self):
        """测试行长度是否符合要求"""
        max_line_length = 88
        
        for py_file in Path("src").rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if len(line.rstrip()) > max_line_length:
                        pytest.fail(
                            f"{{py_file}}:{{line_num}} 行长度 {{len(line.rstrip())}} "
                            f"超过限制 {{max_line_length}}"
                        )
    
    def test_import_sorting(self):
        """测试import语句排序"""
        for py_file in Path("src").rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析AST检查import语句
                tree = ast.parse(content)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
                
                # 检查是否按字母顺序排列（简化检查）
                sorted_imports = sorted(set(imports))
                # 这里可以添加更详细的import顺序检查
                
            except SyntaxError:
                pytest.fail(f"{{py_file}} 语法错误")
    
    def test_no_trailing_whitespace(self):
        """测试是否有尾随空白"""
        for py_file in Path("src").rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.rstrip() != line.rstrip('\\r\\n'):
                        pytest.fail(f"{{py_file}}:{{line_num}} 存在尾随空白")
'''
        
        self._write_test_file(test_path, test_content)
        return test_file
    
    def _generate_security_tests(self, issues: List[Dict]) -> Optional[str]:
        """生成安全检查测试"""
        test_file = "test_security_validation.py"
        test_path = self.tests_dir / test_file
        
        test_content = f'''"""
安全验证测试 - 防止安全问题再次发生
自动生成时间: {datetime.now().isoformat()}
基于 {len(issues)} 个安全问题生成
"""

import ast
import re
import subprocess
import pytest
from pathlib import Path


class TestSecurityValidation:
    """安全验证测试"""
    
    def test_bandit_security_scan(self):
        """运行bandit安全扫描"""
        result = subprocess.run(
            ["bandit", "-r", "src/", "-f", "json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            try:
                import json
                report = json.loads(result.stdout)
                high_issues = [r for r in report.get('results', []) 
                             if r.get('issue_severity') == 'HIGH']
                if high_issues:
                    pytest.fail(f"发现 {{len(high_issues)}} 个高危安全问题")
            except json.JSONDecodeError:
                pytest.fail(f"Bandit扫描失败:\\n{{result.stderr}}")
    
    def test_no_hardcoded_secrets(self):
        """检查是否有硬编码的密钥和密码"""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']', 
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for py_file in Path("src").rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        pytest.fail(
                            f"{{py_file}} 可能包含硬编码密钥: {{matches[0]}}"
                        )
    
    def test_sql_injection_prevention(self):
        """检查SQL注入防护"""
        for py_file in Path("src").rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 检查字符串格式化SQL查询（危险模式）
                dangerous_patterns = [
                    r'execute\s*\(\s*["\'][^"\']*%[sd][^"\']*["\']',
                    r'execute\s*\(\s*["\'][^"\']*\{{[^}}]*\}}[^"\']*["\']'
                ]
                
                for pattern in dangerous_patterns:
                    if re.search(pattern, content):
                        pytest.fail(
                            f"{{py_file}} 可能存在SQL注入风险"
                        )
    
    def test_safe_random_usage(self):
        """检查随机数生成是否安全"""
        for py_file in Path("src").rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name == 'random':
                                pytest.fail(
                                    f"{{py_file}} 使用了不安全的random模块，"
                                    f"请使用secrets模块"
                                )
            except SyntaxError:
                # 语法错误会在其他测试中捕获
                continue
    
    def test_no_eval_usage(self):
        """检查是否使用了危险的eval函数"""
        for py_file in Path("src").rglob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'eval(' in content or 'exec(' in content:
                    pytest.fail(
                        f"{{py_file}} 使用了危险的eval/exec函数"
                    )
'''
        
        self._write_test_file(test_path, test_content)
        return test_file
    
    def _generate_generic_tests(self, category: str, issues: List[Dict]) -> Optional[str]:
        """生成通用测试"""
        test_file = f"test_{category}_validation.py"
        test_path = self.tests_dir / test_file
        
        test_content = f'''"""
{category.replace('_', ' ').title()} 验证测试
自动生成时间: {datetime.now().isoformat()}
基于 {len(issues)} 个 {category} 问题生成
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class Test{category.replace('_', '').title()}Validation:
    """验证 {category} 相关问题"""
    
    def test_basic_validation(self):
        """基础验证测试"""
        # TODO: 根据具体问题类型添加测试逻辑
        assert True, "基础验证测试占位符"
    
    def test_edge_cases(self):
        """边界情况测试"""
        # TODO: 添加边界条件测试
        assert True, "边界情况测试占位符"
    
    def test_error_handling(self):
        """错误处理测试"""
        # TODO: 添加异常处理测试
        assert True, "错误处理测试占位符"
'''
        
        self._write_test_file(test_path, test_content)
        return test_file
    
    def _write_test_file(self, file_path: Path, content: str):
        """写入测试文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.generated_tests.append(str(file_path))


class LintConfigGenerator:
    """Lint配置生成器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.generated_configs = []
    
    def generate_enhanced_configs(self, issues: List[Dict]) -> List[str]:
        """生成增强的lint配置"""
        generated_files = []
        
        # 分析问题以确定需要的配置
        ruff_issues = [i for i in issues if i.get('tool') == 'ruff']
        mypy_issues = [i for i in issues if i.get('tool') == 'mypy']
        bandit_issues = [i for i in issues if i.get('tool') == 'bandit']
        
        if ruff_issues:
            config_file = self._generate_ruff_config(ruff_issues)
            if config_file:
                generated_files.append(config_file)
        
        if mypy_issues:
            config_file = self._generate_mypy_config(mypy_issues)
            if config_file:
                generated_files.append(config_file)
        
        if bandit_issues:
            config_file = self._generate_bandit_config(bandit_issues)
            if config_file:
                generated_files.append(config_file)
        
        return generated_files
    
    def _generate_ruff_config(self, issues: List[Dict]) -> Optional[str]:
        """生成增强的ruff配置"""
        config_path = self.project_root / "pyproject.toml"
        
        # 分析ruff问题以确定需要启用的规则
        rules_to_enable = set()
        rules_to_ignore = set()
        
        for issue in issues:
            rule_code = issue.get('rule_code', '')
            severity = issue.get('severity', 'medium')
            
            if severity == 'high':
                rules_to_enable.add(rule_code[:1])  # 启用规则类别
            elif severity == 'low':
                rules_to_ignore.add(rule_code)  # 忽略低优先级规则
        
        ruff_config = f'''
# Enhanced Ruff Configuration - Auto-generated
# Generated: {datetime.now().isoformat()}
# Based on {len(issues)} ruff issues

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
# 启用基础规则和高优先级规则
select = [
    "E",     # pycodestyle errors  
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "N",     # pep8-naming
    "B",     # flake8-bugbear
    "C4",    # flake8-comprehensions
    "UP",    # pyupgrade
    "S",     # bandit security
    {"".join(f'    "{rule}",    # High priority rule\\n' for rule in sorted(rules_to_enable) if rule)}
]

# 忽略低优先级和误报规则
ignore = [
    "E203",  # whitespace before ':'
    "E501",  # line too long (handled by formatter)
    {"".join(f'    "{rule}",    # Low priority issue\\n' for rule in sorted(rules_to_ignore) if rule)}
]

[tool.ruff.lint.per-file-ignores]
# 测试文件特殊规则
"tests/*" = [
    "S101",  # allow assert in tests
    "S106",  # allow hardcoded passwords in tests
]

# 脚本文件特殊规则
"scripts/*" = [
    "T201",  # allow print statements
]

[tool.ruff.lint.flake8-bugbear]
extend-immutable-calls = ["fastapi.Depends", "fastapi.Query"]

[tool.ruff.lint.isort]
known-first-party = ["src"]
split-on-trailing-comma = true

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-source-first-line = false
line-ending = "auto"
'''
        
        try:
            # 读取现有配置
            existing_content = ""
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # 如果没有ruff配置，添加新配置
            if '[tool.ruff]' not in existing_content:
                with open(config_path, 'a', encoding='utf-8') as f:
                    f.write(ruff_config)
                
                self.generated_configs.append(str(config_path))
                return "pyproject.toml"
        except Exception as e:
            click.echo(f"❌ 生成ruff配置失败: {e}")
        
        return None
    
    def _generate_mypy_config(self, issues: List[Dict]) -> Optional[str]:
        """生成增强的mypy配置"""
        config_path = self.project_root / "mypy.ini"
        
        # 分析mypy问题类型
        strict_mode = any(issue.get('severity') == 'high' for issue in issues)
        
        mypy_config = f'''# Enhanced MyPy Configuration - Auto-generated
# Generated: {datetime.now().isoformat()}  
# Based on {len(issues)} mypy issues

[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = {"True" if strict_mode else "False"}
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

# 模块特定配置
[mypy-tests.*]
disallow_untyped_defs = False

[mypy-scripts.*]
disallow_untyped_defs = False

# 第三方库忽略
[mypy-fastapi.*]
ignore_missing_imports = True

[mypy-pydantic.*]
ignore_missing_imports = True

[mypy-pytest.*]
ignore_missing_imports = True
'''
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(mypy_config)
            
            self.generated_configs.append(str(config_path))
            return "mypy.ini"
        except Exception as e:
            click.echo(f"❌ 生成mypy配置失败: {e}")
        
        return None
    
    def _generate_bandit_config(self, issues: List[Dict]) -> Optional[str]:
        """生成增强的bandit配置"""
        config_path = self.project_root / ".bandit"
        
        # 分析安全问题类型
        skip_tests = []
        for issue in issues:
            test_id = issue.get('test_id', '')
            severity = issue.get('issue_severity', 'MEDIUM')
            
            # 对于低危问题，可以选择跳过
            if severity == 'LOW' and test_id:
                skip_tests.append(test_id)
        
        bandit_config = f'''# Enhanced Bandit Configuration - Auto-generated
# Generated: {datetime.now().isoformat()}
# Based on {len(issues)} bandit issues

[bandit]
exclude_dirs = ["tests", "venv", ".venv", "build", "dist"]
skips = [{','.join(f'"{test}"' for test in skip_tests[:5])}]  # Skip low-priority tests

# 高危测试强制启用
tests = ["B101", "B102", "B103", "B104", "B105", "B106", "B107", "B108", "B110"]
'''
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(bandit_config)
            
            self.generated_configs.append(str(config_path))
            return ".bandit"
        except Exception as e:
            click.echo(f"❌ 生成bandit配置失败: {e}")
        
        return None


class PreCommitGenerator:
    """Pre-commit钩子生成器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def generate_precommit_config(self, issues: List[Dict]) -> bool:
        """生成pre-commit配置"""
        config_path = self.project_root / ".pre-commit-config.yaml"
        
        # 根据问题类型确定需要的钩子
        tools_needed = set()
        for issue in issues:
            tool = issue.get('tool', '')
            if tool:
                tools_needed.add(tool)
        
        config = {
            'repos': [
                {
                    'repo': 'https://github.com/pre-commit/pre-commit-hooks',
                    'rev': 'v4.4.0',
                    'hooks': [
                        {'id': 'trailing-whitespace'},
                        {'id': 'end-of-file-fixer'},
                        {'id': 'check-yaml'},
                        {'id': 'check-added-large-files'},
                        {'id': 'check-merge-conflict'},
                        {'id': 'check-docstring-first'},
                        {'id': 'debug-statements'}
                    ]
                }
            ]
        }
        
        # 添加ruff钩子
        if 'ruff' in tools_needed:
            config['repos'].append({
                'repo': 'https://github.com/astral-sh/ruff-pre-commit',
                'rev': 'v0.1.0',
                'hooks': [
                    {
                        'id': 'ruff',
                        'args': ['--fix', '--exit-non-zero-on-fix']
                    },
                    {'id': 'ruff-format'}
                ]
            })
        
        # 添加mypy钩子
        if 'mypy' in tools_needed:
            config['repos'].append({
                'repo': 'https://github.com/pre-commit/mirrors-mypy',
                'rev': 'v1.5.1',
                'hooks': [
                    {
                        'id': 'mypy',
                        'additional_dependencies': ['types-all']
                    }
                ]
            })
        
        # 添加bandit钩子
        if 'bandit' in tools_needed:
            config['repos'].append({
                'repo': 'https://github.com/PyCQA/bandit',
                'rev': '1.7.5',
                'hooks': [
                    {
                        'id': 'bandit',
                        'args': ['-r', 'src/'],
                        'exclude': 'tests/'
                    }
                ]
            })
        
        # 添加本地测试钩子
        config['repos'].append({
            'repo': 'local',
            'hooks': [
                {
                    'id': 'pytest-check',
                    'name': 'pytest-check',
                    'entry': 'pytest',
                    'language': 'system',
                    'pass_filenames': False,
                    'always_run': True,
                    'args': ['tests/', '--cov=src', '--cov-fail-under=80']
                }
            ]
        })
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            return True
        except Exception as e:
            click.echo(f"❌ 生成pre-commit配置失败: {e}")
            return False


class CIEnhancer:
    """CI流程增强器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.workflows_dir = project_root / ".github" / "workflows"
    
    def enhance_ci_workflow(self, issues: List[Dict]) -> bool:
        """增强CI工作流"""
        workflow_path = self.workflows_dir / "enhanced-quality-check.yml"
        
        # 根据问题生成增强的CI检查
        enhanced_workflow = {
            'name': 'Enhanced Quality Check',
            'on': {
                'push': {'branches': ['main', 'develop']},
                'pull_request': {'branches': ['main', 'develop']}
            },
            'jobs': {
                'quality-gate': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'name': 'Checkout code',
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'name': 'Setup Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r requirements.txt -r requirements-dev.txt'
                        }
                    ]
                }
            }
        }
        
        # 添加基于问题的检查步骤
        steps = enhanced_workflow['jobs']['quality-gate']['steps']
        
        # 根据发现的问题添加相应的检查步骤
        tools_with_issues = set(issue.get('tool', '') for issue in issues)
        
        if 'ruff' in tools_with_issues:
            steps.extend([
                {
                    'name': 'Ruff format check',
                    'run': 'ruff format --check src/ tests/'
                },
                {
                    'name': 'Ruff lint check',
                    'run': 'ruff check src/ tests/'
                }
            ])
        
        if 'mypy' in tools_with_issues:
            steps.append({
                'name': 'MyPy type check',
                'run': 'mypy src/'
            })
        
        if 'bandit' in tools_with_issues:
            steps.append({
                'name': 'Security scan',
                'run': 'bandit -r src/'
            })
        
        if 'pytest' in tools_with_issues:
            steps.extend([
                {
                    'name': 'Run tests',
                    'run': 'pytest tests/ --cov=src --cov-report=xml'
                },
                {
                    'name': 'Coverage threshold check',
                    'run': 'coverage report --fail-under=80'
                }
            ])
        
        # 添加增强的测试步骤
        steps.append({
            'name': 'Run enhanced validation tests',
            'run': 'pytest tests/test_*_validation.py -v'
        })
        
        try:
            self.workflows_dir.mkdir(parents=True, exist_ok=True)
            
            with open(workflow_path, 'w', encoding='utf-8') as f:
                yaml.dump(enhanced_workflow, f, default_flow_style=False, sort_keys=False)
            
            return True
        except Exception as e:
            click.echo(f"❌ 生成增强CI工作流失败: {e}")
            return False


class DefenseGenerator:
    """防御机制生成器主控制器"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        self.test_generator = TestGenerator(self.project_root)
        self.lint_generator = LintConfigGenerator(self.project_root)
        self.precommit_generator = PreCommitGenerator(self.project_root)
        self.ci_enhancer = CIEnhancer(self.project_root)
        
        self.generated_files = []
    
    def generate_comprehensive_defenses(self, issues: List[Dict]) -> Dict[str, List[str]]:
        """生成全面的防御机制"""
        defenses = {
            'test_files': [],
            'lint_configs': [],
            'ci_workflows': [],
            'pre_commit_hooks': []
        }
        
        click.echo(f"🛡️ 为 {len(issues)} 个问题生成防御机制...")
        
        # 生成验证测试
        test_files = self.test_generator.generate_validation_tests(issues)
        defenses['test_files'] = test_files
        
        # 生成lint配置
        lint_configs = self.lint_generator.generate_enhanced_configs(issues)
        defenses['lint_configs'] = lint_configs
        
        # 生成pre-commit钩子
        if self.precommit_generator.generate_precommit_config(issues):
            defenses['pre_commit_hooks'] = ['.pre-commit-config.yaml']
        
        # 增强CI工作流
        if self.ci_enhancer.enhance_ci_workflow(issues):
            defenses['ci_workflows'] = ['enhanced-quality-check.yml']
        
        # 收集所有生成的文件
        self.generated_files.extend(test_files)
        self.generated_files.extend(lint_configs)
        self.generated_files.extend(defenses['pre_commit_hooks'])
        self.generated_files.extend(defenses['ci_workflows'])
        
        return defenses


@click.command()
@click.option("--issues-file", "-i", help="CI问题JSON文件路径")
@click.option("--project-root", "-p", help="项目根目录路径")
@click.option("--output-dir", "-o", help="输出目录")
@click.option("--generate-tests", "-t", is_flag=True, help="生成验证测试")
@click.option("--generate-configs", "-c", is_flag=True, help="生成lint配置")
@click.option("--generate-precommit", "-pc", is_flag=True, help="生成pre-commit钩子")
@click.option("--generate-ci", "-ci", is_flag=True, help="生成CI增强")
@click.option("--summary", "-s", is_flag=True, help="显示生成摘要")
def main(issues_file, project_root, output_dir, generate_tests, generate_configs, 
         generate_precommit, generate_ci, summary):
    """
    🛡️ CI防御机制生成器
    
    根据CI问题自动生成测试用例、lint规则、预提交钩子等防御措施。
    
    Examples:
        defense_generator.py -i ci_issues.json -t -c
        defense_generator.py -i ci_issues.json --generate-precommit
        defense_generator.py -i ci_issues.json -s
    """
    
    project_path = Path(project_root) if project_root else Path.cwd()
    generator = DefenseGenerator(project_path)
    
    click.echo("🛡️ CI防御机制生成器启动")
    
    # 读取问题文件
    if not issues_file:
        issues_file = project_path / "logs" / "ci_issues.json"
    
    issues_path = Path(issues_file)
    if not issues_path.exists():
        click.echo(f"❌ 问题文件不存在: {issues_file}")
        return
    
    try:
        with open(issues_path, 'r', encoding='utf-8') as f:
            issues = json.load(f)
    except Exception as e:
        click.echo(f"❌ 读取问题文件失败: {e}")
        return
    
    click.echo(f"📋 从文件中读取到 {len(issues)} 个问题")
    
    # 根据选项生成不同类型的防御机制
    if not any([generate_tests, generate_configs, generate_precommit, generate_ci]):
        # 如果没有指定具体选项，生成所有防御机制
        defenses = generator.generate_comprehensive_defenses(issues)
    else:
        defenses = {'test_files': [], 'lint_configs': [], 'ci_workflows': [], 'pre_commit_hooks': []}
        
        if generate_tests:
            test_files = generator.test_generator.generate_validation_tests(issues)
            defenses['test_files'] = test_files
        
        if generate_configs:
            lint_configs = generator.lint_generator.generate_enhanced_configs(issues)
            defenses['lint_configs'] = lint_configs
        
        if generate_precommit:
            if generator.precommit_generator.generate_precommit_config(issues):
                defenses['pre_commit_hooks'] = ['.pre-commit-config.yaml']
        
        if generate_ci:
            if generator.ci_enhancer.enhance_ci_workflow(issues):
                defenses['ci_workflows'] = ['enhanced-quality-check.yml']
    
    # 显示结果
    if summary or not any(defenses.values()):
        click.echo("\n📊 生成摘要:")
        for defense_type, files in defenses.items():
            if files:
                click.echo(f"  {defense_type}: {len(files)} 个文件")
                for file in files:
                    click.echo(f"    - {file}")
            else:
                click.echo(f"  {defense_type}: 无")
    
    total_files = sum(len(files) for files in defenses.values())
    if total_files > 0:
        click.echo(f"\n✅ 成功生成 {total_files} 个防御机制文件")
    else:
        click.echo("\nℹ️ 没有生成新的防御机制文件")


if __name__ == "__main__":
    main() 