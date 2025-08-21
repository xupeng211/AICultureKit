"""
AI学习系统 - 模式类型定义

定义项目分析中使用的各种模式类型和数据结构。
"""

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ProjectPattern:
    """项目代码模式"""

    pattern_type: str  # 模式类型：naming, structure, style等
    pattern_name: str  # 模式名称
    pattern_value: Any  # 模式值
    confidence: float  # 置信度 (0-1)
    frequency: int  # 出现频率
    examples: List[str]  # 示例


@dataclass
class LearningResult:
    """学习结果"""

    project_maturity: str  # 项目成熟度：beginner, intermediate, expert
    recommended_strictness: float  # 推荐严格度 (0-1)
    patterns: List[ProjectPattern]  # 发现的模式
    custom_rules: Dict[str, Any]  # 生成的自定义规则
    team_preferences: Dict[str, Any]  # 团队偏好
    generated_at: float  # 生成时间戳


class PatternAnalyzer:
    """模式分析器基类"""

    def __init__(self):
        """初始化分析器"""
        self.patterns = []
        self.confidence_threshold = 0.6

    def analyze(self, data: Any) -> List[ProjectPattern]:
        """分析数据并返回模式"""
        raise NotImplementedError("子类必须实现analyze方法")

    def _calculate_confidence(self, frequency: int, total: int) -> float:
        """计算置信度"""
        if total == 0:
            return 0.0

        ratio = frequency / total

        # 使用sigmoid函数计算置信度
        import math

        confidence = 1 / (1 + math.exp(-5 * (ratio - 0.5)))

        return min(max(confidence, 0.0), 1.0)

    def _extract_examples(
        self, data: List[str], pattern_value: str, max_examples: int = 5
    ) -> List[str]:
        """提取模式示例"""
        examples = []
        for item in data:
            if pattern_value in str(item).lower():
                examples.append(item)
                if len(examples) >= max_examples:
                    break
        return examples


class NamingPatternAnalyzer(PatternAnalyzer):
    """命名模式分析器"""

    def analyze(self, names: List[str]) -> List[ProjectPattern]:
        """分析命名模式"""
        if not names:
            return []

        patterns = []

        # 分析命名风格
        snake_case_count = sum(1 for name in names if self._is_snake_case(name))
        camel_case_count = sum(1 for name in names if self._is_camel_case(name))
        pascal_case_count = sum(1 for name in names if self._is_pascal_case(name))

        total_names = len(names)

        # 确定主要命名风格
        if snake_case_count > camel_case_count and snake_case_count > pascal_case_count:
            confidence = self._calculate_confidence(snake_case_count, total_names)
            if confidence >= self.confidence_threshold:
                patterns.append(
                    ProjectPattern(
                        pattern_type="naming",
                        pattern_name="snake_case_preference",
                        pattern_value="snake_case",
                        confidence=confidence,
                        frequency=snake_case_count,
                        examples=self._extract_examples(names, "_"),
                    )
                )

        elif camel_case_count > pascal_case_count:
            confidence = self._calculate_confidence(camel_case_count, total_names)
            if confidence >= self.confidence_threshold:
                patterns.append(
                    ProjectPattern(
                        pattern_type="naming",
                        pattern_name="camel_case_preference",
                        pattern_value="camelCase",
                        confidence=confidence,
                        frequency=camel_case_count,
                        examples=self._extract_examples(
                            [n for n in names if self._is_camel_case(n)], ""
                        ),
                    )
                )

        elif pascal_case_count > 0:
            confidence = self._calculate_confidence(pascal_case_count, total_names)
            if confidence >= self.confidence_threshold:
                patterns.append(
                    ProjectPattern(
                        pattern_type="naming",
                        pattern_name="pascal_case_preference",
                        pattern_value="PascalCase",
                        confidence=confidence,
                        frequency=pascal_case_count,
                        examples=self._extract_examples(
                            [n for n in names if self._is_pascal_case(n)], ""
                        ),
                    )
                )

        return patterns

    def _is_snake_case(self, name: str) -> bool:
        """检查是否为snake_case"""
        return "_" in name and name.islower()

    def _is_camel_case(self, name: str) -> bool:
        """检查是否为camelCase"""
        return (name[0].islower() if name else False) and any(
            c.isupper() for c in name[1:]
        )

    def _is_pascal_case(self, name: str) -> bool:
        """检查是否为PascalCase"""
        return (name[0].isupper() if name else False) and any(
            c.isupper() for c in name[1:]
        )


