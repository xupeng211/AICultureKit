#!/usr/bin/env python3
"""
错误处理和日志记录系统演示

展示如何使用AICultureKit的统一错误处理和日志记录功能。
"""

import random
import time
from pathlib import Path

# 添加项目根目录到Python路径
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from aiculture.error_handling import (
    # 异常类
    ValidationError,
    ProcessingError,
    ResourceError,
    
    # 日志系统
    setup_logging,
    get_logger,
    LogLevel,
    
    # 错误处理
    with_error_handling,
    RetryConfig,
    FallbackConfig,
    handle_errors,
    
    # 监控
    get_error_monitor,
    get_performance_tracker,
    get_monitoring_manager
)


def setup_demo_logging():
    """设置演示日志"""
    setup_logging(
        service="error_handling_demo",
        version="1.0.0",
        structured=True,
        level=LogLevel.INFO
    )


# 模拟一些可能失败的操作
def unreliable_network_call(success_rate: float = 0.7) -> dict:
    """模拟不可靠的网络调用"""
    if random.random() > success_rate:
        raise ConnectionError("网络连接失败")
    
    # 模拟网络延迟
    time.sleep(random.uniform(0.1, 0.5))
    
    return {"status": "success", "data": "网络数据"}


def validate_user_input(data: dict) -> dict:
    """验证用户输入"""
    if not data:
        raise ValidationError("输入数据不能为空", field="data")
    
    if "name" not in data:
        raise ValidationError("缺少必需字段", field="name", expected_type="string")
    
    if len(data["name"]) < 2:
        raise ValidationError(
            "名称太短",
            field="name",
            value=data["name"],
            expected_type="string with length >= 2"
        )
    
    return data


def process_file(file_path: str) -> dict:
    """处理文件"""
    path = Path(file_path)
    
    if not path.exists():
        raise ResourceError(
            "文件不存在",
            resource_type="file",
            resource_path=str(path)
        )
    
    # 模拟处理时间
    time.sleep(random.uniform(0.2, 1.0))
    
    if random.random() > 0.8:
        raise ProcessingError(
            "文件处理失败",
            operation="file_processing",
            file_path=str(path)
        )
    
    return {"processed": True, "file": str(path)}


# 使用错误处理装饰器的示例
@with_error_handling(
    retry_config=RetryConfig(max_attempts=3, base_delay=0.5),
    fallback_config=FallbackConfig(fallback_value={"status": "fallback", "data": None})
)
def robust_network_call() -> dict:
    """带重试和降级的网络调用"""
    return unreliable_network_call(success_rate=0.3)  # 低成功率，触发重试


def demo_basic_logging():
    """演示基本日志功能"""
    print("\n=== 基本日志功能演示 ===")
    
    logger = get_logger("demo.basic")
    
    # 设置上下文
    logger.set_context(
        user_id="user123",
        request_id="req456",
        component="demo"
    )
    
    logger.info("开始演示基本日志功能")
    logger.debug("这是调试信息", extra_data="debug_value")
    logger.warning("这是警告信息", warning_type="demo")
    
    try:
        raise ValueError("这是一个示例错误")
    except Exception as e:
        logger.error("捕获到错误", error=e, operation="demo_operation")
    
    logger.info("基本日志功能演示完成")


def demo_operation_context():
    """演示操作上下文"""
    print("\n=== 操作上下文演示 ===")
    
    logger = get_logger("demo.context")
    
    with logger.operation_context("user_registration", user_type="new"):
        logger.info("开始用户注册流程")
        
        # 模拟一些操作
        time.sleep(0.1)
        logger.info("验证用户信息")
        
        time.sleep(0.1)
        logger.info("创建用户账户")
        
        time.sleep(0.1)
        logger.info("发送欢迎邮件")


