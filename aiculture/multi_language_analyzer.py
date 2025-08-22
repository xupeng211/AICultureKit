"""
多语言代码分析器 - 支持Python之外的其他编程语言。

目前支持的语言：
- JavaScript/TypeScript
- 未来计划：Java, Go, Rust, C#等
"""

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LanguagePattern:
    """语言特定的代码模式"""

    language: str
    pattern_type: str  # naming, style, structure等
    pattern_name: str  # 模式名称
    pattern_value: Any  # 模式值
    confidence: float  # 置信度
    examples: List[str]  # 示例代码


@dataclass
class LanguageMetrics:
    """语言特定的代码指标"""

    language: str
    file_count: int
    total_lines: int
    avg_function_size: float
    avg_complexity: float
    naming_consistency: float
    style_consistency: float
    patterns: List[LanguagePattern]


class LanguageAnalyzer(ABC):
    """语言分析器抽象基类"""

    def __init__(self, project_path: Path) -> None:
        """初始化语言分析器"""
        self.project_path = project_path
        self.patterns: List[LanguagePattern] = []

    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""

    @abstractmethod
    def get_language_name(self) -> str:
        """获取语言名称"""

    @abstractmethod
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个文件"""

    @abstractmethod
    def extract_patterns(self, file_analysis: List[Dict[str, Any]]) -> List[LanguagePattern]:
        """从文件分析结果中提取模式"""

    def analyze_project(self) -> LanguageMetrics:
        """分析整个项目的该语言代码"""
        file_analyses = []

        # 找到所有相关文件
        for ext in self.get_file_extensions():
            for file_path in self.project_path.rglob(f"*{ext}"):
                if self._should_skip_file(file_path):
                    continue

                try:
                    analysis = self.analyze_file(file_path)
                    if analysis:
                        analysis["file_path"] = str(file_path)
                        file_analyses.append(analysis)
                except Exception:
                    continue  # 跳过分析失败的文件

        if not file_analyses:
            return LanguageMetrics(
                language=self.get_language_name(),
                file_count=0,
                total_lines=0,
                avg_function_size=0,
                avg_complexity=0,
                naming_consistency=0,
                style_consistency=0,
                patterns=[],
            )

        # 聚合分析结果
        return self._aggregate_analysis(file_analyses)

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            "node_modules",
            ".git",
            "dist",
            "build",
            ".cache",
            "coverage",
            ".nyc_output",
            "lib",
            "out",
            "target",
        ]

        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _aggregate_analysis(self, file_analyses: List[Dict[str, Any]]) -> LanguageMetrics:
        """聚合多个文件的分析结果"""
        total_lines = sum(analysis.get("line_count", 0) for analysis in file_analyses)
        total_functions = sum(analysis.get("function_count", 0) for analysis in file_analyses)
        total_function_lines = sum(
            analysis.get("total_function_lines", 0) for analysis in file_analyses
        )

        complexities = []
        for analysis in file_analyses:
            complexities.extend(analysis.get("complexities", []))

        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        avg_function_size = total_function_lines / total_functions if total_functions > 0 else 0

        # 计算命名一致性
        naming_consistency = self._calculate_naming_consistency(file_analyses)

        # 计算风格一致性
        style_consistency = self._calculate_style_consistency(file_analyses)

        # 提取模式
        patterns = self.extract_patterns(file_analyses)

        return LanguageMetrics(
            language=self.get_language_name(),
            file_count=len(file_analyses),
            total_lines=total_lines,
            avg_function_size=avg_function_size,
            avg_complexity=avg_complexity,
            naming_consistency=naming_consistency,
            style_consistency=style_consistency,
            patterns=patterns,
        )

    def _calculate_naming_consistency(self, file_analyses: List[Dict[str, Any]]) -> float:
        """计算命名一致性"""
        # 这是一个通用实现，子类可以重写
        all_names = []
        for analysis in file_analyses:
            all_names.extend(analysis.get("function_names", []))
            all_names.extend(analysis.get("variable_names", []))
            all_names.extend(analysis.get("class_names", []))

        if not all_names:
            return 0.0

        # 简单的启发式：检查camelCase vs snake_case一致性
        camel_case_count = sum(1 for name in all_names if re.match(r"^[a-z][a-zA-Z0-9]*$", name))
        snake_case_count = sum(1 for name in all_names if re.match(r"^[a-z][a-z0-9_]*$", name))
        pascal_case_count = sum(1 for name in all_names if re.match(r"^[A-Z][a-zA-Z0-9]*$", name))

        total = len(all_names)
        max_style_count = max(camel_case_count, snake_case_count, pascal_case_count)

        return max_style_count / total if total > 0 else 0.0

    def _calculate_style_consistency(self, file_analyses: List[Dict[str, Any]]) -> float:
        """计算风格一致性"""
        # 这是一个通用实现，子类可以重写
        if not file_analyses:
            return 0.0

        # 简单的风格一致性指标
        total_score = 0
        total_checks = 0

        # 检查缩进一致性
        indent_styles = []
        for analysis in file_analyses:
            if "indent_style" in analysis:
                indent_styles.append(analysis["indent_style"])

        if indent_styles:
            most_common_indent = max(set(indent_styles), key=indent_styles.count)
            indent_consistency = indent_styles.count(most_common_indent) / len(indent_styles)
            total_score += indent_consistency
            total_checks += 1

        # 检查引号使用一致性
        quote_styles = []
        for analysis in file_analyses:
            if "quote_style" in analysis:
                quote_styles.append(analysis["quote_style"])

        if quote_styles:
            most_common_quote = max(set(quote_styles), key=quote_styles.count)
            quote_consistency = quote_styles.count(most_common_quote) / len(quote_styles)
            total_score += quote_consistency
            total_checks += 1

        return total_score / total_checks if total_checks > 0 else 0.0


class JavaScriptTypeScriptAnalyzer(LanguageAnalyzer):
    """JavaScript/TypeScript代码分析器"""

    def get_file_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""
        return [".js", ".jsx", ".ts", ".tsx"]

    def get_language_name(self) -> str:
        """获取语言名称"""
        return "JavaScript/TypeScript"

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """分析单个JavaScript/TypeScript文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            analysis = {
                "file_path": str(file_path),
                "line_count": len(content.splitlines()),
                "function_count": 0,
                "total_function_lines": 0,
                "complexities": [],
                "function_names": [],
                "variable_names": [],
                "class_names": [],
                "indent_style": self._detect_indent_style(content),
                "quote_style": self._detect_quote_style(content),
                "import_style": self._detect_import_style(content),
                "features": self._detect_language_features(content, file_path.suffix),
            }

            # 分析函数
            functions = self._extract_functions(content)
            analysis["function_count"] = len(functions)

            for func in functions:
                analysis["function_names"].append(func["name"])
                analysis["total_function_lines"] += func["lines"]
                analysis["complexities"].append(func["complexity"])

            # 分析变量和类
            analysis["variable_names"] = self._extract_variables(content)
            analysis["class_names"] = self._extract_classes(content)

            return analysis

        except (UnicodeDecodeError, IOError):
            return {}

    def _detect_indent_style(self, content: str) -> str:
        """检测缩进风格"""
        lines = content.splitlines()
        tab_count = 0
        space_count = 0

        for line in lines:
            if line.startswith("\t"):
                tab_count += 1
            elif line.startswith("  "):  # 2个或更多空格
                space_count += 1

        return "tabs" if tab_count > space_count else "spaces"

    def _detect_quote_style(self, content: str) -> str:
        """检测引号风格"""
        single_quotes = len(re.findall(r"'[^']*'", content))
        double_quotes = len(re.findall(r'"[^"]*"', content))
        template_literals = len(re.findall(r"`[^`]*`", content))

        if template_literals > max(single_quotes, double_quotes):
            return "template_literals"
        elif single_quotes > double_quotes:
            return "single"
        else:
            return "double"

    def _detect_import_style(self, content: str) -> str:
        """检测导入风格"""
        es6_imports = len(re.findall(r'import\s+.*\s+from\s+[\'"`]', content))
        require_imports = len(re.findall(r'require\s*\(\s*[\'"`]', content))

        return "es6" if es6_imports > require_imports else "commonjs"

    def _detect_language_features(self, content: str, file_extension: str) -> Dict[str, bool]:
        """检测语言特性使用情况"""
        features = {
            "typescript": file_extension in [".ts", ".tsx"],
            "jsx": file_extension in [".jsx", ".tsx"],
            "arrow_functions": "arrow_functions" in content or "=>" in content,
            "async_await": "async " in content and "await " in content,
            "destructuring": re.search(r"const\s*{.*}\s*=", content) is not None,
            "template_literals": "`" in content,
            "classes": "class " in content,
            "modules": "import " in content or "export " in content,
        }

        # TypeScript特性检测
        if features["typescript"]:
            features.update(
                {
                    "type_annotations": ":" in content
                    and ("string" in content or "number" in content),
                    "interfaces": "interface " in content,
                    "generics": "<" in content and ">" in content,
                    "enums": "enum " in content,
                }
            )

        return features

    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """提取函数信息"""
        functions = []

        # 匹配各种函数定义模式
        patterns = [
            r"function\s+(\w+)\s*\([^)]*\)\s*{",  # function declaration
            r"(\w+)\s*:\s*function\s*\([^)]*\)\s*{",  # method definition
            r"(\w+)\s*=\s*function\s*\([^)]*\)\s*{",  # function expression
            r"(\w+)\s*=\s*\([^)]*\)\s*=>\s*{",  # arrow function with block
            r"(\w+)\s*=\s*\([^)]*\)\s*=>",  # arrow function
            r"async\s+function\s+(\w+)\s*\([^)]*\)\s*{",  # async function
            r"async\s+(\w+)\s*\([^)]*\)\s*{",  # async method
        ]

        lines = content.splitlines()

        for pattern in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                func_name = match.group(1)
                start_line = content[: match.start()].count("\n")

                # 估算函数长度和复杂度
                func_lines = self._estimate_function_size(content, match.start(), lines)
                complexity = self._calculate_js_complexity(content, match.start(), func_lines)

                functions.append(
                    {
                        "name": func_name,
                        "lines": func_lines,
                        "complexity": complexity,
                        "start_line": start_line,
                    }
                )

        return functions

    def _extract_variables(self, content: str) -> List[str]:
        """提取变量名"""
        variables = []

        # 匹配变量声明
        patterns = [
            r"(?:var|let|const)\s+(\w+)",  # 变量声明
            r"(\w+)\s*=\s*(?:new\s+\w+|function|\()",  # 赋值
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                var_name = match.group(1)
                if var_name and not var_name[0].isupper():  # 排除类名
                    variables.append(var_name)

        return list(set(variables))  # 去重

    def _extract_classes(self, content: str) -> List[str]:
        """提取类名"""
        classes = []

        # 匹配类定义
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, content):
            classes.append(match.group(1))

        return classes

    def _estimate_function_size(self, content: str, start_pos: int, lines: List[str]) -> int:
        """估算函数大小（行数）"""
        # 简单实现：从函数开始位置向下查找匹配的大括号
        brace_count = 0
        in_function = False
        func_lines = 0

        # 从函数开始位置开始计算
        start_line = content[:start_pos].count("\n")

        for i, line in enumerate(lines[start_line:], start_line):
            if "{" in line:
                brace_count += line.count("{")
                in_function = True
            if "}" in line:
                brace_count -= line.count("}")

            if in_function:
                func_lines += 1

            if in_function and brace_count == 0:
                break

        return func_lines

    def _calculate_js_complexity(self, content: str, start_pos: int, func_lines: int) -> int:
        """计算JavaScript函数的复杂度"""
        # 提取函数内容
        start_line = content[:start_pos].count("\n")
        lines = content.splitlines()
        func_content = "\n".join(lines[start_line : start_line + func_lines])

        complexity = 1  # 基础复杂度

        # 计算复杂度因子
        complexity += len(re.findall(r"\bif\b", func_content))
        complexity += len(re.findall(r"\belse\b", func_content))
        complexity += len(re.findall(r"\bwhile\b", func_content))
        complexity += len(re.findall(r"\bfor\b", func_content))
        complexity += len(re.findall(r"\bswitch\b", func_content))
        complexity += len(re.findall(r"\bcatch\b", func_content))
        complexity += len(re.findall(r"\b\?\s*.*\s*:", func_content))  # 三元操作符
        complexity += len(re.findall(r"&&|\|\|", func_content))  # 逻辑操作符

        return complexity

    def extract_patterns(self, file_analyses: List[Dict[str, Any]]) -> List[LanguagePattern]:
        """从文件分析结果中提取JavaScript/TypeScript模式"""
        patterns = []

        if not file_analyses:
            return patterns

        # 分析命名模式
        all_function_names = []
        all_variable_names = []
        all_class_names = []

        for analysis in file_analyses:
            all_function_names.extend(analysis.get("function_names", []))
            all_variable_names.extend(analysis.get("variable_names", []))
            all_class_names.extend(analysis.get("class_names", []))

        # 函数命名模式
        if all_function_names:
            func_naming_style = self._detect_naming_pattern(all_function_names)
            if func_naming_style:
                patterns.append(
                    LanguagePattern(
                        language=self.get_language_name(),
                        pattern_type="naming",
                        pattern_name="function_naming_style",
                        pattern_value=func_naming_style["style"],
                        confidence=func_naming_style["confidence"],
                        examples=func_naming_style["examples"][:3],
                    )
                )

        # 变量命名模式
        if all_variable_names:
            var_naming_style = self._detect_naming_pattern(all_variable_names)
            if var_naming_style:
                patterns.append(
                    LanguagePattern(
                        language=self.get_language_name(),
                        pattern_type="naming",
                        pattern_name="variable_naming_style",
                        pattern_value=var_naming_style["style"],
                        confidence=var_naming_style["confidence"],
                        examples=var_naming_style["examples"][:3],
                    )
                )

        # 引号使用模式
        quote_styles = [analysis.get("quote_style") for analysis in file_analyses]
        quote_styles = [style for style in quote_styles if style]
        if quote_styles:
            most_common_quote = max(set(quote_styles), key=quote_styles.count)
            confidence = quote_styles.count(most_common_quote) / len(quote_styles)
            if confidence > 0.6:
                patterns.append(
                    LanguagePattern(
                        language=self.get_language_name(),
                        pattern_type="style",
                        pattern_name="quote_preference",
                        pattern_value=most_common_quote,
                        confidence=confidence,
                        examples=[],
                    )
                )

        # 导入风格模式
        import_styles = [analysis.get("import_style") for analysis in file_analyses]
        import_styles = [style for style in import_styles if style]
        if import_styles:
            most_common_import = max(set(import_styles), key=import_styles.count)
            confidence = import_styles.count(most_common_import) / len(import_styles)
            if confidence > 0.6:
                patterns.append(
                    LanguagePattern(
                        language=self.get_language_name(),
                        pattern_type="style",
                        pattern_name="import_style",
                        pattern_value=most_common_import,
                        confidence=confidence,
                        examples=[],
                    )
                )

        # 语言特性使用模式
        feature_usage = {}
        for analysis in file_analyses:
            features = analysis.get("features", {})
            for feature, used in features.items():
                if feature not in feature_usage:
                    feature_usage[feature] = []
                feature_usage[feature].append(used)

        for feature, usage_list in feature_usage.items():
            usage_rate = sum(usage_list) / len(usage_list)
            if usage_rate > 0.5:  # 超过50%的文件使用该特性
                patterns.append(
                    LanguagePattern(
                        language=self.get_language_name(),
                        pattern_type="feature",
                        pattern_name=f"{feature}_usage",
                        pattern_value=usage_rate,
                        confidence=usage_rate,
                        examples=[],
                    )
                )

        return patterns

    def _detect_naming_pattern(self, names: List[str]) -> Optional[Dict[str, Any]]:
        """检测命名模式"""
        if not names:
            return None

        patterns = {
            "camelCase": 0,
            "PascalCase": 0,
            "snake_case": 0,
            "kebab-case": 0,
            "UPPER_CASE": 0,
        }

        examples = {
            "camelCase": [],
            "PascalCase": [],
            "snake_case": [],
            "kebab-case": [],
            "UPPER_CASE": [],
        }

        for name in names:
            if re.match(r"^[a-z][a-zA-Z0-9]*$", name):
                patterns["camelCase"] += 1
                if len(examples["camelCase"]) < 3:
                    examples["camelCase"].append(name)
            elif re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
                patterns["PascalCase"] += 1
                if len(examples["PascalCase"]) < 3:
                    examples["PascalCase"].append(name)
            elif re.match(r"^[a-z][a-z0-9_]*$", name):
                patterns["snake_case"] += 1
                if len(examples["snake_case"]) < 3:
                    examples["snake_case"].append(name)
            elif re.match(r"^[a-z][a-z0-9-]*$", name):
                patterns["kebab-case"] += 1
                if len(examples["kebab-case"]) < 3:
                    examples["kebab-case"].append(name)
            elif re.match(r"^[A-Z][A-Z0-9_]*$", name):
                patterns["UPPER_CASE"] += 1
                if len(examples["UPPER_CASE"]) < 3:
                    examples["UPPER_CASE"].append(name)

        # 找出主导模式
        total_names = len(names)
        max_count = 0
        dominant_style = None

        for style, count in patterns.items():
            if count > max_count:
                max_count = count
                dominant_style = style

        if max_count == 0:
            return None

        confidence = max_count / total_names

        return {
            "style": dominant_style,
            "confidence": confidence,
            "examples": examples[dominant_style],
        }


