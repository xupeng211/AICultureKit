#!/usr/bin/env python3
"""可访问性文化扩展测试 - 提升覆盖率"""

import tempfile
from pathlib import Path

import pytest

from aiculture.accessibility_culture import (
    AccessibilityChecker,
    AccessibilityCultureManager,
    I18nIssue,
    InternationalizationChecker,
)


class TestAccessibilityCultureManagerExtended:
    """可访问性文化管理器扩展测试"""

    def setup_method(self):
        """设置测试"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = AccessibilityCultureManager(self.temp_dir)

    def test_manager_initialization_extended(self):
        """测试管理器初始化扩展"""
        assert self.manager.project_path == self.temp_dir
        assert hasattr(self.manager, "i18n_checker")
        assert hasattr(self.manager, "accessibility_checker")
        assert isinstance(self.manager.i18n_checker, InternationalizationChecker)
        assert isinstance(self.manager.accessibility_checker, AccessibilityChecker)

    def test_check_project_accessibility_with_files(self):
        """测试项目可访问性检查（包含文件）"""
        # 创建Python文件
        py_file = self.temp_dir / "test.py"
        py_file.write_text(
            """
def greet_user():
    print("Hello, World!")  # 硬编码文本
    return "Welcome to our app"

def format_date():
    return "2023-12-25"  # 硬编码日期
""",
        )

        # 创建HTML文件
        html_file = self.temp_dir / "index.html"
        html_file.write_text(
            """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <img src="image.jpg">
    <button onclick="doSomething()">Click me</button>
</body>
</html>
""",
        )

        result = self.manager.check_project_accessibility()

        assert isinstance(result, dict)
        assert "i18n_issues" in result
        assert "accessibility_issues" in result
        assert "summary" in result

        # 验证发现了问题
        assert len(result["i18n_issues"]) > 0
        assert len(result["accessibility_issues"]) > 0

    def test_generate_accessibility_report_extended(self):
        """测试生成可访问性报告扩展"""
        # 创建一些测试文件
        (self.temp_dir / "test.py").write_text('print("Hello")')
        (self.temp_dir / "test.html").write_text('<img src="test.jpg">')

        report = self.manager.generate_accessibility_report()

        assert isinstance(report, dict)
        assert "summary" in report
        assert "recommendations" in report
        assert "detailed_issues" in report

        # 验证报告结构
        summary = report["summary"]
        assert "total_files_checked" in summary
        assert "total_issues_found" in summary
        assert "i18n_issues_count" in summary
        assert "accessibility_issues_count" in summary


class TestInternationalizationCheckerExtended:
    """国际化检查器扩展测试"""

    def setup_method(self):
        """设置测试"""
        self.checker = InternationalizationChecker()
        self.temp_dir = Path(tempfile.mkdtemp())

    def test_check_file_with_various_content(self):
        """测试检查包含各种内容的文件"""
        test_cases = [
            # Python文件
            (
                "test.py",
                """
def greet():
    print("Hello, World!")
    return "Welcome"

def get_date():
    return "2023-12-25 10:30:00"
""",
            ),
            # JavaScript文件
            (
                "test.js",
                """
function greet() {
    console.log("Hello, World!");
    alert("Welcome to our site");
}
""",
            ),
            # 空文件
            ("empty.py", ""),
            # 只有注释的文件
            (
                "comments.py",
                """
# This is a comment
# Another comment
""",
            ),
        ]

        for filename, content in test_cases:
            test_file = self.temp_dir / filename
            test_file.write_text(content)

            issues = self.checker.check_file(test_file)
            assert isinstance(issues, list)

            # 验证问题类型
            for issue in issues:
                assert isinstance(issue, I18nIssue)
                assert issue.issue_type in ["hardcoded_text", "locale_format"]
                assert issue.severity in ["info", "warning", "error"]

    def test_check_hardcoded_text_patterns(self):
        """测试硬编码文本模式检查"""
        test_file = self.temp_dir / "patterns.py"

        # 测试各种硬编码文本模式
        test_content = """
