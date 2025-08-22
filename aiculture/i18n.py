"""
国际化支持模块
提供多语言文本管理和翻译功能
"""

import json
import os
from pathlib import Path


class I18nManager:
    """国际化管理器"""

    def __init__(self, locale_dir: Path = None, default_locale: str = "en"):
        """__init__函数"""
        self.locale_dir = locale_dir or Path(__file__).parent / "locales"
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: dict[str, dict[str, str]] = {}

        # 确保locale目录存在
        self.locale_dir.mkdir(exist_ok=True)

        # 加载翻译
        self._load_translations()

    def _load_translations(self) -> None:
        """加载所有翻译文件"""
        for locale_file in self.locale_dir.glob("*.json"):
            locale = locale_file.stem
            try:
                with open(locale_file, encoding="utf-8") as f:
                    self.translations[locale] = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load locale {locale}: {e}")

    def set_locale(self, locale: str) -> None:
        """设置当前语言"""
        self.current_locale = locale
        if locale not in self.translations:
            print(f"Warning: Locale {locale} not found, using {self.default_locale}")

    def get_text(self, key: str, locale: str = None, **kwargs) -> str:
        """获取翻译文本"""
        locale = locale or self.current_locale

        # 尝试获取指定语言的翻译
        if locale in self.translations and key in self.translations[locale]:
            text = self.translations[locale][key]
        # 回退到默认语言
        elif (
            self.default_locale in self.translations
            and key in self.translations[self.default_locale]
        ):
            text = self.translations[self.default_locale][key]
        # 如果都没有，返回key本身
        else:
            text = key

        # 格式化参数
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text

    def add_translation(self, locale: str, key: str, value: str) -> None:
        """添加翻译"""
        if locale not in self.translations:
            self.translations[locale] = {}
        self.translations[locale][key] = value

    def save_translations(self) -> None:
        """保存翻译到文件"""
        for locale, translations in self.translations.items():
            locale_file = self.locale_dir / f"{locale}.json"
            with open(locale_file, "w", encoding="utf-8") as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)


# 全局实例
_i18n_manager = I18nManager()


def _(key: str, **kwargs) -> str:
    """翻译函数的简写形式"""
    return _i18n_manager.get_text(key, **kwargs)


def set_locale(locale: str) -> None:
    """设置全局语言"""
    _i18n_manager.set_locale(locale)


def get_current_locale() -> str:
    """获取当前语言"""
    return _i18n_manager.current_locale


def init_default_translations() -> None:
    """初始化默认翻译"""

    # 英文翻译
    en_translations = {
        # 通用消息
        "welcome": "Welcome",
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "loading": "Loading...",
        "please_wait": "Please wait...",
        "operation_completed": "Operation completed successfully",
        "operation_failed": "Operation failed",
        # 文化检查相关
        "culture_check_started": "Culture check started",
        "culture_check_completed": "Culture check completed",
        "violations_found": "Found {count} violations",
        "no_violations": "No violations found",
        "quality_score": "Quality score: {score}/100",
        # 测试相关
        "running_tests": "Running tests...",
        "tests_passed": "All tests passed",
        "tests_failed": "{count} tests failed",
        "test_coverage": "Test coverage: {coverage}%",
        # 安全相关
        "security_scan_started": "Security scan started",
        "security_issues_found": "Found {count} security issues",
        "high_risk_issues": "High risk issues: {count}",
        "medium_risk_issues": "Medium risk issues: {count}",
        # 性能相关
        "performance_check": "Performance check",
        "memory_usage": "Memory usage: {usage}MB",
        "execution_time": "Execution time: {time}s",
        "performance_regression": "Performance regression detected",
        # 可访问性相关
        "accessibility_check": "Accessibility check",
        "wcag_compliance": "WCAG compliance: {level}",
        "accessibility_issues": "Accessibility issues: {count}",
        # 数据治理相关
        "data_privacy_scan": "Data privacy scan",
        "gdpr_compliance": "GDPR compliance: {score}%",
        "sensitive_data_found": "Sensitive data found: {count} items",
        # 文件操作
        "file_not_found": "File not found: {filename}",
        "file_saved": "File saved: {filename}",
        "directory_created": "Directory created: {dirname}",
        # 配置相关
        "config_loaded": "Configuration loaded",
        "config_saved": "Configuration saved",
        "invalid_config": "Invalid configuration",
        # 报告相关
        "generating_report": "Generating report...",
        "report_generated": "Report generated: {filename}",
        "report_failed": "Failed to generate report",
    }

    # 中文翻译
    zh_translations = {
        # 通用消息
        "welcome": "欢迎",
        "success": "成功",
        "error": "错误",
        "warning": "警告",
        "info": "信息",
        "loading": "加载中...",
        "please_wait": "请稍候...",
        "operation_completed": "操作成功完成",
        "operation_failed": "操作失败",
        # 文化检查相关
        "culture_check_started": "文化检查已开始",
        "culture_check_completed": "文化检查已完成",
        "violations_found": "发现 {count} 个违规",
        "no_violations": "未发现违规",
        "quality_score": "质量评分: {score}/100",
        # 测试相关
        "running_tests": "正在运行测试...",
        "tests_passed": "所有测试通过",
        "tests_failed": "{count} 个测试失败",
        "test_coverage": "测试覆盖率: {coverage}%",
        # 安全相关
        "security_scan_started": "安全扫描已开始",
        "security_issues_found": "发现 {count} 个安全问题",
        "high_risk_issues": "高风险问题: {count} 个",
        "medium_risk_issues": "中等风险问题: {count} 个",
        # 性能相关
        "performance_check": "性能检查",
        "memory_usage": "内存使用: {usage}MB",
        "execution_time": "执行时间: {time}秒",
        "performance_regression": "检测到性能回归",
        # 可访问性相关
        "accessibility_check": "可访问性检查",
        "wcag_compliance": "WCAG合规性: {level}",
        "accessibility_issues": "可访问性问题: {count} 个",
        # 数据治理相关
        "data_privacy_scan": "数据隐私扫描",
        "gdpr_compliance": "GDPR合规性: {score}%",
        "sensitive_data_found": "发现敏感数据: {count} 项",
        # 文件操作
        "file_not_found": "文件未找到: {filename}",
        "file_saved": "文件已保存: {filename}",
        "directory_created": "目录已创建: {dirname}",
        # 配置相关
        "config_loaded": "配置已加载",
        "config_saved": "配置已保存",
        "invalid_config": "无效配置",
        # 报告相关
        "generating_report": "正在生成报告...",
        "report_generated": "报告已生成: {filename}",
        "report_failed": "报告生成失败",
    }

    # 保存翻译
    _i18n_manager.translations["en"] = en_translations
    _i18n_manager.translations["zh"] = zh_translations
    _i18n_manager.save_translations()


# 自动初始化
if not _i18n_manager.translations:
    init_default_translations()


# 根据环境变量设置语言
env_locale = os.getenv("AICULTURE_LOCALE", "en")
if env_locale in _i18n_manager.translations:
    set_locale(env_locale)
