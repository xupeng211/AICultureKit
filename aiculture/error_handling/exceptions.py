"""
统一异常类定义

定义项目中使用的所有自定义异常类，提供清晰的错误分类和处理。
"""

from typing import Any, Dict, Optional


class AICultureError(Exception):
    """AICultureKit基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
        }


class ConfigurationError(AICultureError):
    """配置相关错误"""

    def __init__(
        self,
        message: str,
        config_file: Optional[str] = None,
        config_key: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if config_file:
            details["config_file"] = config_file
        if config_key:
            details["config_key"] = config_key

        super().__init__(message, details=details, **kwargs)


class ValidationError(AICultureError):
    """数据验证错误"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        expected_type: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        if expected_type:
            details["expected_type"] = expected_type

        super().__init__(message, details=details, **kwargs)


class ProcessingError(AICultureError):
    """处理过程错误"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        if file_path:
            details["file_path"] = file_path
        if line_number:
            details["line_number"] = line_number

        super().__init__(message, details=details, **kwargs)


class ResourceError(AICultureError):
    """资源相关错误"""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_path: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_path:
            details["resource_path"] = resource_path

        super().__init__(message, details=details, **kwargs)


class IntegrationError(AICultureError):
    """集成相关错误"""

    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if service:
            details["service"] = service
        if endpoint:
            details["endpoint"] = endpoint
        if status_code:
            details["status_code"] = status_code

        super().__init__(message, details=details, **kwargs)


class SecurityError(AICultureError):
    """安全相关错误"""

    def __init__(
        self,
        message: str,
        security_issue: Optional[str] = None,
        severity: Optional[str] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if security_issue:
            details["security_issue"] = security_issue
        if severity:
            details["severity"] = severity

        super().__init__(message, details=details, **kwargs)


class PerformanceError(AICultureError):
    """性能相关错误"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        duration_ms: Optional[float] = None,
        threshold_ms: Optional[float] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        if duration_ms:
            details["duration_ms"] = duration_ms
        if threshold_ms:
            details["threshold_ms"] = threshold_ms

        super().__init__(message, details=details, **kwargs)


class CultureViolationError(AICultureError):
    """文化标准违规错误"""

    def __init__(
        self,
        message: str,
        principle: Optional[str] = None,
        severity: Optional[str] = None,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if principle:
            details["principle"] = principle
        if severity:
            details["severity"] = severity
        if file_path:
            details["file_path"] = file_path
        if line_number:
            details["line_number"] = line_number

        super().__init__(message, details=details, **kwargs)


class QualityGateError(AICultureError):
    """质量门禁错误"""

    def __init__(
        self,
        message: str,
        gate_name: Optional[str] = None,
        failed_checks: Optional[list] = None,
        **kwargs,
    ):
        details = kwargs.get("details", {})
        if gate_name:
            details["gate_name"] = gate_name
        if failed_checks:
            details["failed_checks"] = failed_checks

        super().__init__(message, details=details, **kwargs)


# 异常映射表，用于从错误代码创建异常
EXCEPTION_MAP = {
    "configuration_error": ConfigurationError,
    "validation_error": ValidationError,
    "processing_error": ProcessingError,
    "resource_error": ResourceError,
    "integration_error": IntegrationError,
    "security_error": SecurityError,
    "performance_error": PerformanceError,
    "culture_violation_error": CultureViolationError,
    "quality_gate_error": QualityGateError,
}


def create_exception(error_code: str, message: str, **kwargs) -> AICultureError:
    """根据错误代码创建异常实例"""
    exception_class = EXCEPTION_MAP.get(error_code, AICultureError)
    return exception_class(message, error_code=error_code, **kwargs)


def is_retryable_error(error: Exception) -> bool:
    """判断错误是否可重试"""
    # 网络相关错误通常可重试
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True

    # 资源暂时不可用
    if isinstance(error, ResourceError):
        return True

    # 集成错误中的某些状态码可重试
    if isinstance(error, IntegrationError):
        status_code = error.details.get("status_code")
        if status_code in [429, 502, 503, 504]:  # 限流、网关错误等
            return True

    return False


def get_error_severity(error: Exception) -> str:
    """获取错误严重程度"""
    if isinstance(error, SecurityError):
        return "critical"
    elif isinstance(error, (QualityGateError, CultureViolationError)):
        return error.details.get("severity", "warning")
    elif isinstance(error, (ConfigurationError, ValidationError)):
        return "error"
    elif isinstance(error, (ProcessingError, ResourceError)):
        return "warning"
    else:
        return "error"