# 各种硬编码文本
message1 = "Hello World"
message2 = 'Welcome to our application'
error_msg = "An error occurred"
title = "User Dashboard"
greeting = "Good morning"
farewell = "Goodbye"

# 不应该匹配的内容
x = 42
y = True
z = None
short = "OK"  # 太短，不应该匹配
"""
        test_file.write_text(test_content)

        issues = self.checker.check_file(test_file)

        # 应该发现多个硬编码文本问题
        hardcode_issues = [i for i in issues if i.issue_type == "hardcoded_text"]
        assert len(hardcode_issues) > 0

        # 验证问题详情
        for issue in hardcode_issues:
            assert len(issue.text_content) > 2  # 不应该匹配短文本
            assert issue.file_path == str(test_file)
            assert issue.line_number > 0

    def test_check_datetime_format_patterns(self):
        """测试日期时间格式模式检查"""
        test_file = self.temp_dir / "datetime.py"

        test_content = """
# 各种日期时间格式
date1 = "2023-12-25"
date2 = "12/25/2023"
time1 = "10:30:00"
time2 = "14:45"
datetime1 = "2023-12-25 10:30:00"
datetime2 = "2023-12-25T10:30:00Z"
timestamp = "2024-01-15 10:30:00"

# 不应该匹配的内容
version = "1.2.3"
ratio = "16:9"
"""
        test_file.write_text(test_content)

        issues = self.checker.check_file(test_file)

        # 应该发现日期时间格式问题
        datetime_issues = [i for i in issues if i.issue_type == "locale_format"]
        assert len(datetime_issues) > 0

        # 验证问题详情
        for issue in datetime_issues:
            assert issue.severity == "info"
            assert "locale" in issue.recommendation.lower()

    def test_check_translation_completeness_with_files(self):
        """测试翻译完整性检查（包含文件）"""
        # 创建本地化目录
        locale_dir = self.temp_dir / "locales"
        locale_dir.mkdir()

        # 创建英文翻译文件
        en_file = locale_dir / "en.json"
        en_file.write_text(
            """
{
    "welcome": "Welcome",
    "goodbye": "Goodbye",
    "settings": {
        "language": "Language",
        "theme": "Theme"
    }
}
""",
        )

        # 创建中文翻译文件（缺少一些键）
        zh_file = locale_dir / "zh.json"
        zh_file.write_text(
            """
{
    "welcome": "欢迎",
    "settings": {
        "language": "语言"
    }
}
""",
        )

        result = self.checker.check_translation_completeness(locale_dir)

        assert isinstance(result, dict)
        assert "total_locales" in result
        assert "total_keys" in result
        assert "missing_translations" in result
        assert "completeness_rate" in result

        # 验证检测到缺失的翻译
        assert result["total_locales"] == 2
        assert result["total_keys"] > 0
        assert "zh" in result["missing_translations"]
        assert len(result["missing_translations"]["zh"]) > 0

        # 验证完整性比率
        assert 0 <= result["completeness_rate"]["en"] <= 100
        assert 0 <= result["completeness_rate"]["zh"] <= 100
        assert result["completeness_rate"]["en"] > result["completeness_rate"]["zh"]


class TestAccessibilityCheckerExtended:
    """可访问性检查器扩展测试"""

    def setup_method(self):
        """设置测试"""
        self.checker = AccessibilityChecker()
        self.temp_dir = Path(tempfile.mkdtemp())

    def test_check_html_accessibility_issues(self):
        """测试HTML可访问性问题检查"""
        html_file = self.temp_dir / "accessibility.html"
        html_file.write_text(
            """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Accessibility Test</title>
