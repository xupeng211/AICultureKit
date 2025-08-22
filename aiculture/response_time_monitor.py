"""
响应时间监控模块 - API和函数响应时间监控

提供：
1. HTTP API响应时间监控
2. 函数执行时间监控
3. 数据库查询时间监控
4. 响应时间告警
5. 性能趋势分析
"""

import json
import queue
import statistics
import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

# 常量定义
SECONDS_PER_HOUR = 3600


@dataclass
class ResponseTimeRecord:
    """响应时间记录"""

    name: str
    category: str  # api, function, database, file_io
    response_time: float  # 响应时间(毫秒)
    timestamp: float
    status: str = "success"  # success, error, timeout
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseTimeThreshold:
    """响应时间阈值配置"""

    name: str
    warning_threshold: float  # 警告阈值(毫秒)
    error_threshold: float  # 错误阈值(毫秒)
    timeout_threshold: float  # 超时阈值(毫秒)
    enabled: bool = True


class ResponseTimeMonitor:
    """响应时间监控器"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.config_file = project_path / ".aiculture" / "response_time_config.json"
        self.records_file = project_path / ".aiculture" / "response_time_records.json"

        self.thresholds: dict[str, ResponseTimeThreshold] = {}
        self.records: list[ResponseTimeRecord] = []
        self.record_queue = queue.Queue()
        self.monitoring = False
        self.monitor_thread = None

        self._load_config()
        self._load_records()
        self._start_background_processor()

    def _load_config(self) -> None:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for name, threshold_data in data.get("thresholds", {}).items():
                        self.thresholds[name] = ResponseTimeThreshold(**threshold_data)
            except Exception as e:
                print(f"加载响应时间配置失败: {e}")

        # 设置默认阈值
        self._set_default_thresholds()

    def _set_default_thresholds(self) -> None:
        """设置默认阈值"""
        defaults = {
            "api_default": ResponseTimeThreshold("api_default", 200, 500, 5000),
            "function_default": ResponseTimeThreshold("function_default", 10, 100, 1000),
            "database_default": ResponseTimeThreshold("database_default", 50, 200, 2000),
            "file_io_default": ResponseTimeThreshold("file_io_default", 100, 500, 3000),
        }

        for name, threshold in defaults.items():
            if name not in self.thresholds:
                self.thresholds[name] = threshold

    def _save_config(self) -> None:
        """保存配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            data = {
                "thresholds": {
                    name: {
                        "name": t.name,
                        "warning_threshold": t.warning_threshold,
                        "error_threshold": t.error_threshold,
                        "timeout_threshold": t.timeout_threshold,
                        "enabled": t.enabled,
                    }
                    for name, t in self.thresholds.items()
                }
            }
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_records(self) -> None:
        """加载历史记录"""
        if self.records_file.exists():
            try:
                with open(self.records_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = [
                        ResponseTimeRecord(**record) for record in data[-1000:]
                    ]  # 只保留最近1000条
            except Exception as e:
                print(f"加载响应时间记录失败: {e}")

    def _save_records(self) -> None:
        """保存记录"""
        self.records_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.records_file, "w", encoding="utf-8") as f:
            data = [
                {
                    "name": r.name,
                    "category": r.category,
                    "response_time": r.response_time,
                    "timestamp": r.timestamp,
                    "status": r.status,
                    "details": r.details,
                }
                for r in self.records[-1000:]
            ]  # 只保存最近1000条
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _start_background_processor(self) -> None:
        """启动后台处理线程"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._process_records, daemon=True)
        self.monitor_thread.start()

    def _process_records(self) -> None:
        """处理记录队列"""
        while self.monitoring:
            try:
                record = self.record_queue.get(timeout=1)
                self.records.append(record)

                # 检查阈值
                self._check_thresholds(record)

                # 定期保存记录
                if len(self.records) % 10 == 0:
                    self._save_records()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"处理响应时间记录错误: {e}")

    def _check_thresholds(self, record: ResponseTimeRecord) -> None:
        """检查阈值并发出告警"""
        # 查找适用的阈值
        threshold = self.thresholds.get(record.name)
        if not threshold:
            threshold = self.thresholds.get(f"{record.category}_default")

        if not threshold or not threshold.enabled:
            return

        if record.response_time >= threshold.timeout_threshold:
            self._send_alert("timeout", record, threshold)
        elif record.response_time >= threshold.error_threshold:
            self._send_alert("error", record, threshold)
        elif record.response_time >= threshold.warning_threshold:
            self._send_alert("warning", record, threshold)

    def _send_alert(
        self, level: str, record: ResponseTimeRecord, threshold: ResponseTimeThreshold
    ) -> None:
        """发送告警"""
        alert_message = """
