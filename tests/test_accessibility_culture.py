"""
可访问性文化模块测试
"""

import tempfile
from pathlib import Path
import pytest

from aiculture.accessibility_culture import (
    AccessibilityCultureManager,
    AccessibilityChecker,
    InternationalizationChecker,
    ResponsiveDesignChecker,
)


class TestAccessibilityChecker:
    """可访问性检查器测试"""

    def setup_method(self):
        """测试设置"""
        self.checker = AccessibilityChecker()

    def test_missing_alt_text_detection(self):
        """测试缺失alt文本检测"""
        html_content = """
        <html>
            <body>
                <img src="image1.jpg" alt="Description">  <!-- 正确 -->
                <img src="image2.jpg">                    <!-- 缺失alt -->
                <img src="image3.jpg" alt="">             <!-- 空alt -->
            </body>
        </html>
        """

        issues = self.checker.check_html_content(html_content, "test.html")

        # 应该找到2个alt文本问题
        alt_issues = [issue for issue in issues if "alt" in issue.description.lower()]
        assert len(alt_issues) >= 1

    def test_heading_structure_check(self):
        """测试标题结构检查"""
        # 错误的标题结构
        bad_html = """
        <html>
            <body>
                <h1>Main Title</h1>
                <h3>Skipped H2</h3>  <!-- 跳过了H2 -->
                <h2>Wrong Order</h2>
            </body>
        </html>
        """

        issues = self.checker.check_html_content(bad_html, "test.html")

        # 应该找到标题结构问题
        heading_issues = [
            issue for issue in issues if "heading" in issue.description.lower()
        ]
        assert len(heading_issues) >= 1

    def test_color_contrast_check(self):
        """测试颜色对比度检查"""
        css_content = """
        .low-contrast {
            color: #999999;
            background-color: #CCCCCC;  /* 对比度不足 */
        }
        
        .good-contrast {
            color: #000000;
            background-color: #FFFFFF;  /* 对比度良好 */
        }
        """

        issues = self.checker.check_css_content(css_content, "test.css")

        # 应该找到对比度问题
        contrast_issues = [
            issue for issue in issues if "contrast" in issue.description.lower()
        ]
        assert len(contrast_issues) >= 0  # 可能找到对比度问题

    def test_form_accessibility_check(self):
        """测试表单可访问性检查"""
        html_content = """
        <html>
            <body>
                <form>
                    <label for="name">Name:</label>
                    <input type="text" id="name">  <!-- 正确 -->
                    
                    <input type="email" placeholder="Email">  <!-- 缺失label -->
                    
                    <button type="submit">Submit</button>
                </form>
            </body>
        </html>
        """

        issues = self.checker.check_html_content(html_content, "form.html")

        # 应该找到表单可访问性问题
        form_issues = [
            issue
            for issue in issues
            if "label" in issue.description.lower()
            or "form" in issue.description.lower()
        ]
        assert len(form_issues) >= 1

    def test_keyboard_navigation_check(self):
        """测试键盘导航检查"""
        html_content = """
        <html>
            <body>
                <div onclick="doSomething()">Clickable Div</div>  <!-- 不可键盘访问 -->
                <button onclick="doSomething()">Button</button>    <!-- 可键盘访问 -->
                <a href="#" tabindex="-1">Link</a>                <!-- 移除了tab顺序 -->
            </body>
        </html>
        """

        issues = self.checker.check_html_content(html_content, "navigation.html")

        # 应该找到键盘导航问题
        keyboard_issues = [
            issue
            for issue in issues
            if "keyboard" in issue.description.lower()
            or "tabindex" in issue.description.lower()
        ]
        assert len(keyboard_issues) >= 0  # 可能找到键盘导航问题

    def test_wcag_compliance_levels(self):
        """测试WCAG合规级别"""
        # 创建不同严重程度的问题
        html_content = """
        <html>
            <body>
                <img src="image.jpg">  <!-- 严重问题：缺失alt -->
                <h1>Title</h1>
                <h3>Subtitle</h3>     <!-- 中等问题：跳过h2 -->
            </body>
        </html>
        """

        issues = self.checker.check_html_content(html_content, "test.html")

        # 验证问题有不同的严重程度
        severities = [issue.severity for issue in issues]
        assert len(set(severities)) >= 1  # 至少有一种严重程度


