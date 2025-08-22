"""
可观测性文化模块测试
"""

import json
import tempfile
from pathlib import Path

import pytest

from aiculture.observability_culture import (
    DistributedTracer,
    LogLevel,
    MetricsCollector,
    MetricType,
    ObservabilityManager,
    StructuredLogger,
)


class TestStructuredLogger:
    """结构化日志器测试"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.logger = StructuredLogger("test_app", self.temp_dir)

    def teardown_method(self):
        """测试清理"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_logger_initialization(self):
        """测试日志器初始化"""
        assert self.logger.app_name == "test_app"
        assert self.logger.log_dir == self.temp_dir
        assert self.logger.log_file.exists()

    def test_log_levels(self):
        """测试不同日志级别"""
        # 测试各种日志级别
        self.logger.debug("Debug message", {"key": "value"})
        self.logger.info("Info message", {"user_id": 123})
        self.logger.warning("Warning message", {"error_code": "W001"})
        self.logger.error("Error message", {"exception": "ValueError"})
        self.logger.critical("Critical message", {"system": "database"})

        # 读取日志文件验证
        with open(self.logger.log_file, "r") as f:
            logs = f.readlines()

        assert len(logs) >= 5

        # 验证日志格式
        for log_line in logs:
            log_data = json.loads(log_line.strip())
            assert "timestamp" in log_data
            assert "level" in log_data
            assert "message" in log_data
            assert "app_name" in log_data
            assert log_data["app_name"] == "test_app"

    def test_structured_logging(self):
        """测试结构化日志"""
        context = {
            "user_id": 12345,
            "request_id": "req-abc-123",
            "operation": "user_login",
            "ip_address": "192.168.1.xxx",
        }

        self.logger.info("User login successful", context)

        # 验证日志内容
        with open(self.logger.log_file, "r") as f:
            log_line = f.readline().strip()

        log_data = json.loads(log_line)
        assert log_data["message"] == "User login successful"
        assert log_data["context"]["user_id"] == 12345
        assert log_data["context"]["request_id"] == "req-abc-123"

    def test_log_filtering(self):
        """测试日志过滤"""
        # 设置最小日志级别为WARNING
        self.logger.min_level = LogLevel.WARNING

        self.logger.debug("Debug message")  # 应该被过滤
        self.logger.info("Info message")  # 应该被过滤
        self.logger.warning("Warning message")  # 应该记录
        self.logger.error("Error message")  # 应该记录

        # 验证只有WARNING和ERROR被记录
        with open(self.logger.log_file, "r") as f:
            logs = f.readlines()

        assert len(logs) == 2

        log1 = json.loads(logs[0].strip())
        log2 = json.loads(logs[1].strip())

        assert log1["level"] == "WARNING"
        assert log2["level"] == "ERROR"


class TestMetricsCollector:
    """指标收集器测试"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.collector = MetricsCollector("test_app", self.temp_dir)

    def teardown_method(self):
        """测试清理"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_collector_initialization(self):
        """测试收集器初始化"""
        assert self.collector.app_name == "test_app"
        assert self.collector.metrics_dir == self.temp_dir
        assert isinstance(self.collector.metrics, dict)

    def test_counter_metrics(self):
        """测试计数器指标"""
        # 记录计数器指标
        self.collector.record_metric("user_logins", MetricType.COUNTER, 1)
        self.collector.record_metric("user_logins", MetricType.COUNTER, 1)
        self.collector.record_metric("user_logins", MetricType.COUNTER, 3)

        # 验证指标
        assert "user_logins" in self.collector.metrics
        metric = self.collector.metrics["user_logins"]
        assert metric["type"] == MetricType.COUNTER
        assert metric["value"] == 5  # 1 + 1 + 3

    def test_gauge_metrics(self):
        """测试仪表盘指标"""
        # 记录仪表盘指标
        self.collector.record_metric("cpu_usage", MetricType.GAUGE, 45.5)
        self.collector.record_metric("cpu_usage", MetricType.GAUGE, 67.2)
        self.collector.record_metric("cpu_usage", MetricType.GAUGE, 23.8)

        # 验证指标（仪表盘指标保存最后一个值）
        metric = self.collector.metrics["cpu_usage"]
        assert metric["type"] == MetricType.GAUGE
        assert metric["value"] == 23.8

    def test_histogram_metrics(self):
        """测试直方图指标"""
        # 记录直方图指标
        response_times = [0.1, 0.2, 0.15, 0.3, 0.25, 0.18, 0.22]
        for time_val in response_times:
            self.collector.record_metric("response_time", MetricType.HISTOGRAM, time_val)

        # 验证指标
        metric = self.collector.metrics["response_time"]
        assert metric["type"] == MetricType.HISTOGRAM
        assert len(metric["values"]) == len(response_times)
        assert metric["count"] == len(response_times)

    def test_metrics_export(self):
        """测试指标导出"""
        # 记录一些指标
        self.collector.record_metric("requests", MetricType.COUNTER, 10)
        self.collector.record_metric("memory_usage", MetricType.GAUGE, 1024)

        # 导出指标
        exported_metrics = self.collector.export_metrics()

        assert isinstance(exported_metrics, dict)
        assert "requests" in exported_metrics
        assert "memory_usage" in exported_metrics
        assert exported_metrics["requests"]["value"] == 10
        assert exported_metrics["memory_usage"]["value"] == 1024

    def test_metrics_persistence(self):
        """测试指标持久化"""
        # 记录指标
        self.collector.record_metric("test_metric", MetricType.COUNTER, 42)

        # 保存指标
        self.collector.save_metrics()

        # 创建新的收集器实例
        new_collector = MetricsCollector("test_app", self.temp_dir)

        # 验证指标被加载
        assert "test_metric" in new_collector.metrics
        assert new_collector.metrics["test_metric"]["value"] == 42


