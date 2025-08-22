#!/usr/bin/env python3
"""架构设计分析工具"""

import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ArchitectureIssue:
    """架构问题"""

    file_path: str
    issue_type: str
    severity: str
    description: str
    suggestion: str
    details: dict[str, Any] = None


class ArchitectureAnalyzer:
    """架构分析器"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.issues = []
        self.dependencies = defaultdict(set)  # 简化的依赖图
        self.module_info = {}

    def analyze_architecture(self) -> dict[str, Any]:
        """分析项目架构"""
        print("🏗️ 开始架构设计分析...")

        # 1. 分析模块依赖关系
        self._analyze_dependencies()

        # 2. 检查循环依赖
        self._check_circular_dependencies()

        # 3. 分析模块耦合度
        self._analyze_coupling()

        # 4. 检查单一职责原则
        self._check_single_responsibility()

        # 5. 分析接口设计
        self._analyze_interfaces()

        # 6. 检查依赖倒置
        self._check_dependency_inversion()

        return self._generate_architecture_report()

    def _analyze_dependencies(self):
        """分析模块依赖关系"""
        python_files = list(self.project_path.rglob("*.py"))

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)

                module_name = self._get_module_name(file_path)
                imports = self._extract_imports(tree)

                self.module_info[module_name] = {
                    "file_path": str(file_path),
                    "imports": imports,
                    "classes": self._extract_classes(tree),
                    "functions": self._extract_functions(tree),
                    "lines_of_code": len(content.split("\n")),
                }

                # 构建依赖关系
                for imported_module in imports:
                    if imported_module.startswith("aiculture"):
                        self.dependencies[module_name].add(imported_module)

            except (SyntaxError, UnicodeDecodeError):
                continue

    def _check_circular_dependencies(self):
        """检查循环依赖（简化版本）"""
        # 简单的循环依赖检查
        for module_a in self.dependencies:
            for module_b in self.dependencies[module_a]:
                if (
                    module_b in self.dependencies
                    and module_a in self.dependencies[module_b]
                ):
                    # 发现双向依赖
                    self.issues.append(
                        ArchitectureIssue(
                            file_path=f"{module_a} <-> {module_b}",
                            issue_type="circular_dependency",
                            severity="high",
                            description=f"发现循环依赖: {module_a} <-> {module_b}",
                            suggestion="重构代码以消除循环依赖，考虑使用依赖注入或接口抽象",
                            details={"modules": [module_a, module_b]},
                        ),
                    )

    def _analyze_coupling(self):
        """分析模块耦合度"""
        for module_name, info in self.module_info.items():
            # 计算传入耦合（被多少模块依赖）
            fan_in = len(
                [
                    m
                    for m in self.module_info.keys()
                    if module_name in self.module_info[m]["imports"]
                ],
            )

            # 计算传出耦合（依赖多少模块）
            fan_out = len(
                [imp for imp in info["imports"] if imp.startswith("aiculture")],
            )

            # 高耦合警告
            if fan_out > 10:
                self.issues.append(
                    ArchitectureIssue(
                        file_path=info["file_path"],
                        issue_type="high_coupling",
                        severity="medium",
                        description=f"模块 {module_name} 依赖过多模块 ({fan_out})",
                        suggestion="考虑拆分模块或使用依赖注入减少耦合",
                        details={"fan_out": fan_out, "fan_in": fan_in},
                    ),
                )

            if fan_in > 15:
                self.issues.append(
                    ArchitectureIssue(
                        file_path=info["file_path"],
                        issue_type="high_fan_in",
                        severity="medium",
                        description=f"模块 {module_name} 被过多模块依赖 ({fan_in})",
                        suggestion="考虑拆分模块或提取公共接口",
                        details={"fan_out": fan_out, "fan_in": fan_in},
                    ),
                )

    def _check_single_responsibility(self):
        """检查单一职责原则"""
        for _module_name, info in self.module_info.items():
            classes = info["classes"]
            info["functions"]

            # 检查类的职责
            for class_info in classes:
                methods = class_info["methods"]
                if len(methods) > 20:
                    self.issues.append(
                        ArchitectureIssue(
                            file_path=info["file_path"],
                            issue_type="too_many_responsibilities",
                            severity="medium",
                            description=f"类 {class_info['name']} 方法过多 ({len(methods)})，可能违反单一职责原则",
                            suggestion="考虑将类拆分为多个更小的类",
                            details={
                                "class_name": class_info["name"],
                                "method_count": len(methods),
                            },
                        ),
                    )

                # 检查方法名的一致性（判断职责是否单一）
                method_verbs = []
                for method in methods:
                    if "_" in method:
                        verb = method.split("_")[0]
                        method_verbs.append(verb)

                if len(set(method_verbs)) > 5:  # 动词种类过多
                    self.issues.append(
                        ArchitectureIssue(
                            file_path=info["file_path"],
                            issue_type="mixed_responsibilities",
                            severity="low",
                            description=f"类 {class_info['name']} 的方法涉及多种操作类型",
                            suggestion="考虑按功能职责重新组织类的方法",
                            details={
                                "class_name": class_info["name"],
                                "verb_types": list(set(method_verbs)),
                            },
                        ),
                    )

    def _analyze_interfaces(self):
        """分析接口设计"""
        for _module_name, info in self.module_info.items():
            classes = info["classes"]

            for class_info in classes:
                # 检查是否有抽象基类
                if class_info["name"].endswith("Base") or class_info["name"].startswith(
                    "Abstract",
                ):
                    # 检查是否有抽象方法
                    abstract_methods = [
                        m for m in class_info["methods"] if m.startswith("_")
                    ]
                    if len(abstract_methods) == 0:
                        self.issues.append(
                            ArchitectureIssue(
                                file_path=info["file_path"],
                                issue_type="missing_abstract_methods",
                                severity="low",
                                description=f"抽象类 {class_info['name']} 没有抽象方法",
                                suggestion="为抽象类添加抽象方法或重新考虑类的设计",
                                details={"class_name": class_info["name"]},
                            ),
                        )

                # 检查公共接口的一致性
                public_methods = [
                    m for m in class_info["methods"] if not m.startswith("_")
                ]
                if len(public_methods) > 15:
                    self.issues.append(
                        ArchitectureIssue(
                            file_path=info["file_path"],
                            issue_type="large_interface",
                            severity="medium",
                            description=f"类 {class_info['name']} 公共接口过大 ({len(public_methods)} 个方法)",
                            suggestion="考虑拆分接口或使用组合模式",
                            details={
                                "class_name": class_info["name"],
                                "public_method_count": len(public_methods),
                            },
                        ),
                    )

    def _check_dependency_inversion(self):
        """检查依赖倒置原则"""
        for module_name, info in self.module_info.items():
            imports = info["imports"]

            # 检查是否直接依赖具体实现而非抽象
            concrete_dependencies = []
            for imp in imports:
                if imp.startswith("aiculture"):
                    # 简单启发式：如果导入的模块名包含具体实现的词汇
                    concrete_indicators = [
                        "manager",
                        "handler",
                        "processor",
                        "executor",
                        "worker",
                    ]
                    if any(
                        indicator in imp.lower() for indicator in concrete_indicators
                    ):
                        concrete_dependencies.append(imp)

            if len(concrete_dependencies) > 5:
                self.issues.append(
                    ArchitectureIssue(
                        file_path=info["file_path"],
                        issue_type="concrete_dependency",
                        severity="low",
                        description=f"模块 {module_name} 依赖过多具体实现",
                        suggestion="考虑引入抽象接口，依赖抽象而非具体实现",
                        details={"concrete_dependencies": concrete_dependencies},
                    ),
                )

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否跳过文件"""
        skip_dirs = {"venv", "__pycache__", ".git", "node_modules", ".pytest_cache"}
        return any(part in skip_dirs for part in file_path.parts)

    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名"""
        relative_path = file_path.relative_to(self.project_path)
        return (
            str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")
        )

    def _extract_imports(self, tree: ast.AST) -> list[str]:
        """提取导入信息"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _extract_classes(self, tree: ast.AST) -> list[dict[str, Any]]:
        """提取类信息"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append(
                    {
                        "name": node.name,
                        "methods": methods,
                        "base_classes": [
                            base.id for base in node.bases if isinstance(base, ast.Name)
                        ],
                    },
                )
        return classes

    def _extract_functions(self, tree: ast.AST) -> list[str]:
        """提取函数信息"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not isinstance(
                node.parent if hasattr(node, "parent") else None,
                ast.ClassDef,
            ):
                functions.append(node.name)
        return functions

    def _generate_architecture_report(self) -> dict[str, Any]:
        """生成架构分析报告"""
        # 按严重程度分组
        by_severity = defaultdict(list)
        for issue in self.issues:
            by_severity[issue.severity].append(issue)

        # 按类型分组
        by_type = defaultdict(list)
        for issue in self.issues:
            by_type[issue.issue_type].append(issue)

        # 计算架构指标
        total_modules = len(self.module_info)
        total_dependencies = sum(len(deps) for deps in self.dependencies.values())
        avg_coupling = total_dependencies / max(total_modules, 1)

        return {
            "total_issues": len(self.issues),
            "by_severity": dict(by_severity),
            "by_type": dict(by_type),
            "metrics": {
                "total_modules": total_modules,
                "total_dependencies": total_dependencies,
                "average_coupling": avg_coupling,
                "circular_dependencies": len(
                    [i for i in self.issues if i.issue_type == "circular_dependency"],
                ),
            },
            "summary": {
                "high_severity": len(by_severity["high"]),
                "medium_severity": len(by_severity["medium"]),
                "low_severity": len(by_severity["low"]),
            },
        }