class MultiLanguageManager:
    """多语言管理器 - 协调不同语言的分析器"""

    def __init__(self, project_path: Path) -> None:
        """初始化多语言管理器"""
        self.project_path = project_path
        self.analyzers = {
            "javascript": JavaScriptTypeScriptAnalyzer(project_path),
            # 未来可以添加更多语言分析器
            # 'java': JavaAnalyzer(project_path),
            # 'go': GoAnalyzer(project_path),
        }

    def analyze_all_languages(self) -> Dict[str, LanguageMetrics]:
        """分析项目中所有支持的语言"""
        results = {}

        for language_key, analyzer in self.analyzers.items():
            try:
                metrics = analyzer.analyze_project()
                if metrics.file_count > 0:  # 只包含有文件的语言
                    results[language_key] = metrics
            except Exception as e:
                # 分析某种语言失败时继续处理其他语言
                print(f"分析 {language_key} 时出错: {e}")
                continue

        return results

    def get_project_language_summary(self) -> Dict[str, Any]:
        """获取项目语言使用总结"""
        language_metrics = self.analyze_all_languages()

        total_files = sum(metrics.file_count for metrics in language_metrics.values())
        total_lines = sum(metrics.total_lines for metrics in language_metrics.values())

        summary = {
            "total_languages": len(language_metrics),
            "total_files": total_files,
            "total_lines": total_lines,
            "language_distribution": {},
            "language_metrics": language_metrics,
        }

        # 计算语言分布
        for language, metrics in language_metrics.items():
            summary["language_distribution"][language] = {
                "file_percentage": (
                    (metrics.file_count / total_files * 100) if total_files > 0 else 0
                ),
                "line_percentage": (
                    (metrics.total_lines / total_lines * 100) if total_lines > 0 else 0
                ),
                "file_count": metrics.file_count,
                "line_count": metrics.total_lines,
            }

        return summary

    def get_cross_language_patterns(self) -> List[Dict[str, Any]]:
        """获取跨语言的模式对比"""
        language_metrics = self.analyze_all_languages()
        cross_patterns = []

        # 比较命名风格一致性
        naming_styles = {}
        for language, metrics in language_metrics.items():
            for pattern in metrics.patterns:
                if pattern.pattern_type == "naming":
                    if pattern.pattern_name not in naming_styles:
                        naming_styles[pattern.pattern_name] = {}
                    naming_styles[pattern.pattern_name][language] = pattern.pattern_value

        for pattern_name, language_styles in naming_styles.items():
            if len(language_styles) > 1:  # 多种语言都有这个模式
                cross_patterns.append(
                    {
                        "type": "naming_consistency",
                        "pattern": pattern_name,
                        "languages": language_styles,
                        "consistent": len(set(language_styles.values())) == 1,
                    }
                )

        # 比较代码复杂度
        complexity_comparison = {}
        for language, metrics in language_metrics.items():
            complexity_comparison[language] = metrics.avg_complexity

        if complexity_comparison:
            cross_patterns.append(
                {
                    "type": "complexity_comparison",
                    "languages": complexity_comparison,
                    "avg_complexity": sum(complexity_comparison.values())
                    / len(complexity_comparison),
                }
            )

        return cross_patterns


