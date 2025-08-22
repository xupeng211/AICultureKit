"""统一错误处理和日志记录系统

提供：
1. 统一的异常类定义
2. 结构化错误处理
3. 智能日志记录
4. 错误恢复机制
5. 性能监控集成
"""

from .error_handler import (
    ErrorHandler,
    FallbackConfig,
    RetryConfig,
    handle_errors,
    with_error_handling,
)
from .exceptions import (
    AICultureError,
    ConfigurationError,
    IntegrationError,
    ProcessingError,
    ResourceError,
    SecurityError,
    ValidationError,
)
from .logging_system import (
    AICultureLogger,
    LogContext,
    LogLevel,
    get_logger,
    setup_logging,
)
from .monitoring import (
    ErrorMetrics,
    ErrorMonitor,
    PerformanceTracker,
    get_error_monitor,
    get_monitoring_manager,
    get_performance_tracker,
)

__all__ = [
    # 异常类
    "AICultureError",
    "ConfigurationError",
    "ValidationError",
    "ProcessingError",
    "ResourceError",
    "IntegrationError",
    "SecurityError",
    # 日志系统
    "AICultureLogger",
    "LogLevel",
    "LogContext",
    "setup_logging",
    "get_logger",
    # 错误处理
    "ErrorHandler",
    "RetryConfig",
    "FallbackConfig",
    "with_error_handling",
    "handle_errors",
    # 监控
    "ErrorMonitor",
    "ErrorMetrics",
    "PerformanceTracker",
    "get_error_monitor",
    "get_performance_tracker",
    "get_monitoring_manager",
]