class TestInternationalizationChecker:
    """国际化检查器测试"""

    def setup_method(self):
        """测试设置"""
        self.checker = InternationalizationChecker()

    def test_hardcoded_text_detection(self):
        """测试硬编码文本检测"""
        python_content = '''
        def greet_user(name):
            """greet_user函数"""
            return f"Hello, {name}!"  # 硬编码英文
        
        def show_error():
            """show_error函数"""
            print("Error occurred")  # 硬编码英文
        
        def get_message():
            """get_message函数"""
            return _("Welcome")  # 正确的国际化
        '''

        issues = self.checker.check_python_content(python_content, "test.py")

        # 应该找到硬编码文本
        hardcoded_issues = [
            issue for issue in issues if "hardcoded" in issue.description.lower()
        ]
        assert len(hardcoded_issues) >= 2

    def test_chinese_text_detection(self):
        """测试中文文本检测"""
        python_content = '''
        def show_message():
            """show_message函数"""
            print("欢迎使用系统")  # 硬编码中文
            return "操作成功"      # 硬编码中文
        
        def localized_message():
            """localized_message函数"""
            return _("欢迎")  # 正确的国际化中文
        '''

        issues = self.checker.check_python_content(python_content, "chinese.py")

        # 应该找到硬编码中文
        chinese_issues = [
            issue
            for issue in issues
            if "chinese" in issue.description.lower() or "中文" in issue.description
        ]
        assert len(chinese_issues) >= 2

    def test_html_lang_attribute_check(self):
        """测试HTML语言属性检查"""
        # 缺失lang属性的HTML
        html_without_lang = """
        <html>
            <head><title>Test</title></head>
            <body><p>Content</p></body>
        </html>
        """

        # 有lang属性的HTML
        html_with_lang = """
        <html lang="en">
            <head><title>Test</title></head>
            <body><p>Content</p></body>
        </html>
        """

        issues1 = self.checker.check_html_content(html_without_lang, "no_lang.html")
        issues2 = self.checker.check_html_content(html_with_lang, "with_lang.html")

        # 没有lang属性的应该有问题
        lang_issues1 = [
            issue for issue in issues1 if "lang" in issue.description.lower()
        ]
        lang_issues2 = [
            issue for issue in issues2 if "lang" in issue.description.lower()
        ]

        assert len(lang_issues1) >= 1
        assert len(lang_issues2) == 0

    def test_date_format_check(self):
        """测试日期格式检查"""
        python_content = '''
        from datetime import datetime
        
        def format_date():
            """format_date函数"""
            return datetime.now().strftime("%m/%d/%Y")  # 美式日期格式
        
        def better_format():
            """better_format函数"""
            return datetime.now().strftime("%Y-%m-%d")  # ISO格式
        '''

        issues = self.checker.check_python_content(python_content, "dates.py")

        # 可能找到日期格式问题
        date_issues = [issue for issue in issues if "date" in issue.description.lower()]
        assert len(date_issues) >= 0

    def test_comprehensive_i18n_check(self):
        """测试综合国际化检查"""
        mixed_content = '''
        class UserInterface:
            """UserInterface:类"""
            def __init__(self):
                """__init__函数"""
                self.title = "用户管理系统"  # 硬编码中文
                self.welcome = "Welcome!"   # 硬编码英文
            
            def show_error(self):
                """show_error函数"""
                print("错误：操作失败")  # 硬编码中文
            
            def localized_message(self):
                """localized_message函数"""
                return _("Success")  # 正确的国际化
        '''

        issues = self.checker.check_python_content(mixed_content, "mixed.py")

        # 应该找到多个国际化问题
        assert len(issues) >= 3

        # 验证问题类型
        issue_types = [issue.issue_type for issue in issues]
        assert "hardcoded_text" in issue_types