def save_multi_language_analysis(analysis_result: Dict[str, Any], project_path: Path) -> None:
    """保存多语言分析结果"""
    result_file = project_path / ".aiculture" / "multi_language_analysis.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # 转换dataclass为dict
        serializable_result = {}
        for key, value in analysis_result.items():
            if isinstance(value, LanguageMetrics):
                serializable_result[key] = {
                    "language": value.language,
                    "file_count": value.file_count,
                    "total_lines": value.total_lines,
                    "avg_function_size": value.avg_function_size,
                    "avg_complexity": value.avg_complexity,
                    "naming_consistency": value.naming_consistency,
                    "style_consistency": value.style_consistency,
                    "patterns": [
                        {
                            "language": p.language,
                            "pattern_type": p.pattern_type,
                            "pattern_name": p.pattern_name,
                            "pattern_value": p.pattern_value,
                            "confidence": p.confidence,
                            "examples": p.examples,
                        }
                        for p in value.patterns
                    ],
                }
            else:
                serializable_result[key] = value

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(serializable_result, f, indent=2, default=str)

    except (IOError, TypeError):
        pass  # 保存失败时忽略


def load_multi_language_analysis(project_path: Path) -> Optional[Dict[str, Any]]:
    """加载多语言分析结果"""
    result_file = project_path / ".aiculture" / "multi_language_analysis.json"

    try:
        if result_file.exists():
            with open(result_file, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass

    return None