def main():
    """主函数"""
    analyzer = ArchitectureAnalyzer(Path())
    report = analyzer.analyze_architecture()

    print("\n🏗️ 架构设计分析报告")
    print("=" * 50)

    metrics = report["metrics"]
    summary = report["summary"]

    print(f"总模块数: {metrics['total_modules']}")
    print(f"总依赖关系: {metrics['total_dependencies']}")
    print(f"平均耦合度: {metrics['average_coupling']:.2f}")
    print(f"循环依赖: {metrics['circular_dependencies']} 个")
    print()

    print(f"架构问题总数: {report['total_issues']}")
    print(f"高严重性: {summary['high_severity']} 个")
    print(f"中等严重性: {summary['medium_severity']} 个")
    print(f"低严重性: {summary['low_severity']} 个")
    print()

    print("🔍 按问题类型分组:")
    for issue_type, issues in report["by_type"].items():
        print(f"  {issue_type}: {len(issues)} 个")

    print("\n🚨 高严重性问题详情:")
    high_issues = report["by_severity"].get("high", [])
    for i, issue in enumerate(high_issues[:5], 1):
        print(f"  {i}. {issue.file_path}")
        print(f"     {issue.description}")
        print(f"     建议: {issue.suggestion}")
        print()

    if len(high_issues) > 5:
        print(f"  ... 还有 {len(high_issues) - 5} 个高严重性问题")

    return report


if __name__ == "__main__":
    main()
