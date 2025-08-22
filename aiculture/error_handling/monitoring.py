"""错误监控和性能跟踪

提供错误统计、性能监控和告警功能。
"""

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

from .exceptions import AICultureError, get_error_severity
from .logging_system import get_logger


@dataclass
class ErrorMetrics:
    """错误指标"""

    total_errors: int = 0
    error_rate: float = 0.0  # 错误率（每分钟）
    errors_by_type: dict[str, int] = field(default_factory=dict)
    errors_by_severity: dict[str, int] = field(default_factory=dict)
    recent_errors: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class PerformanceMetrics:
    """性能指标"""

    total_operations: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    operations_per_second: float = 0.0
    slow_operations: list[dict[str, Any]] = field(default_factory=list)


class ErrorMonitor:
    """错误监控器"""

    def __init__(self, name: str = "default", window_size: int = 1000):
        self.name = name
        self.window_size = window_size
        self.logger = get_logger(f"error_monitor.{name}")

        # 错误统计
        self._error_count = 0
        self._errors_by_type = defaultdict(int)
        self._errors_by_severity = defaultdict(int)
        self._recent_errors = deque(maxlen=window_size)

        # 时间窗口统计
        self._error_timestamps = deque(maxlen=window_size)

        # 线程锁
        self._lock = threading.Lock()

    def record_error(
        self,
        error: Exception,
        operation: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """记录错误"""
        with self._lock:
            timestamp = time.time()
            error_type = error.__class__.__name__
            severity = get_error_severity(error)

            # 更新统计
            self._error_count += 1
            self._errors_by_type[error_type] += 1
            self._errors_by_severity[severity] += 1
            self._error_timestamps.append(timestamp)

            # 记录详细信息
            error_info = {
                "timestamp": timestamp,
                "type": error_type,
                "severity": severity,
                "message": str(error),
                "operation": operation,
                "context": context or {},
            }

            # 如果是自定义异常，添加更多信息
            if isinstance(error, AICultureError):
                error_info.update(error.to_dict())

            self._recent_errors.append(error_info)

            # 记录日志
            self.logger.error(
                f"记录错误: {error_type}",
                error=error,
                operation=operation,
                severity=severity,
                **(context or {}),
            )

    def get_error_rate(self, window_minutes: int = 5) -> float:
        """获取错误率（每分钟错误数）"""
        with self._lock:
            current_time = time.time()
            window_start = current_time - (window_minutes * 60)

            recent_errors = [ts for ts in self._error_timestamps if ts >= window_start]

            if not recent_errors:
                return 0.0

            return len(recent_errors) / window_minutes

    def get_metrics(self) -> ErrorMetrics:
        """获取错误指标"""
        with self._lock:
            return ErrorMetrics(
                total_errors=self._error_count,
                error_rate=self.get_error_rate(),
                errors_by_type=dict(self._errors_by_type),
                errors_by_severity=dict(self._errors_by_severity),
                recent_errors=list(self._recent_errors)[-10:],  # 最近10个错误
            )

    def reset_metrics(self) -> None:
        """重置指标"""
        with self._lock:
            self._error_count = 0
            self._errors_by_type.clear()
            self._errors_by_severity.clear()
            self._recent_errors.clear()
            self._error_timestamps.clear()


class PerformanceTracker:
    """性能跟踪器"""

    def __init__(self, name: str = "default", window_size: int = 1000):
        self.name = name
        self.window_size = window_size
        self.logger = get_logger(f"performance_tracker.{name}")

        # 性能统计
        self._operation_count = 0
        self._response_times = deque(maxlen=window_size)
        self._operation_timestamps = deque(maxlen=window_size)
        self._slow_operations = deque(maxlen=100)  # 保留最近100个慢操作

        # 配置
        self.slow_threshold_ms = 1000  # 慢操作阈值（毫秒）

        # 线程锁
        self._lock = threading.Lock()

    def record_operation(
        self,
        operation: str,
        duration_ms: float,
        status: str = "success",
        context: dict[str, Any] | None = None,
    ) -> None:
        """记录操作性能"""
        with self._lock:
            timestamp = time.time()

            # 更新统计
            self._operation_count += 1
            self._response_times.append(duration_ms)
            self._operation_timestamps.append(timestamp)

            # 记录慢操作
            if duration_ms > self.slow_threshold_ms:
                slow_op_info = {
                    "timestamp": timestamp,
                    "operation": operation,
                    "duration_ms": duration_ms,
                    "status": status,
                    "context": context or {},
                }
                self._slow_operations.append(slow_op_info)

                # 记录慢操作日志
                self.logger.warning(
                    f"慢操作检测: {operation}",
                    operation=operation,
                    duration_ms=duration_ms,
                    threshold_ms=self.slow_threshold_ms,
                    status=status,
                    **(context or {}),
                )

    def get_operations_per_second(self, window_minutes: int = 5) -> float:
        """获取每秒操作数"""
        with self._lock:
            current_time = time.time()
            window_start = current_time - (window_minutes * 60)

            recent_operations = [
                ts for ts in self._operation_timestamps if ts >= window_start
            ]

            if not recent_operations:
                return 0.0

            return len(recent_operations) / (window_minutes * 60)

    def _calculate_percentile(self, percentile: float) -> float:
        """计算百分位数"""
        if not self._response_times:
            return 0.0

        sorted_times = sorted(self._response_times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def get_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        with self._lock:
            avg_response_time = (
                sum(self._response_times) / len(self._response_times)
                if self._response_times
                else 0.0
            )

            return PerformanceMetrics(
                total_operations=self._operation_count,
                avg_response_time=avg_response_time,
                p95_response_time=self._calculate_percentile(95),
                p99_response_time=self._calculate_percentile(99),
                operations_per_second=self.get_operations_per_second(),
                slow_operations=list(self._slow_operations)[-10:],  # 最近10个慢操作
            )

    def reset_metrics(self) -> None:
        """重置指标"""
        with self._lock:
            self._operation_count = 0
            self._response_times.clear()
            self._operation_timestamps.clear()
            self._slow_operations.clear()


class MonitoringManager:
    """监控管理器"""

    def __init__(self):
        self.error_monitors: dict[str, ErrorMonitor] = {}
        self.performance_trackers: dict[str, PerformanceTracker] = {}
        self.logger = get_logger("monitoring_manager")

    def get_error_monitor(self, name: str = "default") -> ErrorMonitor:
        """获取错误监控器"""
        if name not in self.error_monitors:
            self.error_monitors[name] = ErrorMonitor(name)
        return self.error_monitors[name]

    def get_performance_tracker(self, name: str = "default") -> PerformanceTracker:
        """获取性能跟踪器"""
        if name not in self.performance_trackers:
            self.performance_trackers[name] = PerformanceTracker(name)
        return self.performance_trackers[name]

    def get_overall_metrics(self) -> dict[str, Any]:
        """获取整体指标"""
        metrics = {"error_metrics": {}, "performance_metrics": {}}

        # 收集错误指标
        for name, monitor in self.error_monitors.items():
            metrics["error_metrics"][name] = monitor.get_metrics()

        # 收集性能指标
        for name, tracker in self.performance_trackers.items():
            metrics["performance_metrics"][name] = tracker.get_metrics()

        return metrics

    def check_health(self) -> dict[str, Any]:
        """健康检查"""
        health_status = {
            "status": "healthy",
            "issues": [],
            "metrics": self.get_overall_metrics(),
        }

        # 检查错误率
        for name, monitor in self.error_monitors.items():
            error_rate = monitor.get_error_rate()
            if error_rate > 10:  # 每分钟超过10个错误
                health_status["status"] = "unhealthy"
                health_status["issues"].append(
                    {
                        "type": "high_error_rate",
                        "monitor": name,
                        "error_rate": error_rate,
                    },
                )

        # 检查性能
        for name, tracker in self.performance_trackers.items():
            metrics = tracker.get_metrics()
            if metrics.avg_response_time > 5000:  # 平均响应时间超过5秒
                health_status["status"] = "degraded"
                health_status["issues"].append(
                    {
                        "type": "slow_response",
                        "tracker": name,
                        "avg_response_time": metrics.avg_response_time,
                    },
                )

        return health_status


# 全局监控管理器
_monitoring_manager = MonitoringManager()


def get_error_monitor(name: str = "default") -> ErrorMonitor:
    """获取错误监控器"""
    return _monitoring_manager.get_error_monitor(name)


def get_performance_tracker(name: str = "default") -> PerformanceTracker:
    """获取性能跟踪器"""
    return _monitoring_manager.get_performance_tracker(name)


def get_monitoring_manager() -> MonitoringManager:
    """获取监控管理器"""
    return _monitoring_manager