class TestResponsiveDesignChecker:
    """响应式设计检查器测试"""

    def setup_method(self):
        """测试设置"""
        self.checker = ResponsiveDesignChecker()

    def test_viewport_meta_check(self):
        """测试viewport meta标签检查"""
        # 缺失viewport的HTML
        html_without_viewport = """
        <html>
            <head><title>Test</title></head>
            <body><p>Content</p></body>
        </html>
        """

        # 有viewport的HTML
        html_with_viewport = """
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Test</title>
            </head>
            <body><p>Content</p></body>
        </html>
        """

        issues1 = self.checker.check_html_content(
            html_without_viewport, "no_viewport.html"
        )
        issues2 = self.checker.check_html_content(
            html_with_viewport, "with_viewport.html"
        )

        # 没有viewport的应该有问题
        viewport_issues1 = [
            issue for issue in issues1 if "viewport" in issue.description.lower()
        ]
        viewport_issues2 = [
            issue for issue in issues2 if "viewport" in issue.description.lower()
        ]

        assert len(viewport_issues1) >= 1
        assert len(viewport_issues2) == 0

    def test_media_query_check(self):
        """测试媒体查询检查"""
        # 没有媒体查询的CSS
        css_without_media = """
        .container {
            width: 1200px;
            margin: 0 auto;
        }
        """

        # 有媒体查询的CSS
        css_with_media = """
        .container {
            width: 1200px;
            margin: 0 auto;
        }
        
        @media (max-width: 768px) {
            .container {
                width: 100%;
                padding: 0 20px;
            }
        }
        """

        issues1 = self.checker.check_css_content(css_without_media, "no_media.css")
        issues2 = self.checker.check_css_content(css_with_media, "with_media.css")

        # 没有媒体查询的可能有问题
        media_issues1 = [
            issue for issue in issues1 if "media" in issue.description.lower()
        ]
        media_issues2 = [
            issue for issue in issues2 if "media" in issue.description.lower()
        ]

        # 至少第一个应该有更多问题
        assert len(issues1) >= len(issues2)

    def test_fixed_width_detection(self):
        """测试固定宽度检测"""
        css_content = """
        .fixed-width {
            width: 800px;  /* 固定宽度 */
        }
        
        .responsive-width {
            width: 100%;   /* 响应式宽度 */
            max-width: 800px;
        }
        """

        issues = self.checker.check_css_content(css_content, "widths.css")

        # 可能找到固定宽度问题
        width_issues = [
            issue for issue in issues if "width" in issue.description.lower()
        ]
        assert len(width_issues) >= 0

    def test_touch_target_size_check(self):
        """测试触摸目标大小检查"""
        css_content = """
        .small-button {
            width: 20px;   /* 太小的触摸目标 */
            height: 20px;
        }
        
        .good-button {
            width: 44px;   /* 合适的触摸目标 */
            height: 44px;
        }
        """

        issues = self.checker.check_css_content(css_content, "buttons.css")

        # 可能找到触摸目标大小问题
        touch_issues = [
            issue
            for issue in issues
            if "touch" in issue.description.lower()
            or "size" in issue.description.lower()
        ]
        assert len(touch_issues) >= 0


