"""
性能文化模块 - 性能基准测试、回归检测、内存监控

提供全面的性能文化保障，包括：
1. 性能基准测试框架
2. 性能回归检测
3. 内存泄漏检测
4. 响应时间监控
5. 性能优化建议
"""

import json
import threading
import time
import tracemalloc
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil


@dataclass
class PerformanceBenchmark:
    """性能基准数据"""

    name: str
    category: str  # api, function, database, file_io
    baseline_time: float  # 基准执行时间(秒)
    baseline_memory: int  # 基准内存使用(字节)
    threshold_multiplier: float = 2.0  # 阈值倍数
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)


@dataclass
class PerformanceResult:
    """性能测试结果"""

    benchmark_name: str
    execution_time: float
    memory_usage: int
    cpu_usage: float
    is_regression: bool
    regression_factor: float
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)


class PerformanceProfiler:
    """性能分析器"""

    def __init__(self):
        """__init__函数"""
        self.active_profiles = {}
        self.results = []

    def start_profiling(self, name: str) -> None:
        """开始性能分析"""
        tracemalloc.start()
        self.active_profiles[name] = {
            'start_time': time.perf_counter(),
            'start_memory': tracemalloc.get_traced_memory()[0],
            'process': psutil.Process(),
            'cpu_start': psutil.cpu_percent(),
        }

    def stop_profiling(self, name: str) -> PerformanceResult:
        """停止性能分析并返回结果"""
        if name not in self.active_profiles:
            raise ValueError(f"No active profile found for {name}")

        profile = self.active_profiles[name]
        end_time = time.perf_counter()
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        execution_time = end_time - profile['start_time']
        memory_usage = peak_memory - profile['start_memory']
        cpu_usage = psutil.cpu_percent() - profile['cpu_start']

        result = PerformanceResult(
            benchmark_name=name,
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            is_regression=False,  # 将由基准比较确定
            regression_factor=1.0,
            details={
                'peak_memory': peak_memory,
                'current_memory': current_memory,
                'process_memory': profile['process'].memory_info().rss,
            },
        )

        del self.active_profiles[name]
        self.results.append(result)
        return result


