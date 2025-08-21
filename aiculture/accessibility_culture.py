"""
可访问性文化模块 - 无障碍设计、国际化支持、多设备兼容性

提供：
1. 无障碍设计检查 (WCAG 2.1)
2. 国际化支持验证 (i18n)
3. 多设备兼容性测试
4. 可访问性最佳实践
5. 自动化可访问性测试
"""

import json
import re
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class AccessibilityLevel(Enum):
    """可访问性级别 (WCAG)"""

    A = "A"
    AA = "AA"
    AAA = "AAA"


class AccessibilityCategory(Enum):
    """可访问性类别"""

    PERCEIVABLE = "perceivable"
    OPERABLE = "operable"
    UNDERSTANDABLE = "understandable"
    ROBUST = "robust"


class DeviceType(Enum):
    """设备类型"""

    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"
    TV = "tv"
    WATCH = "watch"


@dataclass
class AccessibilityIssue:
    """可访问性问题"""

    rule_id: str
    severity: str  # error, warning, info
    category: AccessibilityCategory
    level: AccessibilityLevel
    description: str
    file_path: str
    line_number: int
    element: str
    recommendation: str
    wcag_reference: str


@dataclass
class I18nIssue:
    """国际化问题"""

    issue_type: str  # hardcoded_text, missing_translation, locale_format
    severity: str
    description: str
    file_path: str
    line_number: int
    text_content: str
    recommendation: str


@dataclass
class ResponsiveIssue:
    """响应式设计问题"""

    issue_type: str  # viewport, breakpoint, touch_target, font_size
    severity: str
    description: str
    file_path: str
    line_number: int
    device_type: DeviceType
    recommendation: str