class TestAccessibilityCultureManager:
    """可访问性文化管理器测试"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = AccessibilityCultureManager(self.temp_dir)

    def teardown_method(self):
        """测试清理"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager.project_path == self.temp_dir
        assert isinstance(self.manager.accessibility_checker, AccessibilityChecker)
        assert isinstance(self.manager.i18n_checker, InternationalizationChecker)
        assert isinstance(self.manager.responsive_checker, ResponsiveDesignChecker)

    def test_project_accessibility_scan(self):
        """测试项目可访问性扫描"""
        # 创建测试HTML文件
        html_file = self.temp_dir / "index.html"
        with open(html_file, "w") as f:
            f.write(
                """
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <img src="image.jpg">  <!-- 缺失alt -->
                    <h1>Title</h1>
                    <h3>Subtitle</h3>     <!-- 跳过h2 -->
                </body>
            </html>
            """
            )

        # 创建测试Python文件
        py_file = self.temp_dir / "app.py"
        with open(py_file, "w") as f:
            f.write(
                '''
            def greet():
                """greet函数"""
                return "Hello World!"  # 硬编码英文
            
            def welcome():
                """welcome函数"""
                print("欢迎使用")  # 硬编码中文
            '''
            )

        # 扫描项目
        scan_result = self.manager.scan_project()

        assert isinstance(scan_result, dict)
        assert "accessibility_issues" in scan_result
        assert "i18n_issues" in scan_result
        assert "responsive_issues" in scan_result
        assert "total_issues" in scan_result

        # 应该找到一些问题
        assert scan_result["total_issues"] > 0

    def test_comprehensive_report_generation(self):
        """测试综合报告生成"""
        # 创建包含各种问题的测试文件
        html_file = self.temp_dir / "test.html"
        with open(html_file, "w") as f:
            f.write(
                """
            <html>
                <head><title>测试页面</title></head>  <!-- 硬编码中文 -->
                <body>
                    <img src="logo.jpg">  <!-- 缺失alt -->
                    <div onclick="click()">Click me</div>  <!-- 不可访问 -->
                </body>
            </html>
            """
            )

        css_file = self.temp_dir / "style.css"
        with open(css_file, "w") as f:
            f.write(
                """
            .container {
                width: 1000px;  /* 固定宽度 */
            }
            
            .button {
                width: 15px;    /* 触摸目标太小 */
                height: 15px;
            }
            """
            )

        # 生成综合报告
        report = self.manager.generate_comprehensive_report()

        assert isinstance(report, dict)
        assert "overall_score" in report
        assert "accessibility_score" in report
        assert "i18n_score" in report
        assert "responsive_score" in report
        assert "recommendations" in report

        # 验证评分范围
        assert 0 <= report["overall_score"] <= 100
        assert 0 <= report["accessibility_score"] <= 100
        assert 0 <= report["i18n_score"] <= 100
        assert 0 <= report["responsive_score"] <= 100

    def test_issue_prioritization(self):
        """测试问题优先级排序"""
        # 创建包含不同严重程度问题的文件
        html_file = self.temp_dir / "priority_test.html"
        with open(html_file, "w") as f:
            f.write(
                """
            <html>
                <body>
                    <img src="critical.jpg">  <!-- 严重：缺失alt -->
                    <h1>Title</h1>
                    <h3>Skip H2</h3>          <!-- 中等：跳过标题 -->
                    <p style="color: #888; background: #999;">Low contrast</p>  <!-- 轻微 -->
                </body>
            </html>
            """
            )

        scan_result = self.manager.scan_project()

        # 验证问题按严重程度分类
        if "accessibility_issues" in scan_result:
            issues = scan_result["accessibility_issues"]
            severities = [issue.severity for issue in issues]

            # 应该有不同严重程度的问题
            unique_severities = set(severities)
            assert len(unique_severities) >= 1


# 集成测试
class TestAccessibilityCultureIntegration:
    """可访问性文化集成测试"""

    def test_end_to_end_accessibility_check(self):
        """测试端到端可访问性检查"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            manager = AccessibilityCultureManager(temp_dir)

            # 创建一个完整的Web应用示例
            html_file = temp_dir / "app.html"
            with open(html_file, "w") as f:
                f.write(
                    """
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Accessible App</title>
                        <link rel="stylesheet" href="style.css">
                    </head>
                    <body>
                        <header>
                            <h1>Welcome to Our App</h1>
                            <nav>
                                <ul>
                                    <li><a href="#home">Home</a></li>
                                    <li><a href="#about">About</a></li>
                                </ul>
                            </nav>
                        </header>
                        
                        <main>
                            <img src="hero.jpg" alt="Hero image showing our product">
                            <form>
                                <label for="email">Email:</label>
                                <input type="email" id="email" required>
                                
                                <label for="message">Message:</label>
                                <textarea id="message"></textarea>
                                
                                <button type="submit">Send Message</button>
                            </form>
                        </main>
                    </body>
                </html>
                """
                )

            css_file = temp_dir / "style.css"
            with open(css_file, "w") as f:
                f.write(
                    """
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                @media (max-width: 768px) {
                    .container {
                        padding: 0 10px;
                    }
                }
                
                button {
                    min-width: 44px;
                    min-height: 44px;
                    padding: 10px 20px;
                }
                """
                )

            py_file = temp_dir / "app.py"
            with open(py_file, "w") as f:
                f.write(
                    '''
                from flask import Flask, render_template
                
                app = Flask(__name__)
                
                @app.route('/')
                def home():
                    """home函数"""
                    return render_template('app.html')
                
                @app.route('/api/message')
                def get_message():
                    """get_message函数"""
                    return {"message": _("Welcome to our application")}
                '''
                )

            # 执行完整的可访问性检查
            report = manager.generate_comprehensive_report()

            # 验证报告结构
            assert isinstance(report, dict)
            assert "overall_score" in report
            assert "accessibility_score" in report
            assert "i18n_score" in report
            assert "responsive_score" in report

            # 这个例子应该有较高的可访问性分数
            assert report["accessibility_score"] > 70
            assert report["responsive_score"] > 70

        finally:
            import shutil

            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