def demo_error_handling():
    """演示错误处理"""
    print("\n=== 错误处理演示 ===")
    
    logger = get_logger("demo.error_handling")
    error_monitor = get_error_monitor("demo")
    
    # 1. 基本错误处理
    try:
        validate_user_input({})
    except ValidationError as e:
        logger.error("验证失败", error=e)
        error_monitor.record_error(e, operation="user_validation")
    
    # 2. 带重试的网络调用
    try:
        result = robust_network_call()
        logger.info("网络调用成功", result=result)
    except Exception as e:
        logger.error("网络调用最终失败", error=e)
        error_monitor.record_error(e, operation="network_call")
    
    # 3. 使用错误处理上下文
    try:
        with handle_errors("file_processing_batch"):
            # 处理多个文件
            files = ["file1.txt", "file2.txt", "nonexistent.txt"]
            for file_path in files:
                try:
                    result = process_file(file_path)
                    logger.info(f"文件处理成功: {file_path}", result=result)
                except Exception as e:
                    logger.warning(f"文件处理失败: {file_path}", error=e)
                    error_monitor.record_error(e, operation="file_processing", context={"file": file_path})
    except Exception as e:
        logger.error("批处理失败", error=e)


def demo_performance_monitoring():
    """演示性能监控"""
    print("\n=== 性能监控演示 ===")
    
    logger = get_logger("demo.performance")
    performance_tracker = get_performance_tracker("demo")
    
    # 模拟一些操作
    operations = [
        ("fast_operation", 0.1),
        ("medium_operation", 0.5),
        ("slow_operation", 1.2),  # 超过慢操作阈值
        ("very_slow_operation", 2.0)
    ]
    
    for op_name, duration in operations:
        start_time = time.perf_counter()
        
        with logger.operation_context(op_name):
            time.sleep(duration)
            
            actual_duration = (time.perf_counter() - start_time) * 1000
            performance_tracker.record_operation(
                operation=op_name,
                duration_ms=actual_duration,
                status="success"
            )


def demo_monitoring_dashboard():
    """演示监控仪表板"""
    print("\n=== 监控仪表板演示 ===")
    
    monitoring_manager = get_monitoring_manager()
    
    # 获取整体指标
    metrics = monitoring_manager.get_overall_metrics()
    
    print("📊 错误指标:")
    for name, error_metrics in metrics['error_metrics'].items():
        print(f"  监控器: {name}")
        print(f"    总错误数: {error_metrics.total_errors}")
        print(f"    错误率: {error_metrics.error_rate:.2f}/分钟")
        print(f"    按类型分布: {error_metrics.errors_by_type}")
        print(f"    按严重程度分布: {error_metrics.errors_by_severity}")
    
    print("\n🚀 性能指标:")
    for name, perf_metrics in metrics['performance_metrics'].items():
        print(f"  跟踪器: {name}")
        print(f"    总操作数: {perf_metrics.total_operations}")
        print(f"    平均响应时间: {perf_metrics.avg_response_time:.2f}ms")
        print(f"    P95响应时间: {perf_metrics.p95_response_time:.2f}ms")
        print(f"    P99响应时间: {perf_metrics.p99_response_time:.2f}ms")
        print(f"    每秒操作数: {perf_metrics.operations_per_second:.2f}")
        print(f"    慢操作数: {len(perf_metrics.slow_operations)}")
    
    # 健康检查
    health = monitoring_manager.check_health()
    print(f"\n🏥 系统健康状态: {health['status']}")
    if health['issues']:
        print("  发现的问题:")
        for issue in health['issues']:
            print(f"    - {issue['type']}: {issue}")


def main():
    """主函数"""
    print("🚀 AICultureKit 错误处理和日志记录系统演示")
    
    # 设置日志
    setup_demo_logging()
    
    # 运行各种演示
    demo_basic_logging()
    demo_operation_context()
    demo_error_handling()
    demo_performance_monitoring()
    demo_monitoring_dashboard()
    
    print("\n✅ 演示完成！")
    print("\n💡 要点总结:")
    print("1. 使用结构化日志记录，便于分析和监控")
    print("2. 统一的异常类型，提供丰富的错误信息")
    print("3. 智能重试和降级机制，提高系统可靠性")
    print("4. 实时错误和性能监控，及时发现问题")
    print("5. 操作上下文跟踪，便于问题排查")


if __name__ == "__main__":
    main()
