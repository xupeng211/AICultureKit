"""
可观测性文化模块 - 结构化日志、指标收集、分布式追踪

提供：
1. 结构化日志规范和工具
2. 指标收集标准
3. 分布式追踪规范
4. 告警规则模板
5. 可观测性最佳实践
"""

import json
import logging
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class LogLevel(Enum):
    """日志级别"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MetricType(Enum):
    """指标类型"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class StructuredLogEntry:
    """结构化日志条目"""

    timestamp: str
    level: str
    message: str
    service: str
    version: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    duration_ms: Optional[float] = None
    status: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """指标数据"""

    name: str
    type: MetricType
    value: Union[int, float]
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    help_text: str = ""


@dataclass
class Span:
    """分布式追踪Span"""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    status: str = "ok"  # ok, error, timeout
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)


class StructuredLogger:
    """结构化日志器"""

    def __init__(
        self,
        service_name: str,
        version: str = "1.0.0",
        output_file: Optional[Path] = None,
    ):
        self.service_name = service_name
        self.version = version
        self.output_file = output_file
        self.context = threading.local()

        # 设置标准日志器
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.DEBUG)

        # 添加处理器
        if output_file:
            handler = logging.FileHandler(output_file)
        else:
            handler = logging.StreamHandler()

        # 使用JSON格式
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _get_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return getattr(self.context, 'data', {})

    def set_context(self, **kwargs) -> None:
        """设置上下文"""
        if not hasattr(self.context, 'data'):
            self.context.data = {}
        self.context.data.update(kwargs)

    def clear_context(self) -> None:
        """清除上下文"""
        self.context.data = {}

    def _create_log_entry(self, level: LogLevel, message: str, **kwargs) -> StructuredLogEntry:
        """创建日志条目"""
        context = self._get_context()

        entry = StructuredLogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=level.value,
            message=message,
            service=self.service_name,
            version=self.version,
            trace_id=context.get('trace_id'),
            span_id=context.get('span_id'),
            user_id=context.get('user_id'),
            request_id=context.get('request_id'),
            component=kwargs.get('component'),
            operation=kwargs.get('operation'),
            duration_ms=kwargs.get('duration_ms'),
            status=kwargs.get('status'),
            error=kwargs.get('error'),
            metadata=kwargs.get('metadata', {}),
        )

        return entry

    def _log(self, level: LogLevel, message: str, **kwargs) -> None:
        """记录日志"""
        entry = self._create_log_entry(level, message, **kwargs)
        log_json = json.dumps(asdict(entry), ensure_ascii=False)

        # 使用标准日志器输出
        if level == LogLevel.DEBUG:
            self.logger.debug(log_json)
        elif level == LogLevel.INFO:
            self.logger.info(log_json)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_json)
        elif level == LogLevel.ERROR:
            self.logger.error(log_json)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_json)

    def debug(self, message: str, **kwargs) -> None:
        """调试日志"""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """信息日志"""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """警告日志"""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """错误日志"""
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """严重错误日志"""
        self._log(LogLevel.CRITICAL, message, **kwargs)

    @contextmanager
    def operation_context(self, operation: str, **context):
        """操作上下文管理器"""
        start_time = time.perf_counter()
        old_context = self._get_context().copy()

        # 设置新上下文
        self.set_context(operation=operation, **context)

        try:
            self.info(f"开始操作: {operation}", operation=operation, status="started")
            yield

            duration_ms = (time.perf_counter() - start_time) * 1000
            self.info(
                f"完成操作: {operation}",
                operation=operation,
                status="completed",
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.error(
                f"操作失败: {operation}",
                operation=operation,
                status="failed",
                duration_ms=duration_ms,
                error=str(e),
            )
            raise
        finally:
            # 恢复旧上下文
            self.context.data = old_context


class MetricsCollector:
    """指标收集器"""

    def __init__(self, service_name: str):
        """__init__函数"""
        self.service_name = service_name
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.lock = threading.Lock()

    def counter(
        self,
        name: str,
        value: float = 1,
        labels: Optional[Dict[str, str]] = None,
        help_text: str = "",
    ) -> None:
        """计数器指标"""
        with self.lock:
            key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
            self.counters[key] = self.counters.get(key, 0) + value

            metric = Metric(
                name=name,
                type=MetricType.COUNTER,
                value=self.counters[key],
                timestamp=time.time(),
                labels=labels or {},
                help_text=help_text,
            )
            self.metrics.append(metric)

    def gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        help_text: str = "",
    ) -> None:
        """仪表盘指标"""
        with self.lock:
            key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
            self.gauges[key] = value

            metric = Metric(
                name=name,
                type=MetricType.GAUGE,
                value=value,
                timestamp=time.time(),
                labels=labels or {},
                help_text=help_text,
            )
            self.metrics.append(metric)

    def histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        help_text: str = "",
    ) -> None:
        """直方图指标"""
        metric = Metric(
            name=name,
            type=MetricType.HISTOGRAM,
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            help_text=help_text,
        )
        with self.lock:
            self.metrics.append(metric)

    def get_metrics(self, format: str = "json") -> Union[str, List[Dict]]:
        """获取指标数据"""
        with self.lock:
            if format == "json":
                return [asdict(metric) for metric in self.metrics[-1000:]]  # 最近1000个指标
            elif format == "prometheus":
                return self._format_prometheus()
            else:
                return self.metrics[-1000:]

    def _format_prometheus(self) -> str:
        """格式化为Prometheus格式"""
        lines = []
        metric_groups = {}

        # 按名称分组
        for metric in self.metrics[-1000:]:
            if metric.name not in metric_groups:
                metric_groups[metric.name] = []
            metric_groups[metric.name].append(metric)

        for name, metrics in metric_groups.items():
            if metrics[0].help_text:
                lines.append(f"# HELP {name} {metrics[0].help_text}")
            lines.append(f"# TYPE {name} {metrics[0].type.value}")

            for metric in metrics:
                labels_str = ""
                if metric.labels:
                    labels_list = [f'{k}="{v}"' for k, v in metric.labels.items()]
                    labels_str = "{" + ",".join(labels_list) + "}"

                lines.append(f"{name}{labels_str} {metric.value} {int(metric.timestamp * 1000)}")

        return "\n".join(lines)

    def clear_metrics(self) -> None:
        """清除指标"""
        with self.lock:
            self.metrics.clear()


