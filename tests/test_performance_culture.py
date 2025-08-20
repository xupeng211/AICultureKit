"""
性能文化模块测试
"""

import time
import tempfile
from pathlib import Path
import pytest

from aiculture.performance_culture import (
    PerformanceBenchmarkManager,
    MemoryLeakDetector,
    PerformanceProfiler,
    PerformanceBenchmark,
    PerformanceResult,
)


class TestPerformanceProfiler:
    """性能分析器测试"""

    def test_profiler_basic_functionality(self):
        """测试基本性能分析功能"""
        profiler = PerformanceProfiler()

        # 开始分析
        profiler.start_profiling("test_operation")

        # 模拟一些工作
        time.sleep(0.01)
        result = [i for i in range(100)]

        # 停止分析
        performance_result = profiler.stop_profiling("test_operation")

        # 验证结果
        assert isinstance(performance_result, PerformanceResult)
        assert performance_result.benchmark_name == "test_operation"
        assert performance_result.execution_time > 0
        assert performance_result.memory_usage >= 0
        assert len(profiler.results) == 1

    def test_profiler_multiple_operations(self):
        """测试多个操作的性能分析"""
        profiler = PerformanceProfiler()

        # 分析多个操作
        operations = ["op1", "op2", "op3"]
        for op in operations:
            profiler.start_profiling(op)
            time.sleep(0.005)
            profiler.stop_profiling(op)

        assert len(profiler.results) == 3
        for i, result in enumerate(profiler.results):
            assert result.benchmark_name == operations[i]

    def test_profiler_error_handling(self):
        """测试错误处理"""
        profiler = PerformanceProfiler()

        # 尝试停止未开始的分析
        with pytest.raises(ValueError):
            profiler.stop_profiling("nonexistent")


class TestPerformanceBenchmarkManager:
    """性能基准管理器测试"""

    def setup_method(self):
        """测试设置"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = PerformanceBenchmarkManager(self.temp_dir)

    def teardown_method(self):
        """测试清理"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_create_benchmark(self):
        """测试创建性能基准"""

        def sample_function():
            """sample_function函数"""
            return sum(range(100))

        benchmark = self.manager.create_benchmark("sample_function", "function", sample_function)

        assert isinstance(benchmark, PerformanceBenchmark)
        assert benchmark.name == "sample_function"
        assert benchmark.category == "function"
        assert benchmark.baseline_time > 0
        assert benchmark.baseline_memory >= 0
        assert "sample_function" in self.manager.benchmarks

    def test_run_benchmark(self):
        """测试运行基准测试"""

        def sample_function():
            """sample_function函数"""
            return sum(range(100))

        # 先创建基准
        self.manager.create_benchmark("sample_function", "function", sample_function)

        # 运行基准测试
        result = self.manager.run_benchmark("sample_function", sample_function)

        assert isinstance(result, PerformanceResult)
        assert result.benchmark_name == "sample_function"
        assert result.execution_time > 0
        assert isinstance(result.is_regression, bool)
        assert result.regression_factor >= 1.0

    def test_benchmark_persistence(self):
        """测试基准数据持久化"""

        def sample_function():
            """sample_function函数"""
            return sum(range(50))

        # 创建基准
        self.manager.create_benchmark("persistent_test", "function", sample_function)

        # 创建新的管理器实例
        new_manager = PerformanceBenchmarkManager(self.temp_dir)

        # 验证基准数据被加载
        assert "persistent_test" in new_manager.benchmarks
        assert new_manager.benchmarks["persistent_test"].name == "persistent_test"

    def test_performance_report(self):
        """测试性能报告生成"""

        def sample_function():
            """sample_function函数"""
            return sum(range(50))

        # 创建基准并运行测试
        self.manager.create_benchmark("report_test", "function", sample_function)
        self.manager.run_benchmark("report_test", sample_function)

        # 获取报告
        report = self.manager.get_performance_report()

        assert isinstance(report, dict)
        assert "total_benchmarks" in report
        assert "total_results" in report
        assert "regressions" in report
        assert report["total_benchmarks"] >= 1


