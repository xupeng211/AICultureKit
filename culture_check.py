#!/usr/bin/env python3
"""
快速文化标准符合度检查
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


def check_test_coverage():
    """检查测试覆盖率"""
    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "--cov=aiculture",
                "--cov-report=term",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # 解析覆盖率
        for line in result.stdout.split('\n'):
            if 'TOTAL' in line and '%' in line:
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        coverage = int(part.replace('%', ''))
                        return coverage
        return 0
    except Exception as e:
        print(f"测试覆盖率检查失败: {e}")
        return 0


def check_code_quality():
    """检查代码质量"""
    try:
        result = subprocess.run(
            ["flake8", "aiculture", "--count", "--statistics"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # 统计错误数量
        error_count = 0
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            if lines and lines[-1].isdigit():
                error_count = int(lines[-1])

        return error_count
    except Exception as e:
        print(f"代码质量检查失败: {e}")
        return -1


def check_security_issues():
    """检查安全问题"""
    try:
        from aiculture.data_governance_culture import DataGovernanceManager

        governance = DataGovernanceManager(Path('.'))
        scan_result = governance.scan_project_for_privacy_issues()

        high_risk = len(scan_result.get('by_severity', {}).get('high', []))
        medium_risk = len(scan_result.get('by_severity', {}).get('medium', []))

        return high_risk, medium_risk
    except Exception as e:
        print(f"安全问题检查失败: {e}")
        return 0, 0


def check_internationalization():
    """检查国际化支持"""
    try:
        from aiculture.i18n import _, set_locale

        # 测试中英文切换
        set_locale('en')
        en_text = _('welcome')

        set_locale('zh')
        zh_text = _('welcome')

        return en_text != zh_text and en_text == 'Welcome' and zh_text == '欢迎'
    except Exception as e:
        print(f"国际化功能检查失败: {e}")
        return False


def check_data_catalog():
    """检查数据目录功能"""
    try:
        from aiculture.data_catalog import DataCatalog

        catalog = DataCatalog(Path('./temp_catalog'))
        report = catalog.generate_catalog_report()

        # 清理临时目录
        import shutil

        if Path('./temp_catalog').exists():
            shutil.rmtree('./temp_catalog')

        return isinstance(report, dict)
    except Exception as e:
        print(f"数据目录功能检查失败: {e}")
        return False


def check_monitoring_config():
    """检查监控配置功能"""
    try:
        from aiculture.monitoring_config import MonitoringConfigManager

        manager = MonitoringConfigManager(Path('./temp_monitoring'))
        config = manager.generate_prometheus_config()

        # 清理临时目录
        import shutil

        if Path('./temp_monitoring').exists():
            shutil.rmtree('./temp_monitoring')

        return isinstance(config, dict) and 'global' in config
    except Exception as e:
        print(f"监控配置功能检查失败: {e}")
        return False


def run_all_checks() -> Dict[str, Any]:
    """运行所有检查项目"""
    checks = {}

    print('🧪 检查测试覆盖率...')
    coverage = check_test_coverage()
    checks['test_coverage'] = coverage
    print(f'   测试覆盖率: {coverage}%')

    print('📝 检查代码质量...')
    flake8_errors = check_code_quality()
    checks['code_quality'] = flake8_errors
    if flake8_errors == -1:
        print('   代码质量检查失败')
    else:
        print(f'   Flake8错误数: {flake8_errors}')

    print('🔒 检查安全问题...')
    high_risk, medium_risk = check_security_issues()
    checks['security'] = (high_risk, medium_risk)
    print(f'   高风险问题: {high_risk} 个')
    print(f'   中等风险问题: {medium_risk} 个')

    print('🌐 检查国际化支持...')
    i18n_ok = check_internationalization()
    checks['i18n'] = i18n_ok
    print(f'   国际化功能: {"✅ 正常" if i18n_ok else "❌ 异常"}')

    print('📋 检查数据目录功能...')
    catalog_ok = check_data_catalog()
    checks['data_catalog'] = catalog_ok
    print(f'   数据目录功能: {"✅ 正常" if catalog_ok else "❌ 异常"}')

    print('📊 检查监控配置功能...')
    monitoring_ok = check_monitoring_config()
    checks['monitoring'] = monitoring_ok
    print(f'   监控配置功能: {"✅ 正常" if monitoring_ok else "❌ 异常"}')

    return checks


def calculate_coverage_score(coverage: int) -> Tuple[int, str]:
    """计算测试覆盖率评分"""
    if coverage >= 80:
        return 30, "优秀"
    elif coverage >= 60:
        return 20, "良好"
    elif coverage >= 30:
        return 10, "一般"
    else:
        return 0, "不足"


def calculate_quality_score(flake8_errors: int) -> Tuple[int, str]:
    """计算代码质量评分"""
    if flake8_errors == 0:
        return 25, "优秀"
    elif flake8_errors <= 5:
        return 20, "良好"
    elif flake8_errors <= 15:
        return 10, "一般"
    else:
        return 0, "不足"


def calculate_security_score(high_risk: int, medium_risk: int) -> Tuple[int, str]:
    """计算安全性评分"""
    if high_risk == 0 and medium_risk <= 5:
        return 20, "优秀"
    elif high_risk == 0 and medium_risk <= 20:
        return 15, "良好"
    elif high_risk <= 2:
        return 10, "一般"
    else:
        return 0, "不足"


def calculate_functional_score(checks: Dict[str, Any]) -> Tuple[int, str]:
    """计算功能完整性评分"""
    functional_score = 0
    if checks['i18n']:
        functional_score += 8
    if checks['data_catalog']:
        functional_score += 8
    if checks['monitoring']:
        functional_score += 9

    if functional_score >= 20:
        return functional_score, "优秀"
    elif functional_score >= 15:
        return functional_score, "良好"
    elif functional_score >= 10:
        return functional_score, "一般"
    else:
        return functional_score, "不足"


def calculate_scores(checks: Dict[str, Any]) -> Tuple[int, Dict[str, str]]:
    """计算各项评分"""
    score = 0
    status_info = {}

    # 测试覆盖率 (30分)
    coverage_score, coverage_status = calculate_coverage_score(checks['test_coverage'])
    score += coverage_score
    status_info['coverage'] = coverage_status

    # 代码质量 (25分)
    quality_score, quality_status = calculate_quality_score(checks['code_quality'])
    score += quality_score
    status_info['quality'] = quality_status

    # 安全性 (20分)
    high_risk, medium_risk = checks['security']
    security_score, security_status = calculate_security_score(high_risk, medium_risk)
    score += security_score
    status_info['security'] = security_status

    # 功能完整性 (25分)
    functional_score, functional_status = calculate_functional_score(checks)
    score += functional_score
    status_info['functional'] = functional_status

    return score, status_info


def print_evaluation_results(
    checks: Dict[str, Any], score: int, status_info: Dict[str, str]
):
    """打印评估结果"""
    print()
    print('📊 综合评估结果:')
    print('-' * 40)

    coverage = checks['test_coverage']
    flake8_errors = checks['code_quality']
    high_risk, medium_risk = checks['security']
    functional_score = sum(
        [
            8 if checks['i18n'] else 0,
            8 if checks['data_catalog'] else 0,
            9 if checks['monitoring'] else 0,
        ]
    )

    print(f'📊 测试覆盖率: {coverage}% ({status_info["coverage"]})')
    print(f'📝 代码质量: {flake8_errors} 个错误 ({status_info["quality"]})')
    print(
        f'🔒 安全性: {high_risk} 高风险, {medium_risk} 中风险 ({status_info["security"]})'
    )
    print(f'🔧 功能完整性: {functional_score}/25 分 ({status_info["functional"]})')
    print()

    print(f'🏆 总体评分: {score}/100')


def print_final_assessment(score: int):
    """打印最终评价"""
    if score >= 85:
        overall_status = "优秀"
        emoji = "🎉"
        message = "项目完全符合开发文化标准！"
    elif score >= 70:
        overall_status = "良好"
        emoji = "👍"
        message = "项目基本符合开发文化标准，有小幅改进空间。"
    elif score >= 60:
        overall_status = "一般"
        emoji = "⚠️"
        message = "项目部分符合开发文化标准，需要重点改进。"
    else:
        overall_status = "不达标"
        emoji = "❌"
        message = "项目不符合开发文化标准，需要大幅改进。"

    print(f'{emoji} 文化标准符合度: {overall_status}')
    print(f'💬 评价: {message}')


def print_quality_suggestions(coverage: int, flake8_errors: int):
    """打印质量相关建议"""
    if coverage < 80:
        print('   • 提升测试覆盖率，目标80%以上')
    if flake8_errors > 0:
        print('   • 修复代码质量问题，消除flake8错误')


def print_security_suggestions(high_risk: int, medium_risk: int):
    """打印安全相关建议"""
    if high_risk > 0:
        print('   • 立即处理高风险安全问题')
    if medium_risk > 20:
        print('   • 逐步清理中等风险安全问题')


def print_functionality_suggestions(checks: Dict[str, Any]):
    """打印功能相关建议"""
    if not checks['i18n']:
        print('   • 修复国际化功能问题')
    if not checks['data_catalog']:
        print('   • 修复数据目录功能问题')
    if not checks['monitoring']:
        print('   • 修复监控配置功能问题')


def print_congratulations(coverage: int, flake8_errors: int, high_risk: int):
    """打印祝贺信息"""
    if coverage >= 80 and flake8_errors == 0 and high_risk == 0:
        print('   🎊 恭喜！项目已达到优秀的文化标准！')


def print_improvement_suggestions(checks: Dict[str, Any]):
    """打印改进建议"""
    print()
    print('💡 改进建议:')

    coverage = checks['test_coverage']
    flake8_errors = checks['code_quality']
    high_risk, medium_risk = checks['security']

    print_quality_suggestions(coverage, flake8_errors)
    print_security_suggestions(high_risk, medium_risk)
    print_functionality_suggestions(checks)
    print_congratulations(coverage, flake8_errors, high_risk)


def main():
    """主函数"""
    print('🔍 AICultureKit 项目文化标准符合度检查')
    print('=' * 60)

    # 运行所有检查
    checks = run_all_checks()

    # 计算评分
    score, status_info = calculate_scores(checks)

    # 打印结果
    print_evaluation_results(checks, score, status_info)
    print_final_assessment(score)
    print_improvement_suggestions(checks)


if __name__ == "__main__":
    main()