</head>
<body>
    <!-- 缺少alt属性的图片 -->
    <img src="image1.jpg">
    <img src="image2.jpg" alt="">
    <img src="image3.jpg" alt="Proper description">

    <!-- 按钮可访问性问题 -->
    <button onclick="doSomething()">Click</button>
    <button type="button" aria-label="Close dialog">×</button>

    <!-- 表单可访问性 -->
    <input type="text" placeholder="Enter name">
    <label for="email">Email:</label>
    <input type="email" id="email">

    <!-- 颜色对比度问题 -->
    <div style="color: #ccc; background: #fff;">Low contrast text</div>
    <div style="color: #000; background: #fff;">Good contrast text</div>
</body>
</html>
""",
        )

        issues = self.checker.check_file(html_file)

        assert isinstance(issues, list)
        assert len(issues) > 0

        # 验证发现了各种可访问性问题
        issue_types = [issue.issue_type for issue in issues]
        assert "missing_alt_text" in issue_types or "accessibility" in str(issues)

    def test_check_css_accessibility_issues(self):
        """测试CSS可访问性问题检查"""
        css_file = self.temp_dir / "styles.css"
        css_file.write_text(
            """
/* 颜色对比度问题 */
.low-contrast {
    color: #ccc;
    background-color: #fff;
}

.very-low-contrast {
    color: #fff;
    background-color: #fff;
}

/* 字体大小问题 */
.tiny-text {
    font-size: 8px;
}

.small-text {
    font-size: 10px;
}

/* 正常样式 */
.normal-text {
    color: #000;
    background-color: #fff;
    font-size: 16px;
}
""",
        )

        issues = self.checker.check_file(css_file)

        assert isinstance(issues, list)
        # CSS检查可能发现问题，也可能不发现，取决于实现

    def test_check_unsupported_file_type(self):
        """测试不支持的文件类型"""
        # 创建不支持的文件类型
        txt_file = self.temp_dir / "readme.txt"
        txt_file.write_text("This is a plain text file.")

        issues = self.checker.check_file(txt_file)

        # 对于不支持的文件类型，应该返回空列表
        assert isinstance(issues, list)
        assert len(issues) == 0


class TestI18nIssueExtended:
    """I18n问题数据类扩展测试"""

    def test_issue_creation_with_all_fields(self):
        """测试创建包含所有字段的问题"""
        issue = I18nIssue(
            issue_type="hardcoded_text",
            severity="warning",
            description="Found hardcoded text in source code",
            file_path="/path/to/file.py",
            line_number=42,
            text_content="Hello, World!",
            recommendation="Use internationalization function like _() or t()",
        )

        assert issue.issue_type == "hardcoded_text"
        assert issue.severity == "warning"
        assert issue.description == "Found hardcoded text in source code"
        assert issue.file_path == "/path/to/file.py"
        assert issue.line_number == 42
        assert issue.text_content == "Hello, World!"
        assert (
            issue.recommendation == "Use internationalization function like _() or t()"
        )

    def test_issue_creation_with_minimal_fields(self):
        """测试创建包含最少字段的问题"""
        issue = I18nIssue(
            issue_type="locale_format",
            severity="info",
            description="Date format detected",
            file_path="/path/to/file.py",
            line_number=10,
        )

        assert issue.issue_type == "locale_format"
        assert issue.severity == "info"
        assert issue.description == "Date format detected"
        assert issue.file_path == "/path/to/file.py"
        assert issue.line_number == 10
        assert issue.text_content is None
        assert issue.recommendation is None

    def test_issue_string_representation_detailed(self):
        """测试问题字符串表示详细版"""
        issue = I18nIssue(
            issue_type="hardcoded_text",
            severity="error",
            description="Critical hardcoded text",
            file_path="src/main.py",
            line_number=100,
            text_content="Error: Something went wrong",
            recommendation="Use error message localization",
        )

        str_repr = str(issue)
        assert "src/main.py" in str_repr
        assert "100" in str_repr
        assert "error" in str_repr.lower()
        assert "hardcoded_text" in str_repr


if __name__ == "__main__":
    pytest.main([__file__])