class TestMemoryLeakDetector:
    """内存泄漏检测器测试"""

    def test_detector_initialization(self):
        """测试检测器初始化"""
        detector = MemoryLeakDetector()

        assert detector.snapshots == []
        assert detector.monitoring is False
        assert detector.monitor_thread is None

    def test_monitoring_lifecycle(self):
        """测试监控生命周期"""
        detector = MemoryLeakDetector()

        # 开始监控
        detector.start_monitoring(interval=1)
        assert detector.monitoring is True
        assert detector.monitor_thread is not None

        # 等待一些快照
        time.sleep(2.5)

        # 停止监控
        detector.stop_monitoring()
        assert detector.monitoring is False

        # 应该有一些快照
        assert len(detector.snapshots) >= 1

    def test_leak_detection_insufficient_data(self):
        """测试数据不足时的泄漏检测"""
        detector = MemoryLeakDetector()

        result = detector.detect_leaks()

        assert result["status"] == "insufficient_data"
        assert "message" in result

    def test_trend_calculation(self):
        """测试趋势计算"""
        detector = MemoryLeakDetector()

        # 测试空列表
        trend = detector._calculate_trend([])
        assert trend == 0

        # 测试单个值
        trend = detector._calculate_trend([100])
        assert trend == 0

        # 测试递增趋势
        trend = detector._calculate_trend([100, 110, 120, 130])
        assert trend > 0

        # 测试递减趋势
        trend = detector._calculate_trend([130, 120, 110, 100])
        assert trend < 0


class TestPerformanceBenchmark:
    """性能基准数据结构测试"""

    def test_benchmark_creation(self):
        """测试基准创建"""
        benchmark = PerformanceBenchmark(
            name="test_benchmark", category="function", baseline_time=0.1, baseline_memory=1024
        )

        assert benchmark.name == "test_benchmark"
        assert benchmark.category == "function"
        assert benchmark.baseline_time == 0.1
        assert benchmark.baseline_memory == 1024
        assert benchmark.threshold_multiplier == 2.0
        assert benchmark.created_at > 0
        assert benchmark.last_updated > 0


class TestPerformanceResult:
    """性能结果数据结构测试"""

    def test_result_creation(self):
        """测试结果创建"""
        result = PerformanceResult(
            benchmark_name="test_result",
            execution_time=0.05,
            memory_usage=512,
            cpu_usage=10.5,
            is_regression=False,
            regression_factor=1.2,
        )

        assert result.benchmark_name == "test_result"
        assert result.execution_time == 0.05
        assert result.memory_usage == 512
        assert result.cpu_usage == 10.5
        assert result.is_regression is False
        assert result.regression_factor == 1.2
        assert result.timestamp > 0
        assert isinstance(result.details, dict)


# 集成测试
class TestPerformanceCultureIntegration:
    """性能文化集成测试"""

    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # 创建管理器
            manager = PerformanceBenchmarkManager(temp_dir)

            # 定义测试函数
            def cpu_intensive_task():
                """cpu_intensive_task函数"""
                return sum(i * i for i in range(1000))

            def memory_intensive_task():
                """memory_intensive_task函数"""
                data = [i for i in range(10000)]
                return len(data)

            # 创建基准
            cpu_benchmark = manager.create_benchmark("cpu_task", "function", cpu_intensive_task)
            memory_benchmark = manager.create_benchmark(
                "memory_task", "function", memory_intensive_task
            )

            # 运行基准测试
            cpu_result = manager.run_benchmark("cpu_task", cpu_intensive_task)
            memory_result = manager.run_benchmark("memory_task", memory_intensive_task)

            # 验证结果
            assert cpu_result.benchmark_name == "cpu_task"
            assert memory_result.benchmark_name == "memory_task"

            # 获取报告
            report = manager.get_performance_report()
            assert report["total_benchmarks"] == 2
            assert report["total_results"] == 2

        finally:
            import shutil

            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