class DistributedTracer:
    """分布式追踪器"""

    def __init__(self, service_name: str):
        """__init__函数"""
        self.service_name = service_name
        self.spans: Dict[str, Span] = {}
        self.active_spans = threading.local()

    def start_span(self, operation_name: str, parent_span_id: Optional[str] = None) -> Span:
        """开始一个新的Span"""
        trace_id = getattr(self.active_spans, 'trace_id', None)
        if not trace_id:
            trace_id = str(uuid.uuid4())
            self.active_spans.trace_id = trace_id

        span_id = str(uuid.uuid4())

        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id or getattr(self.active_spans, 'span_id', None),
            operation_name=operation_name,
            start_time=time.time(),
        )

        self.spans[span_id] = span
        self.active_spans.span_id = span_id

        return span

    def finish_span(self, span: Span, status: str = "ok", **tags) -> None:
        """结束Span"""
        span.end_time = time.time()
        span.duration_ms = (span.end_time - span.start_time) * 1000
        span.status = status
        span.tags.update(tags)

        # 恢复父Span为活跃Span
        if span.parent_span_id:
            self.active_spans.span_id = span.parent_span_id
        else:
            if hasattr(self.active_spans, 'span_id'):
                delattr(self.active_spans, 'span_id')

    @contextmanager
    def trace_operation(self, operation_name: str, **tags):
        """追踪操作的上下文管理器"""
        span = self.start_span(operation_name)
        span.tags.update(tags)

        try:
            yield span
            self.finish_span(span, "ok")
        except Exception as e:
            span.logs.append({'timestamp': time.time(), 'level': 'error', 'message': str(e)})
            self.finish_span(span, "error", error=str(e))
            raise

    def get_trace(self, trace_id: str) -> List[Span]:
        """获取完整的追踪链"""
        return [span for span in self.spans.values() if span.trace_id == trace_id]

    def export_traces(self, format: str = "json") -> Union[str, List[Dict]]:
        """导出追踪数据"""
        if format == "json":
            return [asdict(span) for span in self.spans.values()]
        elif format == "jaeger":
            return self._format_jaeger()
        else:
            return list(self.spans.values())

    def _format_jaeger(self) -> Dict[str, Any]:
        """格式化为Jaeger格式"""
        traces = {}
        for span in self.spans.values():
            if span.trace_id not in traces:
                traces[span.trace_id] = []
            traces[span.trace_id].append(
                {
                    'traceID': span.trace_id,
                    'spanID': span.span_id,
                    'parentSpanID': span.parent_span_id,
                    'operationName': span.operation_name,
                    'startTime': int(span.start_time * 1000000),  # 微秒
                    'duration': int((span.duration_ms or 0) * 1000),  # 微秒
                    'tags': [{'key': k, 'value': v} for k, v in span.tags.items()],
                    'logs': span.logs,
                }
            )

        return {'data': [{'traceID': tid, 'spans': spans} for tid, spans in traces.items()]}