class AccessibilityChecker:
    """无障碍设计检查器"""

    def __init__(self):
        """__init__函数"""
        # HTML可访问性规则
        self.html_rules = {
            "missing_alt_text": {
                "pattern": r"<img(?![^>]*alt=)[^>]*>",
                "severity": "error",
                "category": AccessibilityCategory.PERCEIVABLE,
                "level": AccessibilityLevel.A,
                "description": "图片缺少alt属性",
                "recommendation": "为所有图片添加描述性的alt属性",
                "wcag_reference": "WCAG 2.1 SC 1.1.1",
            },
            "missing_form_labels": {
                "pattern": r'<input(?![^>]*(?:aria-label|aria-labelledby))(?![^>]*id="[^"]*")(?![^>]*type="(?:hidden|submit|button)")[^>]*>',
                "severity": "error",
                "category": AccessibilityCategory.PERCEIVABLE,
                "level": AccessibilityLevel.A,
                "description": "表单输入缺少标签",
                "recommendation": "为表单输入添加label或aria-label",
                "wcag_reference": "WCAG 2.1 SC 1.3.1",
            },
            "missing_heading_structure": {
                "pattern": r"<h([1-6])[^>]*>",
                "severity": "warning",
                "category": AccessibilityCategory.PERCEIVABLE,
                "level": AccessibilityLevel.AA,
                "description": "标题结构可能不正确",
                "recommendation": "确保标题按层级顺序使用",
                "wcag_reference": "WCAG 2.1 SC 1.3.1",
            },
            "low_contrast": {
                "pattern": r"color:\s*#([0-9a-fA-F]{3,6})",
                "severity": "warning",
                "category": AccessibilityCategory.PERCEIVABLE,
                "level": AccessibilityLevel.AA,
                "description": "可能存在对比度不足",
                "recommendation": "确保文本与背景对比度至少为4.5:1",
                "wcag_reference": "WCAG 2.1 SC 1.4.3",
            },
            "missing_focus_indicators": {
                "pattern": r"outline:\s*(?:none|0)",
                "severity": "error",
                "category": AccessibilityCategory.OPERABLE,
                "level": AccessibilityLevel.AA,
                "description": "移除了焦点指示器",
                "recommendation": "提供清晰的焦点指示器",
                "wcag_reference": "WCAG 2.1 SC 2.4.7",
            },
            "missing_skip_links": {
                "pattern": r"<nav[^>]*>",
                "severity": "warning",
                "category": AccessibilityCategory.OPERABLE,
                "level": AccessibilityLevel.A,
                "description": "可能缺少跳转链接",
                "recommendation": "添加跳转到主内容的链接",
                "wcag_reference": "WCAG 2.1 SC 2.4.1",
            },
        }

        # React/JSX特定规则
        self.jsx_rules = {
            "missing_jsx_alt": {
                "pattern": r"<img(?![^>]*alt=)[^/>]*(?:/>|>[^<]*</img>)",
                "severity": "error",
                "category": AccessibilityCategory.PERCEIVABLE,
                "level": AccessibilityLevel.A,
                "description": "JSX图片组件缺少alt属性",
                "recommendation": "为img组件添加alt属性",
                "wcag_reference": "WCAG 2.1 SC 1.1.1",
            },
            "missing_jsx_labels": {
                "pattern": r"<input(?![^>]*(?:aria-label|aria-labelledby))[^/>]*(?:/>|>[^<]*</input>)",
                "severity": "error",
                "category": AccessibilityCategory.PERCEIVABLE,
                "level": AccessibilityLevel.A,
                "description": "JSX输入组件缺少标签",
                "recommendation": "添加htmlFor属性或aria-label",
                "wcag_reference": "WCAG 2.1 SC 1.3.1",
            },
        }

    def check_html_file(self, file_path: Path) -> List[AccessibilityIssue]:
        """检查HTML文件的可访问性"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            # 检查HTML规则
            for rule_id, rule in self.html_rules.items():
                matches = re.finditer(
                    rule["pattern"], content, re.IGNORECASE | re.MULTILINE
                )

                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    issue = AccessibilityIssue(
                        rule_id=rule_id,
                        severity=rule["severity"],
                        category=rule["category"],
                        level=rule["level"],
                        description=rule["description"],
                        file_path=str(file_path),
                        line_number=line_num,
                        element=match.group(0)[:100],
                        recommendation=rule["recommendation"],
                        wcag_reference=rule["wcag_reference"],
                    )
                    issues.append(issue)

            # 检查标题层级
            issues.extend(self._check_heading_hierarchy(content, str(file_path)))

        except Exception as e:
            print(f"检查文件 {file_path} 时出错: {e}")

        return issues

    def check_jsx_file(self, file_path: Path) -> List[AccessibilityIssue]:
        """检查JSX文件的可访问性"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查JSX规则
            for rule_id, rule in self.jsx_rules.items():
                matches = re.finditer(
                    rule["pattern"], content, re.IGNORECASE | re.MULTILINE
                )

                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    issue = AccessibilityIssue(
                        rule_id=rule_id,
                        severity=rule["severity"],
                        category=rule["category"],
                        level=rule["level"],
                        description=rule["description"],
                        file_path=str(file_path),
                        line_number=line_num,
                        element=match.group(0)[:100],
                        recommendation=rule["recommendation"],
                        wcag_reference=rule["wcag_reference"],
                    )
                    issues.append(issue)

        except Exception as e:
            print(f"检查JSX文件 {file_path} 时出错: {e}")

        return issues

    def _check_heading_hierarchy(
        self, content: str, file_path: str
    ) -> List[AccessibilityIssue]:
        """检查标题层级结构"""
        issues = []
        heading_pattern = r"<h([1-6])[^>]*>"
        headings = []

        for match in re.finditer(heading_pattern, content, re.IGNORECASE):
            level = int(match.group(1))
            line_num = content[: match.start()].count("\n") + 1
            headings.append((level, line_num, match.group(0)))

        # 检查层级跳跃
        for i in range(1, len(headings)):
            current_level, current_line, current_element = headings[i]
            prev_level = headings[i - 1][0]

            if current_level > prev_level + 1:
                issue = AccessibilityIssue(
                    rule_id="heading_hierarchy_skip",
                    severity="warning",
                    category=AccessibilityCategory.PERCEIVABLE,
                    level=AccessibilityLevel.AA,
                    description=f"标题层级跳跃：从h{prev_level}跳到h{current_level}",
                    file_path=file_path,
                    line_number=current_line,
                    element=current_element[:100],
                    recommendation="按顺序使用标题层级，不要跳级",
                    wcag_reference="WCAG 2.1 SC 1.3.1",
                )
                issues.append(issue)

        return issues