class TestDistributedTracer:
    """分布式追踪器测试"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.tracer = DistributedTracer("test_service", self.temp_dir)

    def teardown_method(self):
        """测试清理"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_tracer_initialization(self):
        """测试追踪器初始化"""
        assert self.tracer.service_name == "test_service"
        assert self.tracer.traces_dir == self.temp_dir
        assert isinstance(self.tracer.active_spans, dict)

    def test_span_lifecycle(self):
        """测试Span生命周期"""
        # 开始Span
        span_id = self.tracer.start_span("user_operation", {"user_id": 123})

        assert span_id in self.tracer.active_spans
        span = self.tracer.active_spans[span_id]
        assert span["operation_name"] == "user_operation"
        assert span["context"]["user_id"] == 123
        assert span["start_time"] > 0

        # 添加标签
        self.tracer.add_span_tag(span_id, "status", "processing")
        assert span["tags"]["status"] == "processing"

        # 添加日志
        self.tracer.add_span_log(span_id, "Processing user data")
        assert len(span["logs"]) == 1

        # 结束Span
        self.tracer.finish_span(span_id)

        assert span_id not in self.tracer.active_spans
        assert span["end_time"] > span["start_time"]
        assert span["duration"] > 0

    def test_nested_spans(self):
        """测试嵌套Span"""
        # 创建父Span
        parent_span_id = self.tracer.start_span("parent_operation")

        # 创建子Span
        child_span_id = self.tracer.start_span("child_operation", parent_span_id=parent_span_id)

        # 验证父子关系
        child_span = self.tracer.active_spans[child_span_id]
        assert child_span["parent_span_id"] == parent_span_id

        # 结束Span
        self.tracer.finish_span(child_span_id)
        self.tracer.finish_span(parent_span_id)

    def test_trace_export(self):
        """测试追踪导出"""
        # 创建一些Span
        span1_id = self.tracer.start_span("operation1")
        span2_id = self.tracer.start_span("operation2")

        self.tracer.finish_span(span1_id)
        self.tracer.finish_span(span2_id)

        # 导出追踪
        traces = self.tracer.export_traces()

        assert isinstance(traces, list)
        assert len(traces) == 2

        for trace in traces:
            assert "span_id" in trace
            assert "operation_name" in trace
            assert "start_time" in trace
            assert "end_time" in trace
            assert "duration" in trace


class TestObservabilityManager:
    """可观测性管理器测试"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = ObservabilityManager("test_app", self.temp_dir)

    def teardown_method(self):
        """测试清理"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager.app_name == "test_app"
        assert self.manager.base_dir == self.temp_dir
        assert isinstance(self.manager.logger, StructuredLogger)
        assert isinstance(self.manager.metrics, MetricsCollector)
        assert isinstance(self.manager.tracer, DistributedTracer)

    def test_integrated_logging_and_metrics(self):
        """测试集成的日志和指标"""
        # 记录一个操作
        self.manager.logger.info("Operation started", {"operation": "test"})
        self.manager.metrics.record_metric("operations", MetricType.COUNTER, 1)

        # 验证日志
        with open(self.manager.logger.log_file, "r") as f:
            log_line = f.readline().strip()

        log_data = json.loads(log_line)
        assert log_data["message"] == "Operation started"

        # 验证指标
        assert self.manager.metrics.metrics["operations"]["value"] == 1

    def test_comprehensive_observability(self):
        """测试综合可观测性"""
        # 开始追踪
        span_id = self.manager.tracer.start_span("comprehensive_test")

        # 记录日志
        self.manager.logger.info("Test operation", {"span_id": span_id})

        # 记录指标
        self.manager.metrics.record_metric("test_counter", MetricType.COUNTER, 1)
        self.manager.metrics.record_metric("test_gauge", MetricType.GAUGE, 42.5)

        # 结束追踪
        self.manager.tracer.finish_span(span_id)

        # 验证所有组件都有数据
        assert len(self.manager.metrics.metrics) == 2
        assert len(self.manager.tracer.completed_spans) == 1

        # 验证日志文件存在且有内容
        assert self.manager.logger.log_file.exists()
        assert self.manager.logger.log_file.stat().st_size > 0


# 集成测试
class TestObservabilityCultureIntegration:
    """可观测性文化集成测试"""

    def test_end_to_end_observability(self):
        """测试端到端可观测性"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            manager = ObservabilityManager("integration_test", temp_dir)

            # 模拟一个完整的操作流程
            span_id = manager.tracer.start_span("user_registration")

            # 记录开始日志
            manager.logger.info(
                "User registration started",
                {"span_id": span_id, "user_email": "demo@placeholder.local"},
            )

            # 记录指标
            manager.metrics.record_metric("registrations", MetricType.COUNTER, 1)
            manager.metrics.record_metric("active_users", MetricType.GAUGE, 150)

            # 添加追踪标签
            manager.tracer.add_span_tag(span_id, "user_type", "premium")
            manager.tracer.add_span_log(span_id, "Validating user data")

            # 记录成功日志
            manager.logger.info(
                "User registration completed", {"span_id": span_id, "status": "success"}
            )

            # 结束追踪
            manager.tracer.finish_span(span_id)

            # 验证所有数据都被正确记录
            assert manager.metrics.metrics["registrations"]["value"] == 1
            assert manager.metrics.metrics["active_users"]["value"] == 150
            assert len(manager.tracer.completed_spans) == 1

            # 验证日志文件
            with open(manager.logger.log_file, "r") as f:
                logs = f.readlines()

            assert len(logs) == 2

        finally:
            import shutil

            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