class StructurePatternAnalyzer(PatternAnalyzer):
    """结构模式分析器"""

    def analyze(self, structure_data: Dict[str, Any]) -> List[ProjectPattern]:
        """分析项目结构模式"""
        patterns = []

        # 分析目录结构
        if "directories" in structure_data:
            directories = structure_data["directories"]

            # 检查是否有标准的Python项目结构
            standard_dirs = ["src", "tests", "docs", "scripts"]
            found_standard = sum(1 for d in standard_dirs if d in directories)

            if found_standard >= 2:
                confidence = self._calculate_confidence(
                    found_standard, len(standard_dirs)
                )
                patterns.append(
                    ProjectPattern(
                        pattern_type="structure",
                        pattern_name="standard_python_layout",
                        pattern_value="standard",
                        confidence=confidence,
                        frequency=found_standard,
                        examples=[d for d in standard_dirs if d in directories],
                    )
                )

        # 分析文件组织模式
        if "file_extensions" in structure_data:
            extensions = structure_data["file_extensions"]

            # 检查主要编程语言
            if ".py" in extensions and extensions[".py"] > 5:
                confidence = min(
                    extensions[".py"] / 20, 1.0
                )  # 20个以上Python文件认为是Python项目
                patterns.append(
                    ProjectPattern(
                        pattern_type="structure",
                        pattern_name="python_project",
                        pattern_value="python",
                        confidence=confidence,
                        frequency=extensions[".py"],
                        examples=[".py"],
                    )
                )

        return patterns


class StylePatternAnalyzer(PatternAnalyzer):
    """代码风格模式分析器"""

    def analyze(self, style_data: Dict[str, Any]) -> List[ProjectPattern]:
        """分析代码风格模式"""
        patterns = []

        # 分析引号偏好
        if "quote_usage" in style_data:
            single_quotes = style_data["quote_usage"].get("single", 0)
            double_quotes = style_data["quote_usage"].get("double", 0)
            total_quotes = single_quotes + double_quotes

            if total_quotes > 0:
                if single_quotes > double_quotes:
                    confidence = self._calculate_confidence(single_quotes, total_quotes)
                    patterns.append(
                        ProjectPattern(
                            pattern_type="style",
                            pattern_name="quote_preference",
                            pattern_value="single",
                            confidence=confidence,
                            frequency=single_quotes,
                            examples=["'string'"],
                        )
                    )
                else:
                    confidence = self._calculate_confidence(double_quotes, total_quotes)
                    patterns.append(
                        ProjectPattern(
                            pattern_type="style",
                            pattern_name="quote_preference",
                            pattern_value="double",
                            confidence=confidence,
                            frequency=double_quotes,
                            examples=['"string"'],
                        )
                    )

        # 分析缩进偏好
        if "indentation" in style_data:
            spaces = style_data["indentation"].get("spaces", 0)
            tabs = style_data["indentation"].get("tabs", 0)
            total_indent = spaces + tabs

            if total_indent > 0:
                if spaces > tabs:
                    confidence = self._calculate_confidence(spaces, total_indent)
                    patterns.append(
                        ProjectPattern(
                            pattern_type="style",
                            pattern_name="indentation_preference",
                            pattern_value="spaces",
                            confidence=confidence,
                            frequency=spaces,
                            examples=["4 spaces"],
                        )
                    )
                else:
                    confidence = self._calculate_confidence(tabs, total_indent)
                    patterns.append(
                        ProjectPattern(
                            pattern_type="style",
                            pattern_name="indentation_preference",
                            pattern_value="tabs",
                            confidence=confidence,
                            frequency=tabs,
                            examples=["tabs"],
                        )
                    )

        return patterns


class DocumentationPatternAnalyzer(PatternAnalyzer):
    """文档模式分析器"""

    def analyze(self, doc_data: Dict[str, Any]) -> List[ProjectPattern]:
        """分析文档模式"""
        patterns = []

        # 分析文档字符串风格
        if "docstring_style" in doc_data:
            styles = doc_data["docstring_style"]
            total_docstrings = sum(styles.values())

            if total_docstrings > 0:
                # 找出最常用的文档字符串风格
                most_common_style = max(styles.items(), key=lambda x: x[1])
                style_name, count = most_common_style

                confidence = self._calculate_confidence(count, total_docstrings)
                if confidence >= self.confidence_threshold:
                    patterns.append(
                        ProjectPattern(
                            pattern_type="documentation",
                            pattern_name="docstring_style",
                            pattern_value=style_name,
                            confidence=confidence,
                            frequency=count,
                            examples=[f'"""{style_name} style docstring"""'],
                        )
                    )

        # 分析文档覆盖率
        if "coverage" in doc_data:
            coverage = doc_data["coverage"]

            if coverage > 0.7:  # 70%以上覆盖率
                patterns.append(
                    ProjectPattern(
                        pattern_type="documentation",
                        pattern_name="high_documentation_coverage",
                        pattern_value="high",
                        confidence=coverage,
                        frequency=int(coverage * 100),
                        examples=["Well documented functions and classes"],
                    )
                )

        return patterns