class ObservabilityManager:
    """可观测性管理器"""

    def __init__(
        self,
        service_name: str,
        version: str = "1.0.0",
        output_dir: Optional[Path] = None,
    ):
        self.service_name = service_name
        self.version = version
        self.output_dir = output_dir or Path(".aiculture/observability")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化组件
        self.logger = StructuredLogger(service_name, version, self.output_dir / "app.log")
        self.metrics = MetricsCollector(service_name)
        self.tracer = DistributedTracer(service_name)

    @contextmanager
    def observe_operation(self, operation_name: str, **context):
        """全面观测操作的上下文管理器"""
        # 设置日志上下文
        self.logger.set_context(**context)

        # 开始追踪
        with self.tracer.trace_operation(operation_name, **context) as span:
            # 设置追踪上下文到日志
            self.logger.set_context(trace_id=span.trace_id, span_id=span.span_id)

            # 记录开始指标
            self.metrics.counter(f"{operation_name}_started", labels={'service': self.service_name})

            start_time = time.perf_counter()

            try:
                yield {'logger': self.logger, 'metrics': self.metrics, 'span': span}

                # 记录成功指标
                duration = time.perf_counter() - start_time
                self.metrics.counter(
                    f"{operation_name}_completed", labels={'service': self.service_name}
                )
                self.metrics.histogram(
                    f"{operation_name}_duration",
                    duration * 1000,
                    labels={'service': self.service_name},
                )

            except Exception as e:
                # 记录失败指标
                self.metrics.counter(
                    f"{operation_name}_failed",
                    labels={'service': self.service_name, 'error': type(e).__name__},
                )
                raise
            finally:
                self.logger.clear_context()

    def export_observability_data(self) -> Dict[str, Any]:
        """导出所有可观测性数据"""
        return {
            'service': self.service_name,
            'version': self.version,
            'timestamp': time.time(),
            'metrics': self.metrics.get_metrics(),
            'traces': self.tracer.export_traces(),
        }

    def generate_dashboard_config(self) -> Dict[str, Any]:
        """生成仪表板配置"""
        return {
            'dashboard': {
                'title': f'{self.service_name} 可观测性仪表板',
                'panels': [
                    {
                        'title': '请求率',
                        'type': 'graph',
                        'metrics': ['requests_per_second'],
                        'unit': 'req/s',
                    },
                    {
                        'title': '响应时间',
                        'type': 'graph',
                        'metrics': ['response_time_p95', 'response_time_p99'],
                        'unit': 'ms',
                    },
                    {
                        'title': '错误率',
                        'type': 'graph',
                        'metrics': ['error_rate'],
                        'unit': '%',
                    },
                    {
                        'title': '系统资源',
                        'type': 'graph',
                        'metrics': ['cpu_usage', 'memory_usage'],
                        'unit': '%',
                    },
                ],
            }
        }


# 使用示例
if __name__ == "__main__":
    # 初始化可观测性管理器
    obs = ObservabilityManager("test-service", "1.0.0")

    # 使用全面观测
    with obs.observe_operation("test_operation", user_id="123", request_id="req-456") as ctx:
        logger = ctx['logger']
        metrics = ctx['metrics']
        span = ctx['span']

        logger.info("执行业务逻辑", component="business")
        metrics.counter("business_operations")

        # 模拟一些工作
        time.sleep(0.1)

        logger.info("操作完成", component="business")

    # 导出数据
    data = obs.export_observability_data()
    print(f"可观测性数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