class PerformanceBenchmarkManager:
    """性能基准管理器"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.benchmarks_file = (
            project_path / ".aiculture" / "performance_benchmarks.json"
        )
        self.results_file = project_path / ".aiculture" / "performance_results.json"
        self.benchmarks: Dict[str, PerformanceBenchmark] = {}
        self.profiler = PerformanceProfiler()
        self._load_benchmarks()

    def _load_benchmarks(self) -> None:
        """加载性能基准数据"""
        if self.benchmarks_file.exists():
            try:
                with open(self.benchmarks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, benchmark_data in data.items():
                        self.benchmarks[name] = PerformanceBenchmark(**benchmark_data)
            except Exception as e:
                print(f"加载性能基准数据失败: {e}")

    def _save_benchmarks(self) -> None:
        """保存性能基准数据"""
        self.benchmarks_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.benchmarks_file, 'w', encoding='utf-8') as f:
            data = {
                name: {
                    'name': b.name,
                    'category': b.category,
                    'baseline_time': b.baseline_time,
                    'baseline_memory': b.baseline_memory,
                    'threshold_multiplier': b.threshold_multiplier,
                    'created_at': b.created_at,
                    'last_updated': b.last_updated,
                }
                for name, b in self.benchmarks.items()
            }
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_benchmark(
        self, name: str, category: str, func: Callable, *args, **kwargs
    ) -> PerformanceBenchmark:
        """创建性能基准"""
        print(f"🏃 创建性能基准: {name}")

        # 运行多次取平均值
        times = []
        memories = []

        for i in range(3):
            self.profiler.start_profiling(f"{name}_baseline_{i}")
            func(*args, **kwargs)
            result = self.profiler.stop_profiling(f"{name}_baseline_{i}")
            times.append(result.execution_time)
            memories.append(result.memory_usage)

        baseline_time = sum(times) / len(times)
        baseline_memory = sum(memories) / len(memories)

        benchmark = PerformanceBenchmark(
            name=name,
            category=category,
            baseline_time=baseline_time,
            baseline_memory=baseline_memory,
        )

        self.benchmarks[name] = benchmark
        self._save_benchmarks()

        print(f"✅ 基准创建完成: {baseline_time:.4f}s, {baseline_memory}bytes")
        return benchmark

    def run_benchmark(
        self, name: str, func: Callable, *args, **kwargs
    ) -> PerformanceResult:
        """运行性能基准测试"""
        if name not in self.benchmarks:
            raise ValueError(f"Benchmark {name} not found")

        benchmark = self.benchmarks[name]

        self.profiler.start_profiling(name)
        func(*args, **kwargs)
        result = self.profiler.stop_profiling(name)

        # 检查是否有性能回归
        time_regression = result.execution_time > (
            benchmark.baseline_time * benchmark.threshold_multiplier
        )
        memory_regression = result.memory_usage > (
            benchmark.baseline_memory * benchmark.threshold_multiplier
        )

        result.is_regression = time_regression or memory_regression
        result.regression_factor = max(
            result.execution_time / benchmark.baseline_time,
            (
                result.memory_usage / benchmark.baseline_memory
                if benchmark.baseline_memory > 0
                else 1.0
            ),
        )

        self._save_result(result)
        return result

    def _save_result(self, result: PerformanceResult) -> None:
        """保存性能测试结果"""
        self.results_file.parent.mkdir(parents=True, exist_ok=True)

        results = []
        if self.results_file.exists():
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
            except Exception:
                results = []

        results.append(
            {
                'benchmark_name': result.benchmark_name,
                'execution_time': result.execution_time,
                'memory_usage': result.memory_usage,
                'cpu_usage': result.cpu_usage,
                'is_regression': result.is_regression,
                'regression_factor': result.regression_factor,
                'timestamp': result.timestamp,
                'details': result.details,
            }
        )

        # 只保留最近100个结果
        results = results[-100:]

        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        if not self.results_file.exists():
            return {'benchmarks': 0, 'regressions': 0, 'results': []}

        with open(self.results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)

        regressions = [r for r in results if r.get('is_regression', False)]

        return {
            'total_benchmarks': len(self.benchmarks),
            'total_results': len(results),
            'regressions': len(regressions),
            'regression_rate': len(regressions) / len(results) if results else 0,
            'recent_results': results[-10:],
            'worst_regressions': sorted(
                regressions, key=lambda x: x.get('regression_factor', 1), reverse=True
            )[:5],
        }


class MemoryLeakDetector:
    """内存泄漏检测器"""

    def __init__(self):
        """__init__函数"""
        self.snapshots = []
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self, interval: int = 60) -> None:
        """开始内存监控"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_memory, args=(interval,), daemon=True
        )
        self.monitor_thread.start()
        print(f"🔍 开始内存监控，间隔: {interval}秒")

    def stop_monitoring(self) -> None:
        """停止内存监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️ 内存监控已停止")

    def _monitor_memory(self, interval: int) -> None:
        """内存监控线程"""
        while self.monitoring:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()

                snapshot = {
                    'timestamp': time.time(),
                    'rss': memory_info.rss,  # 物理内存
                    'vms': memory_info.vms,  # 虚拟内存
                    'percent': process.memory_percent(),
                    'open_files': len(process.open_files()),
                    'connections': len(process.connections()),
                }

                self.snapshots.append(snapshot)

                # 只保留最近1000个快照
                if len(self.snapshots) > 1000:
                    self.snapshots = self.snapshots[-1000:]

                time.sleep(interval)

            except Exception as e:
                print(f"内存监控错误: {e}")
                time.sleep(interval)

    def detect_leaks(self) -> Dict[str, Any]:
        """检测内存泄漏"""
        if len(self.snapshots) < 10:
            return {
                'status': 'insufficient_data',
                'message': '数据不足，无法检测内存泄漏',
            }

        # 分析内存趋势
        recent_snapshots = self.snapshots[-50:]  # 最近50个快照

        rss_values = [s['rss'] for s in recent_snapshots]
        vms_values = [s['vms'] for s in recent_snapshots]

        # 计算内存增长趋势
        rss_trend = self._calculate_trend(rss_values)
        vms_trend = self._calculate_trend(vms_values)

        # 检测异常增长
        leak_detected = False
        warnings = []

        if rss_trend > 1024 * 1024:  # 1MB/分钟增长
            leak_detected = True
            warnings.append(f"物理内存持续增长: {rss_trend / 1024 / 1024:.2f}MB/分钟")

        if vms_trend > 10 * 1024 * 1024:  # 10MB/分钟增长
            leak_detected = True
            warnings.append(f"虚拟内存持续增长: {vms_trend / 1024 / 1024:.2f}MB/分钟")

        return {
            'status': 'leak_detected' if leak_detected else 'normal',
            'rss_trend': rss_trend,
            'vms_trend': vms_trend,
            'warnings': warnings,
            'current_memory': recent_snapshots[-1] if recent_snapshots else None,
            'snapshots_analyzed': len(recent_snapshots),
        }

    def _calculate_trend(self, values: List[float]) -> float:
        """计算趋势（简单线性回归斜率）"""
        if len(values) < 2:
            return 0

        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))

        # 计算斜率
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope


def performance_benchmark(name: str, category: str = "function"):
    """性能基准装饰器"""

    def decorator(func: Callable):
        """decorator函数"""

        def wrapper(*args, **kwargs):
            """wrapper函数"""
            # 这里可以集成到全局的性能管理器中
            return func(*args, **kwargs)

        wrapper._performance_benchmark = {'name': name, 'category': category}
        return wrapper

    return decorator


# 使用示例
if __name__ == "__main__":
    # 示例用法
    manager = PerformanceBenchmarkManager(Path("."))

    @performance_benchmark("test_function", "function")
    def test_function():
        """test_function函数"""
        time.sleep(0.1)
        return sum(range(1000))

    # 创建基准
    manager.create_benchmark("test_function", "function", test_function)

    # 运行测试
    result = manager.run_benchmark("test_function", test_function)
    print(f"性能测试结果: {result}")

    # 获取报告
    report = manager.get_performance_report()
    print(f"性能报告: {report}")
