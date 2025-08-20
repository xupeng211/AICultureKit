"""
文化原则强制执行器

自动检查和强制执行开发文化原则，确保所有代码都符合标准。
"""

import ast
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from .ai_culture_principles import AICulturePrinciples, PrincipleCategory


@dataclass
class Violation:
    """违规记录"""
    principle: str
    severity: str  # error, warning, info
    file_path: str
    line_number: int
    description: str
    suggestion: str


class CultureEnforcer:
    """文化原则强制执行器"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.principles = AICulturePrinciples()
        self.violations: List[Violation] = []
    
    def enforce_all(self) -> Dict[str, Any]:
        """执行所有原则检查"""
        self.violations.clear()
        
        # 检查项目结构
        self._check_project_structure()
        
        # 检查代码质量
        self._check_code_quality()
        
        # 检查安全问题
        self._check_security()
        
        # 检查测试覆盖率
        self._check_test_coverage()
        
        # 检查文档完整性
        self._check_documentation()
        
        return self._generate_report()
    
    def _check_project_structure(self):
        """检查项目结构是否符合标准"""
        required_files = [
            "README.md",
            ".gitignore",
            "requirements.txt",  # 或 pyproject.toml
            ".pre-commit-config.yaml"
        ]
        
        for file_name in required_files:
            if not (self.project_path / file_name).exists():
                self.violations.append(Violation(
                    principle="project_structure",
                    severity="error",
                    file_path=file_name,
                    line_number=0,
                    description=f"缺少必要文件: {file_name}",
                    suggestion=f"创建 {file_name} 文件"
                ))
        
        # 检查测试目录
        if not (self.project_path / "tests").exists():
            self.violations.append(Violation(
                principle="testing",
                severity="warning",
                file_path="tests/",
                line_number=0,
                description="缺少测试目录",
                suggestion="创建 tests/ 目录并添加测试用例"
            ))
    
    def _check_code_quality(self):
        """检查代码质量原则"""
        python_files = list(self.project_path.rglob("*.py"))
        
        for file_path in python_files:
            if "venv" in str(file_path) or ".git" in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查SOLID原则
                self._check_solid_principles(file_path, content)
                
                # 检查DRY原则
                self._check_dry_principle(file_path, content)
                
                # 检查KISS原则
                self._check_kiss_principle(file_path, content)
                
            except Exception as e:
                print(f"无法分析文件 {file_path}: {e}")
    
    def _check_solid_principles(self, file_path: Path, content: str):
        """检查SOLID原则"""
        try:
            tree = ast.parse(content)
            
            # 检查单一职责原则
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 10:  # 简单的启发式规则
                        self.violations.append(Violation(
                            principle="solid_srp",
                            severity="warning",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description=f"类 {node.name} 可能违反单一职责原则 (方法数: {len(methods)})",
                            suggestion="考虑将类拆分为更小的、职责单一的类"
                        ))
        
        except SyntaxError:
            pass  # 跳过语法错误的文件
    
    def _check_dry_principle(self, file_path: Path, content: str):
        """检查DRY原则"""
        lines = content.split('\n')
        line_counts = {}
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 20:
                if line in line_counts:
                    line_counts[line].append(i)
                else:
                    line_counts[line] = [i]
        
        # 检查重复代码
        for line, occurrences in line_counts.items():
            if len(occurrences) >= 3:  # 出现3次以上认为是重复
                self.violations.append(Violation(
                    principle="dry",
                    severity="warning", 
                    file_path=str(file_path),
                    line_number=occurrences[0],
                    description=f"检测到重复代码: '{line[:50]}...'",
                    suggestion="考虑将重复代码提取为函数或常量"
                ))
    
    def _check_kiss_principle(self, file_path: Path, content: str):
        """检查KISS原则"""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查函数复杂度
                    complexity = self._calculate_complexity(node)
                    if complexity > 10:  # 圈复杂度阈值
                        self.violations.append(Violation(
                            principle="kiss",
                            severity="warning",
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description=f"函数 {node.name} 复杂度过高 (复杂度: {complexity})",
                            suggestion="考虑将函数拆分为更小的函数"
                        ))
        
        except SyntaxError:
            pass
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数的圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _check_security(self):
        """检查安全问题"""
        try:
            # 使用bandit进行安全检查
            result = subprocess.run(
                ["bandit", "-r", str(self.project_path), "-f", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                import json
                bandit_results = json.loads(result.stdout)
                
                for issue in bandit_results.get('results', []):
                    self.violations.append(Violation(
                        principle="security",
                        severity=issue['issue_severity'].lower(),
                        file_path=issue['filename'],
                        line_number=issue['line_number'],
                        description=issue['issue_text'],
                        suggestion=f"查看bandit文档: {issue['test_id']}"
                    ))
        
        except FileNotFoundError:
            # bandit未安装
            pass
        except Exception:
            # 其他错误
            pass 
    
    def _check_test_coverage(self):
        """检查测试覆盖率"""
        try:
            # 运行pytest获取覆盖率
            result = subprocess.run(
                ["pytest", "--cov=.", "--cov-report=json", "--quiet"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            coverage_file = self.project_path / "coverage.json"
            if coverage_file.exists():
                import json
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data['totals']['percent_covered']
                if total_coverage < 80:
                    self.violations.append(Violation(
                        principle="testing",
                        severity="warning",
                        file_path="overall",
                        line_number=0,
                        description=f"测试覆盖率不足: {total_coverage:.1f}%",
                        suggestion="添加更多测试用例以达到80%覆盖率"
                    ))
        
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    
    def _check_documentation(self):
        """检查文档完整性"""
        readme_path = self.project_path / "README.md"
        
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_sections = [
                "installation", "install", "安装",
                "usage", "使用", "example", "示例"
            ]
            
            content_lower = content.lower()
            missing_sections = []
            
            for section in required_sections:
                if section not in content_lower:
                    missing_sections.append(section)
            
            if len(missing_sections) == len(required_sections):
                self.violations.append(Violation(
                    principle="documentation",
                    severity="warning",
                    file_path="README.md",
                    line_number=0,
                    description="README.md缺少安装和使用说明",
                    suggestion="添加安装指南和使用示例"
                ))
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成检查报告"""
        errors = [v for v in self.violations if v.severity == "error"]
        warnings = [v for v in self.violations if v.severity == "warning"]
        
        # 按原则分组
        by_principle = {}
        for violation in self.violations:
            if violation.principle not in by_principle:
                by_principle[violation.principle] = []
            by_principle[violation.principle].append(violation)
        
        # 计算质量分数
        score = max(0, 100 - len(errors) * 15 - len(warnings) * 5)
        
        return {
            "score": score,
            "total_violations": len(self.violations),
            "errors": len(errors),
            "warnings": len(warnings),
            "by_principle": by_principle,
            "violations": [
                {
                    "principle": v.principle,
                    "severity": v.severity,
                    "file": v.file_path,
                    "line": v.line_number,
                    "description": v.description,
                    "suggestion": v.suggestion
                }
                for v in self.violations
            ]
        }
    
    def generate_fix_suggestions(self) -> List[str]:
        """生成修复建议"""
        suggestions = []
        
        # 按严重程度排序
        sorted_violations = sorted(
            self.violations,
            key=lambda x: 0 if x.severity == "error" else 1
        )
        
        for violation in sorted_violations:
            suggestions.append(
                f"📁 {violation.file_path}:{violation.line_number}\n"
                f"🔴 {violation.principle.upper()}: {violation.description}\n"
                f"💡 建议: {violation.suggestion}\n"
            )
        
        return suggestions


def enforce_culture_in_project(project_path: str = ".") -> Dict[str, Any]:
    """在项目中强制执行文化原则"""
    enforcer = CultureEnforcer(project_path)
    return enforcer.enforce_all() 