class InternationalizationChecker:
    """国际化检查器"""

    def __init__(self):
        """__init__函数"""
        # 硬编码文本模式
        self.hardcoded_text_patterns = [
            r'["\']([A-Za-z\s]{3,})["\']',  # 引号中的英文文本
            r'placeholder=["\']([^"\']+)["\']',  # placeholder属性
            r'title=["\']([^"\']+)["\']',  # title属性
            r'alt=["\']([^"\']+)["\']',  # alt属性
        ]

        # 常见的非国际化字符串
        self.common_hardcoded = [
            "Click here",
            "Submit",
            "Cancel",
            "OK",
            "Yes",
            "No",
            "Login",
            "Logout",
            "Sign up",
            "Sign in",
            "Register",
            "Home",
            "About",
            "Contact",
            "Help",
            "Settings",
            "Error",
            "Warning",
            "Success",
            "Info",
            "Loading",
        ]

        # 日期/时间格式模式
        self.datetime_patterns = [
            r"\d{1,2}/\d{1,2}/\d{4}",  # MM/DD/YYYY
            r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
            r"\d{1,2}:\d{2}:\d{2}",  # HH:MM:SS
        ]

    def _check_hardcoded_text_in_line(
        self, line: str, line_num: int, file_path: Path
    ) -> List[I18nIssue]:
        """检查单行中的硬编码文本"""
        issues = []

        for pattern in self.hardcoded_text_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                text = match.group(1)

                # 检查是否是常见的硬编码文本
                if text in self.common_hardcoded or len(text.split()) > 2:
                    issue = I18nIssue(
                        issue_type="hardcoded_text",
                        severity="warning",
                        description=f'发现硬编码文本: "{text}"',
                        file_path=str(file_path),
                        line_number=line_num,
                        text_content=text,
                        recommendation="使用国际化函数如t()或i18n.get()",
                    )
                    issues.append(issue)

        return issues

    def _check_datetime_format_in_line(
        self, line: str, line_num: int, file_path: Path
    ) -> List[I18nIssue]:
        """检查单行中的日期时间格式"""
        issues = []

        for pattern in self.datetime_patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                issue = I18nIssue(
                    issue_type="locale_format",
                    severity="info",
                    description=f"发现硬编码日期格式: {match.group(0)}",
                    file_path=str(file_path),
                    line_number=line_num,
                    text_content=match.group(0),
                    recommendation="使用locale.strftime()或国际化日期格式",
                )
                issues.append(issue)

        return issues

    def check_file(self, file_path: Path) -> List[I18nIssue]:
        """检查文件的国际化问题"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            # 检查硬编码文本
            for line_num, line in enumerate(lines, 1):
                # 跳过注释和导入语句
                if line.strip().startswith(("#", "//", "/*", "import", "from")):
                    continue

                # 检查硬编码文本
                hardcoded_issues = self._check_hardcoded_text_in_line(
                    line, line_num, file_path
                )
                issues.extend(hardcoded_issues)

                # 检查日期时间格式
                datetime_issues = self._check_datetime_format_in_line(
                    line, line_num, file_path
                )
                issues.extend(datetime_issues)

        except Exception as e:
            print(f"检查国际化文件 {file_path} 时出错: {e}")

        return issues

    def _collect_translation_keys(
        self, obj: Dict[str, Any], prefix: str = ""
    ) -> Set[str]:
        """收集翻译键"""
        keys = set()
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.add(full_key)
                if isinstance(value, dict):
                    keys.update(self._collect_translation_keys(value, full_key))
        return keys

    def _load_translation_files(
        self, locale_dir: Path
    ) -> Tuple[Dict[str, Dict], Set[str]]:
        """加载所有翻译文件"""
        translation_files = {}
        base_keys = set()

        for json_file in locale_dir.glob("*.json"):
            locale = json_file.stem
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    translations = json.load(f)
                    translation_files[locale] = translations

                    keys = self._collect_translation_keys(translations)
                    if not base_keys:
                        base_keys = keys

            except Exception as e:
                print(f"读取翻译文件 {json_file} 时出错: {e}")

        return translation_files, base_keys

    def _find_missing_translations(
        self, translation_files: Dict[str, Dict], base_keys: Set[str]
    ) -> Dict[str, List[str]]:
        """查找缺失的翻译"""
        missing_translations = {}

        for locale, translations in translation_files.items():
            locale_keys = self._collect_translation_keys(translations)
            missing = base_keys - locale_keys

            if missing:
                missing_translations[locale] = list(missing)

        return missing_translations

    def _calculate_completeness_rates(
        self,
        translation_files: Dict[str, Dict],
        base_keys: Set[str],
        missing_translations: Dict[str, List[str]],
    ) -> Dict[str, float]:
        """计算完整性比率"""
        return {
            locale: (len(base_keys) - len(missing_translations.get(locale, [])))
            / len(base_keys)
            * 100
            for locale in translation_files.keys()
        }

    def check_translation_completeness(self, locale_dir: Path) -> Dict[str, Any]:
        """检查翻译完整性"""
        if not locale_dir.exists():
            return {"error": "本地化目录不存在"}

        # 加载翻译文件
        translation_files, base_keys = self._load_translation_files(locale_dir)

        # 查找缺失的翻译
        missing_translations = self._find_missing_translations(
            translation_files, base_keys
        )

        # 计算完整性比率
        completeness_rate = self._calculate_completeness_rates(
            translation_files, base_keys, missing_translations
        )

        return {
            "total_locales": len(translation_files),
            "total_keys": len(base_keys),
            "missing_translations": missing_translations,
            "completeness_rate": completeness_rate,
        }


class ResponsiveDesignChecker:
    """响应式设计检查器"""

    def __init__(self):
        """__init__函数"""
        self.css_rules = {
            "missing_viewport": {
                "pattern": r'<meta\s+name=["\']viewport["\']',
                "severity": "error",
                "description": "缺少viewport meta标签",
                "recommendation": '添加<meta name="viewport" content="width=device-width, initial-scale=1">',
            },
            "fixed_width": {
                "pattern": r"width:\s*\d+px",
                "severity": "warning",
                "description": "使用固定宽度可能影响响应式设计",
                "recommendation": "考虑使用相对单位如%、em、rem或vw",
            },
            "small_touch_target": {
                "pattern": r"(?:width|height):\s*(?:[1-3]?\d)px",
                "severity": "warning",
                "description": "触摸目标可能过小",
                "recommendation": "确保触摸目标至少44x44px",
            },
            "missing_media_queries": {
                "pattern": r"@media\s*\([^)]*\)",
                "severity": "info",
                "description": "检查媒体查询使用情况",
                "recommendation": "使用媒体查询适配不同设备",
            },
        }

    def check_css_file(self, file_path: Path) -> List[ResponsiveIssue]:
        """检查CSS文件的响应式设计"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for rule_id, rule in self.css_rules.items():
                matches = re.finditer(rule["pattern"], content, re.IGNORECASE)

                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1

                    # 根据规则类型确定设备类型
                    device_type = DeviceType.MOBILE
                    if "width" in match.group(0):
                        device_type = DeviceType.DESKTOP

                    issue = ResponsiveIssue(
                        issue_type=rule_id,
                        severity=rule["severity"],
                        description=rule["description"],
                        file_path=str(file_path),
                        line_number=line_num,
                        device_type=device_type,
                        recommendation=rule["recommendation"],
                    )
                    issues.append(issue)

        except Exception as e:
            print(f"检查CSS文件 {file_path} 时出错: {e}")

        return issues

    def check_html_file(self, file_path: Path) -> List[ResponsiveIssue]:
        """检查HTML文件的响应式设计"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查viewport meta标签
            if not re.search(
                r'<meta\s+name=["\']viewport["\']', content, re.IGNORECASE
            ):
                issue = ResponsiveIssue(
                    issue_type="missing_viewport",
                    severity="error",
                    description="缺少viewport meta标签",
                    file_path=str(file_path),
                    line_number=1,
                    device_type=DeviceType.MOBILE,
                    recommendation="在<head>中添加viewport meta标签",
                )
                issues.append(issue)

        except Exception as e:
            print(f"检查HTML文件 {file_path} 时出错: {e}")

        return issues


class AccessibilityCultureManager:
    """可访问性文化管理器"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.accessibility_checker = AccessibilityChecker()
        self.i18n_checker = InternationalizationChecker()
        self.responsive_checker = ResponsiveDesignChecker()

    def scan_project_accessibility(self) -> Dict[str, Any]:
        """扫描项目可访问性"""
        all_issues = []
        file_count = 0

        # 扫描HTML文件
        for html_file in self.project_path.rglob("*.html"):
            if self._should_skip_file(html_file):
                continue

            file_count += 1
            issues = self.accessibility_checker.check_html_file(html_file)
            all_issues.extend(issues)

        # 扫描JSX文件
        for jsx_file in self.project_path.rglob("*.jsx"):
            if self._should_skip_file(jsx_file):
                continue

            file_count += 1
            issues = self.accessibility_checker.check_jsx_file(jsx_file)
            all_issues.extend(issues)

        # 按严重程度和类别分组
        by_severity = {"error": [], "warning": [], "info": []}
        by_category = {cat.value: [] for cat in AccessibilityCategory}

        for issue in all_issues:
            by_severity[issue.severity].append(issue)
            by_category[issue.category.value].append(issue)

        return {
            "total_files_scanned": file_count,
            "total_issues": len(all_issues),
            "by_severity": by_severity,
            "by_category": by_category,
            "wcag_compliance": self._calculate_wcag_compliance(all_issues),
            "recommendations": self._generate_accessibility_recommendations(all_issues),
        }

    def scan_project_i18n(self) -> Dict[str, Any]:
        """扫描项目国际化"""
        all_issues = []
        file_count = 0

        # 扫描代码文件
        for ext in ["*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.html"]:
            for file_path in self.project_path.rglob(ext):
                if self._should_skip_file(file_path):
                    continue

                file_count += 1
                issues = self.i18n_checker.check_file(file_path)
                all_issues.extend(issues)

        # 检查翻译完整性
        locale_dir = self.project_path / "locales"
        translation_completeness = self.i18n_checker.check_translation_completeness(
            locale_dir
        )

        # 按类型分组
        by_type = {}
        for issue in all_issues:
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type].append(issue)

        return {
            "total_files_scanned": file_count,
            "total_issues": len(all_issues),
            "by_type": by_type,
            "translation_completeness": translation_completeness,
            "recommendations": self._generate_i18n_recommendations(
                all_issues, translation_completeness
            ),
        }

    def scan_project_responsive(self) -> Dict[str, Any]:
        """扫描项目响应式设计"""
        all_issues = []
        file_count = 0

        # 扫描CSS文件
        for css_file in self.project_path.rglob("*.css"):
            if self._should_skip_file(css_file):
                continue

            file_count += 1
            issues = self.responsive_checker.check_css_file(css_file)
            all_issues.extend(issues)

        # 扫描HTML文件
        for html_file in self.project_path.rglob("*.html"):
            if self._should_skip_file(html_file):
                continue

            issues = self.responsive_checker.check_html_file(html_file)
            all_issues.extend(issues)

        # 按设备类型分组
        by_device = {device.value: [] for device in DeviceType}
        for issue in all_issues:
            by_device[issue.device_type.value].append(issue)

        return {
            "total_files_scanned": file_count,
            "total_issues": len(all_issues),
            "by_device": by_device,
            "recommendations": self._generate_responsive_recommendations(all_issues),
        }

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合可访问性报告"""
        accessibility_scan = self.scan_project_accessibility()
        i18n_scan = self.scan_project_i18n()
        responsive_scan = self.scan_project_responsive()

        total_issues = (
            accessibility_scan["total_issues"]
            + i18n_scan["total_issues"]
            + responsive_scan["total_issues"]
        )

        # 计算总体评分
        accessibility_score = max(0, 100 - accessibility_scan["total_issues"] * 5)
        i18n_score = max(0, 100 - i18n_scan["total_issues"] * 3)
        responsive_score = max(0, 100 - responsive_scan["total_issues"] * 4)

        overall_score = (accessibility_score + i18n_score + responsive_score) / 3

        return {
            "timestamp": time.time(),
            "overall_score": overall_score,
            "total_issues": total_issues,
            "accessibility": accessibility_scan,
            "internationalization": i18n_scan,
            "responsive_design": responsive_scan,
            "priority_actions": [
                f"修复 {accessibility_scan['by_severity']['error']} 个可访问性错误",
                f"处理 {i18n_scan['total_issues']} 个国际化问题",
                f"优化 {responsive_scan['total_issues']} 个响应式设计问题",
                "实施自动化可访问性测试",
                "建立多语言内容管理流程",
            ],
        }

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否跳过文件"""
        return any(
            part.startswith(".")
            or part in ["node_modules", "venv", "__pycache__", "build", "dist"]
            for part in file_path.parts
        )

    def _calculate_wcag_compliance(
        self, issues: List[AccessibilityIssue]
    ) -> Dict[str, Any]:
        """计算WCAG合规性"""
        level_counts = {level.value: 0 for level in AccessibilityLevel}

        for issue in issues:
            if issue.severity == "error":
                level_counts[issue.level.value] += 1

        return {
            "level_a_violations": level_counts["A"],
            "level_aa_violations": level_counts["AA"],
            "level_aaa_violations": level_counts["AAA"],
            "compliant_level": (
                "None"
                if level_counts["A"] > 0
                else (
                    "A"
                    if level_counts["AA"] > 0
                    else "AA" if level_counts["AAA"] > 0 else "AAA"
                )
            ),
        }

    def _generate_accessibility_recommendations(
        self, issues: List[AccessibilityIssue]
    ) -> List[str]:
        """生成可访问性建议"""
        recommendations = []

        error_count = len([i for i in issues if i.severity == "error"])
        if error_count > 0:
            recommendations.append(f"优先修复 {error_count} 个可访问性错误")

        alt_issues = len([i for i in issues if "alt" in i.rule_id])
        if alt_issues > 0:
            recommendations.append("为所有图片添加有意义的alt文本")

        form_issues = len(
            [i for i in issues if "form" in i.rule_id or "label" in i.rule_id]
        )
        if form_issues > 0:
            recommendations.append("为表单元素添加适当的标签")

        return recommendations

    def _generate_i18n_recommendations(
        self, issues: List[I18nIssue], translation_data: Dict[str, Any]
    ) -> List[str]:
        """生成国际化建议"""
        recommendations = []

        hardcoded_count = len([i for i in issues if i.issue_type == "hardcoded_text"])
        if hardcoded_count > 0:
            recommendations.append(f"替换 {hardcoded_count} 个硬编码文本为国际化函数")

        if (
            "missing_translations" in translation_data
            and translation_data["missing_translations"]
        ):
            recommendations.append("完善缺失的翻译内容")

        recommendations.append("建立翻译内容管理和审核流程")

        return recommendations

    def _generate_responsive_recommendations(
        self, issues: List[ResponsiveIssue]
    ) -> List[str]:
        """生成响应式设计建议"""
        recommendations = []

        viewport_issues = len([i for i in issues if i.issue_type == "missing_viewport"])
        if viewport_issues > 0:
            recommendations.append("添加viewport meta标签")

        fixed_width_issues = len([i for i in issues if i.issue_type == "fixed_width"])
        if fixed_width_issues > 0:
            recommendations.append("使用相对单位替换固定宽度")

        recommendations.append("实施移动优先的响应式设计策略")

        return recommendations


# 使用示例
if __name__ == "__main__":
    # 初始化可访问性文化管理器
    accessibility = AccessibilityCultureManager(Path("."))

    # 生成综合报告
    report = accessibility.generate_comprehensive_report()
    print(f"可访问性综合报告: {json.dumps(report, indent=2, ensure_ascii=False)}")

    # 单独扫描可访问性
    accessibility_issues = accessibility.scan_project_accessibility()
    print(f"可访问性问题: {accessibility_issues['total_issues']} 个")

    # 单独扫描国际化
    i18n_issues = accessibility.scan_project_i18n()
    print(f"国际化问题: {i18n_issues['total_issues']} 个")