🚨 响应时间告警 [{level.upper()}]
名称: {record.name}
类别: {record.category}
响应时间: {record.response_time:.2f}ms
阈值: {getattr(threshold, f'{level}_threshold')}ms
时间: {datetime.fromtimestamp(record.timestamp)}
"""
        print(alert_message)

        # 这里可以集成到告警系统中
        # 例如发送邮件、Slack通知等

    @contextmanager
    def monitor_execution(self, name: str, category: str = "function", **details):
        """监控执行时间的上下文管理器"""
        start_time = time.perf_counter()
        status = "success"

        try:
            yield
        except Exception as e:
            status = "error"
            details["error"] = str(e)
            raise
        finally:
            end_time = time.perf_counter()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒

            record = ResponseTimeRecord(
                name=name,
                category=category,
                response_time=response_time,
                timestamp=time.time(),
                status=status,
                details=details,
            )

            self.record_queue.put(record)

    def monitor_api_call(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """监控API调用"""
        start_time = time.perf_counter()

        try:
            response = requests.request(method, url, **kwargs)
            status = "success" if response.status_code < 400 else "error"
        except requests.exceptions.Timeout:
            status = "timeout"
            raise
        except Exception:
            status = "error"
            raise
        finally:
            end_time = time.perf_counter()
            response_time = (end_time - start_time) * 1000

            record = ResponseTimeRecord(
                name=f"{method} {url}",
                category="api",
                response_time=response_time,
                timestamp=time.time(),
                status=status,
                details={
                    "method": method,
                    "url": url,
                    "status_code": (response.status_code if "response" in locals() else None),
                },
            )

            self.record_queue.put(record)

        return response

    def set_threshold(self, name: str, warning: float, error: float, timeout: float) -> None:
        """设置阈值"""
        self.thresholds[name] = ResponseTimeThreshold(
            name=name,
            warning_threshold=warning,
            error_threshold=error,
            timeout_threshold=timeout,
        )
        self._save_config()

    def get_statistics(self, name: str | None = None, hours: int = 24) -> dict[str, Any]:
        """获取统计信息"""
        cutoff_time = time.time() - (hours * SECONDS_PER_HOUR)

        # 过滤记录
        filtered_records = [
            r
            for r in self.records
            if r.timestamp >= cutoff_time and (name is None or r.name == name)
        ]

        if not filtered_records:
            return {"message": "没有找到匹配的记录"}

        response_times = [r.response_time for r in filtered_records]

        return {
            "total_requests": len(filtered_records),
            "avg_response_time": statistics.mean(response_times),
            "median_response_time": statistics.median(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": self._percentile(response_times, 95),
            "p99_response_time": self._percentile(response_times, 99),
            "success_rate": len([r for r in filtered_records if r.status == "success"])
            / len(filtered_records),
            "error_rate": len([r for r in filtered_records if r.status == "error"])
            / len(filtered_records),
            "timeout_rate": len([r for r in filtered_records if r.status == "timeout"])
            / len(filtered_records),
        }

    def _percentile(self, data: list[float], percentile: int) -> float:
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def get_trend_analysis(self, name: str | None = None, hours: int = 24) -> dict[str, Any]:
        """获取趋势分析"""
        cutoff_time = time.time() - (hours * SECONDS_PER_HOUR)

        filtered_records = [
            r
            for r in self.records
            if r.timestamp >= cutoff_time and (name is None or r.name == name)
        ]

        if len(filtered_records) < 10:
            return {"message": "数据不足，无法进行趋势分析"}

        # 按小时分组
        hourly_data = {}
        for record in filtered_records:
            hour = int(record.timestamp // SECONDS_PER_HOUR) * SECONDS_PER_HOUR
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(record.response_time)

        # 计算每小时的平均响应时间
        hourly_averages = {hour: statistics.mean(times) for hour, times in hourly_data.items()}

        # 计算趋势
        hours = sorted(hourly_averages.keys())
        averages = [hourly_averages[hour] for hour in hours]

        trend = "stable"
        if len(averages) >= 3:
            recent_avg = statistics.mean(averages[-3:])
            earlier_avg = statistics.mean(averages[:3])

            if recent_avg > earlier_avg * 1.2:
                trend = "degrading"
            elif recent_avg < earlier_avg * 0.8:
                trend = "improving"

        return {
            "trend": trend,
            "hourly_averages": hourly_averages,
            "current_avg": (statistics.mean(averages[-3:]) if len(averages) >= 3 else None),
            "baseline_avg": (statistics.mean(averages[:3]) if len(averages) >= 3 else None),
        }

    def stop_monitoring(self) -> None:
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self._save_records()


def response_time_monitor(name: str, category: str = "function"):
    """响应时间监控装饰器"""

    def decorator(func: Callable):
        """decorator函数"""

        def wrapper(*args, **kwargs):
            """wrapper函数"""
            # 这里需要访问全局的监控器实例
            # 在实际使用中，可以通过依赖注入或全局变量来实现
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                status = "success"
                return result
            except Exception:
                status = "error"
                raise
            finally:
                end_time = time.perf_counter()
                response_time = (end_time - start_time) * 1000
                print(f"⏱️ {name}: {response_time:.2f}ms [{status}]")

        wrapper._response_time_monitor = {"name": name, "category": category}
        return wrapper

    return decorator


# 使用示例
if __name__ == "__main__":
    monitor = ResponseTimeMonitor(Path("."))

    # 监控函数执行
    @response_time_monitor("test_function", "function")
    def test_function():
        """test_function函数"""
        time.sleep(0.1)
        return "success"

    # 使用上下文管理器监控
    with monitor.monitor_execution("database_query", "database"):
        time.sleep(0.05)  # 模拟数据库查询

    # 获取统计信息
    stats = monitor.get_statistics()
    print(f"统计信息: {stats}")

    # 获取趋势分析
    trend = monitor.get_trend_analysis()
    print(f"趋势分析: {trend}")

    monitor.stop_monitoring()
