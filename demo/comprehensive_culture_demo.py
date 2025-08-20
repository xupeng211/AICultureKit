#!/usr/bin/env python3
"""
AICultureKit 综合文化演示
展示所有新增的文化模块功能
"""

import time
import json
from pathlib import Path

# 导入所有文化模块
from aiculture.culture_enforcer import CultureEnforcer
from aiculture.performance_culture import PerformanceBenchmarkManager, MemoryLeakDetector
from aiculture.observability_culture import ObservabilityManager
from aiculture.data_governance_culture import DataGovernanceManager
from aiculture.accessibility_culture import AccessibilityCultureManager
from aiculture.response_time_monitor import ResponseTimeMonitor
from aiculture.alerting_rules import AlertingRulesManager

# 🔒 数据隐私声明 / Data Privacy Notice:
# 本演示代码中的所有敏感字段名和数据都是虚构的示例，仅用于展示功能。
# 在实际项目中，请遵循数据隐私法规（如GDPR、CCPA等）处理敏感信息。
# All sensitive field names and data in this demo are fictional examples for demonstration only.
# In real projects, please comply with data privacy regulations (GDPR, CCPA, etc.) when handling sensitive information.


def demo_performance_culture():
    """演示性能文化"""
    print("\n🚀 性能文化演示")
    print("=" * 50)

    # 性能基准管理
    manager = PerformanceBenchmarkManager(Path("."))

    # 创建示例函数
    def sample_function():
        """示例函数"""
        time.sleep(0.01)  # 模拟工作
        return sum(range(1000))

    # 创建性能基准
    print("📊 创建性能基准...")
    benchmark = manager.create_benchmark("sample_function", "function", sample_function)
    print(f"   基准时间: {benchmark.baseline_time:.4f}s")

    # 运行性能测试
    print("🏃 运行性能测试...")
    result = manager.run_benchmark("sample_function", sample_function)
    print(f"   执行时间: {result.execution_time:.4f}s")
    print(f"   内存使用: {result.memory_usage} bytes")
    print(f"   是否回归: {'是' if result.is_regression else '否'}")

    # 内存泄漏检测
    print("🔍 内存泄漏检测...")
    detector = MemoryLeakDetector()
    detector.start_monitoring(interval=1)
    time.sleep(3)  # 监控3秒
    detector.stop_monitoring()

    leak_result = detector.detect_leaks()
    print(f"   检测状态: {leak_result['status']}")
    if leak_result.get('warnings'):
        for warning in leak_result['warnings']:
            print(f"   ⚠️ {warning}")


def demo_observability_culture():
    """演示可观测性文化"""
    print("\n📊 可观测性文化演示")
    print("=" * 50)

    # 初始化可观测性管理器
    obs = ObservabilityManager("demo-service", "1.0.0")

    # 演示结构化日志
    print("📝 结构化日志演示...")
    with obs.observe_operation("demo_operation", user_id="123", request_id="req-456") as ctx:
        logger = ctx['logger']
        metrics = ctx['metrics']

        logger.info("开始处理请求", component="api")
        metrics.counter("requests_total", labels={'method': 'GET', 'status': '200'})

        # 模拟一些工作
        time.sleep(0.05)

        logger.info("请求处理完成", component="api")
        metrics.histogram("request_duration", 50, labels={'method': 'GET'})

    # 导出可观测性数据
    data = obs.export_observability_data()
    print(f"   指标数量: {len(data['metrics'])}")
    print(f"   追踪数量: {len(data['traces'])}")

    # 响应时间监控
    print("⏱️ 响应时间监控演示...")
    monitor = ResponseTimeMonitor(Path("."))

    # 监控函数执行
    with monitor.monitor_execution("demo_function", "function"):
        time.sleep(0.02)  # 模拟工作

    # 获取统计信息
    stats = monitor.get_statistics()
    if stats.get('total_requests', 0) > 0:
        print(f"   平均响应时间: {stats['avg_response_time']:.2f}ms")
        print(f"   成功率: {stats['success_rate']:.2%}")

    monitor.stop_monitoring()


def demo_data_governance_culture():
    """演示数据治理文化"""
    print("\n🛡️ 数据治理文化演示")
    print("=" * 50)

    # 初始化数据治理管理器
    governance = DataGovernanceManager(Path("."))

    # 扫描隐私问题
    print("🔍 隐私问题扫描...")
    privacy_scan = governance.scan_project_for_privacy_issues()
    print(f"   发现问题: {privacy_scan['total_findings']} 个")

    if privacy_scan['total_findings'] > 0:
        for severity, issues in privacy_scan['by_severity'].items():
            if issues:
                print(f"   {severity.upper()}: {len(issues)} 个")

    # 生成合规报告
    print("📋 生成合规报告...")
    compliance_report = governance.generate_compliance_report()
    print(f"   总体合规评分: {compliance_report['overall_compliance_score']:.1f}/100")
    print(f"   数据清单大小: {compliance_report['data_inventory_size']}")

    # 显示行动项
    print("   📝 行动项:")
    for item in compliance_report['action_items'][:3]:
        print(f"      • {item}")


