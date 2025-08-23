"""
统一日志记录系统

提供结构化、可配置的日志记录功能。
"""

import json
import logging
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union


class LogLevel(Enum):
    """日志级别"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogContext:
    """日志上下文"""

    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LogEntry:
    """日志条目"""

    timestamp: str
    level: str
    message: str
    service: str
    version: str
    context: LogContext
    error: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None


class AICultureLogger:
    """AICultureKit统一日志器"""

    def __init__(
        self,
        name: str,
        service: str = "aiculture",
        version: str = "1.0.0",
        output_file: Optional[Path] = None,
        structured: bool = True,
        level: LogLevel = LogLevel.INFO,
    ):
        self.name = name
        self.service = service
        self.version = version
        self.structured = structured
        self.context = threading.local()

        # 设置标准日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))

        # 清除现有处理器
        self.logger.handlers.clear()

        # 添加处理器
        if output_file:
            handler = logging.FileHandler(output_file, encoding="utf-8")
        else:
            handler = logging.StreamHandler(sys.stdout)

        if structured:
            formatter = logging.Formatter("%(message)s")
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _get_context(self) -> LogContext:
        """获取当前日志上下文"""
        return getattr(self.context, "data", LogContext())

    def set_context(self, **kwargs) -> None:
        """设置日志上下文"""
        current_context = self._get_context()

        # 更新上下文字段
        for key, value in kwargs.items():
            if hasattr(current_context, key):
                setattr(current_context, key, value)
            else:
                # 添加到metadata中
                if current_context.metadata is None:
                    current_context.metadata = {}
                current_context.metadata[key] = value

        self.context.data = current_context

    def clear_context(self) -> None:
        """清除日志上下文"""
        self.context.data = LogContext()

    def _create_log_entry(
        self, level: LogLevel, message: str, error: Optional[Exception] = None, **kwargs
    ) -> LogEntry:
        """创建日志条目"""
        context = self._get_context()

        # 处理错误信息
        error_dict = None
        if error:
            error_dict = {
                "type": error.__class__.__name__,
                "message": str(error),
                "traceback": None,  # 可以添加traceback信息
            }

            # 如果是自定义异常，添加更多信息
            if hasattr(error, "to_dict"):
                error_dict.update(error.to_dict())

        # 处理性能信息
        performance_dict = None
        if "duration_ms" in kwargs:
            performance_dict = {
                "duration_ms": kwargs.pop("duration_ms"),
                "operation": context.operation,
            }

        # 更新上下文metadata
        if kwargs:
            if context.metadata is None:
                context.metadata = {}
            context.metadata.update(kwargs)

        return LogEntry(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            level=level.value,
            message=message,
            service=self.service,
            version=self.version,
            context=context,
            error=error_dict,
            performance=performance_dict,
        )

    def _log(
        self, level: LogLevel, message: str, error: Optional[Exception] = None, **kwargs
    ) -> None:
        """记录日志"""
        if self.structured:
            entry = self._create_log_entry(level, message, error, **kwargs)
            log_json = json.dumps(asdict(entry), ensure_ascii=False, default=str)
            log_message = log_json
        else:
            log_message = message
            if error:
                log_message += f" | Error: {error}"
            if kwargs:
                log_message += f" | Details: {kwargs}"

        # 使用标准日志器输出
        if level == LogLevel.DEBUG:
            self.logger.debug(log_message)
        elif level == LogLevel.INFO:
            self.logger.info(log_message)
        elif level == LogLevel.WARNING:
            self.logger.warning(log_message)
        elif level == LogLevel.ERROR:
            self.logger.error(log_message)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_message)

    def debug(self, message: str, **kwargs) -> None:
        """调试日志"""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """信息日志"""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """警告日志"""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, error: Optional[Exception] = None, **kwargs) -> None:
        """错误日志"""
        self._log(LogLevel.ERROR, message, error=error, **kwargs)

    def critical(
        self, message: str, error: Optional[Exception] = None, **kwargs
    ) -> None:
        """严重错误日志"""
        self._log(LogLevel.CRITICAL, message, error=error, **kwargs)

    @contextmanager
    def operation_context(self, operation: str, **context_kwargs):
        """操作上下文管理器"""
        start_time = time.perf_counter()

        # 保存旧上下文
        old_context = self._get_context()

        # 设置新上下文
        self.set_context(operation=operation, **context_kwargs)

        try:
            self.info(f"开始操作: {operation}", status="started")
            yield

            duration_ms = (time.perf_counter() - start_time) * 1000
            self.info(
                f"完成操作: {operation}", status="completed", duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.error(
                f"操作失败: {operation}",
                error=e,
                status="failed",
                duration_ms=duration_ms,
            )
            raise
        finally:
            # 恢复旧上下文
            self.context.data = old_context


# 全局日志器实例
_loggers: Dict[str, AICultureLogger] = {}
_default_config = {
    "service": "aiculture",
    "version": "1.0.0",
    "structured": True,
    "level": LogLevel.INFO,
}


def setup_logging(
    service: str = "aiculture",
    version: str = "1.0.0",
    output_file: Optional[Union[str, Path]] = None,
    structured: bool = True,
    level: LogLevel = LogLevel.INFO,
) -> None:
    """设置全局日志配置"""
    global _default_config
    _default_config.update(
        {
            "service": service,
            "version": version,
            "output_file": Path(output_file) if output_file else None,
            "structured": structured,
            "level": level,
        }
    )


def get_logger(name: str) -> AICultureLogger:
    """获取日志器实例"""
    if name not in _loggers:
        _loggers[name] = AICultureLogger(name, **_default_config)
    return _loggers[name]


# 便捷函数
def debug(message: str, **kwargs) -> None:
    """全局调试日志"""
    get_logger("aiculture").debug(message, **kwargs)


def info(message: str, **kwargs) -> None:
    """全局信息日志"""
    get_logger("aiculture").info(message, **kwargs)


def warning(message: str, **kwargs) -> None:
    """全局警告日志"""
    get_logger("aiculture").warning(message, **kwargs)


def error(message: str, error: Optional[Exception] = None, **kwargs) -> None:
    """全局错误日志"""
    get_logger("aiculture").error(message, error=error, **kwargs)


def critical(message: str, error: Optional[Exception] = None, **kwargs) -> None:
    """全局严重错误日志"""
    get_logger("aiculture").critical(message, error=error, **kwargs)