def demo_accessibility_culture():
    """演示可访问性文化"""
    print("\n♿ 可访问性文化演示")
    print("=" * 50)

    # 初始化可访问性管理器
    accessibility = AccessibilityCultureManager(Path("."))

    # 生成综合报告
    print("🔍 可访问性综合扫描...")
    report = accessibility.generate_comprehensive_report()

    print(f"   总体评分: {report['overall_score']:.1f}/100")
    print(f"   总问题数: {report['total_issues']}")

    # 可访问性问题
    accessibility_issues = report['accessibility']
    print(f"   可访问性问题: {accessibility_issues['total_issues']} 个")
    if accessibility_issues['total_issues'] > 0:
        for severity, issues in accessibility_issues['by_severity'].items():
            if issues:
                print(f"      {severity.upper()}: {len(issues)} 个")

    # 国际化问题
    i18n_issues = report['internationalization']
    print(f"   国际化问题: {i18n_issues['total_issues']} 个")

    # 响应式设计问题
    responsive_issues = report['responsive_design']
    print(f"   响应式设计问题: {responsive_issues['total_issues']} 个")

    # 显示优先行动
    print("   📝 优先行动:")
    for action in report['priority_actions'][:3]:
        print(f"      • {action}")


def demo_alerting_system():
    """演示告警系统"""
    print("\n🚨 告警系统演示")
    print("=" * 50)

    # 初始化告警管理器
    alerting = AlertingRulesManager(Path("."))

    # 模拟指标数据
    metrics = {
        "avg_response_time": 600,  # 600ms，超过阈值
        "memory_usage_percent": 85,  # 85%，超过阈值
        "cpu_usage_percent": 70,  # 70%，正常
        "error_rate": 2,  # 2%，正常
        "service_availability": 100,  # 100%，正常
        "test_coverage": 75,  # 75%，低于阈值
        "security_issues": 1,  # 1个安全问题
        "data_quality_score": 95,  # 95%，正常
    }

    print("📊 评估告警规则...")
    new_alerts = alerting.evaluate_rules(metrics)
    print(f"   新产生告警: {len(new_alerts)} 个")

    # 获取活跃告警
    active_alerts = alerting.get_active_alerts()
    print(f"   活跃告警: {len(active_alerts)} 个")

    if active_alerts:
        print("   🔥 活跃告警详情:")
        for alert in active_alerts[:3]:  # 只显示前3个
            print(f"      • {alert.rule_name}: {alert.message}")

    # 验证规则
    validation_results = alerting.validate_rules()
    if validation_results:
        print(f"   ⚠️ 规则验证问题: {len(validation_results)} 个")
    else:
        print("   ✅ 所有规则验证通过")


def demo_comprehensive_enforcement():
    """演示综合文化执行"""
    print("\n🎯 综合文化执行演示")
    print("=" * 50)

    # 初始化文化执行器
    enforcer = CultureEnforcer(".")

    print("🔍 执行全面文化检查...")
    result = enforcer.enforce_all()

    print(f"   质量评分: {result['score']}/100")
    print(f"   总违规数: {result['total_violations']}")
    print(f"   错误: {result['errors']} 个")
    print(f"   警告: {result['warnings']} 个")

    # 按原则分组显示违规
    if result.get('by_principle'):
        print("   📋 按原则分组的违规:")
        for principle, violations in result['by_principle'].items():
            if violations:
                print(f"      • {principle}: {len(violations)} 个")

    # 显示建议
    print("   💡 改进建议:")
    suggestions = [
        "优先修复错误级别的问题",
        "完善性能监控和基准测试",
        "加强数据隐私保护措施",
        "改善用户界面可访问性",
        "建立完整的可观测性体系",
    ]

    for suggestion in suggestions[:3]:
        print(f"      • {suggestion}")


def main():
    """主演示函数"""
    print("🌟 AICultureKit 综合文化演示")
    print("=" * 60)
    print("展示完整的AI协作开发文化体系")

    try:
        # 演示各个文化模块
        demo_performance_culture()
        demo_observability_culture()
        demo_data_governance_culture()
        demo_accessibility_culture()
        demo_alerting_system()
        demo_comprehensive_enforcement()

        print("\n🎉 演示完成！")
        print("=" * 60)
        print("🏆 AICultureKit 现在包含完整的开发文化体系:")
        print("   ✅ 性能文化 - 基准测试、内存监控、响应时间追踪")
        print("   ✅ 可观测性文化 - 结构化日志、指标收集、分布式追踪")
        print("   ✅ 数据治理文化 - 隐私保护、质量验证、合规检查")
        print("   ✅ 可访问性文化 - 无障碍设计、国际化、响应式设计")
        print("   ✅ 智能告警系统 - 自动化监控、智能告警、规则管理")
        print("   ✅ 综合执行器 - 统一的文化原则执行和报告")

        print("\n💡 这是一个真正完整的AI时代开发文化标杆项目！")

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
