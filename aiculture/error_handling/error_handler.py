"""
智能错误处理器

提供重试、降级、恢复等错误处理策略。
"""

import functools
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .exceptions import AICultureError, is_retryable_error, get_error_severity
from .logging_system import get_logger


@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0  # 基础延迟（秒）
    max_delay: float = 60.0  # 最大延迟（秒）
    exponential_base: float = 2.0  # 指数退避基数
    jitter: bool = True  # 是否添加随机抖动
    retryable_exceptions: Optional[List[Type[Exception]]] = None


@dataclass
class FallbackConfig:
    """降级配置"""
    fallback_function: Optional[Callable] = None
    fallback_value: Any = None
    use_cache: bool = True
    cache_ttl: int = 300  # 缓存TTL（秒）


class ErrorHandler:
    """智能错误处理器"""
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.logger = get_logger(f"error_handler.{name}")
        self._error_stats: Dict[str, int] = {}
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
    
    def _should_retry(self, error: Exception, retry_config: RetryConfig) -> bool:
        """判断是否应该重试"""
        # 检查是否在可重试异常列表中
        if retry_config.retryable_exceptions:
            if not any(isinstance(error, exc_type) for exc_type in retry_config.retryable_exceptions):
                return False
        
        # 使用默认的重试判断逻辑
        return is_retryable_error(error)
    
    def _calculate_delay(self, attempt: int, retry_config: RetryConfig) -> float:
        """计算重试延迟"""
        delay = retry_config.base_delay * (retry_config.exponential_base ** (attempt - 1))
        delay = min(delay, retry_config.max_delay)
        
        # 添加随机抖动
        if retry_config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def _get_cache_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        import hashlib
        key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str, ttl: int) -> Optional[Any]:
        """获取缓存结果"""
        if cache_key not in self._cache:
            return None
        
        timestamp = self._cache_timestamps.get(cache_key, 0)
        if time.time() - timestamp > ttl:
            # 缓存过期
            del self._cache[cache_key]
            del self._cache_timestamps[cache_key]
            return None
        
        return self._cache[cache_key]
    
    def _set_cached_result(self, cache_key: str, result: Any) -> None:
        """设置缓存结果"""
        self._cache[cache_key] = result
        self._cache_timestamps[cache_key] = time.time()
    
    def _record_error(self, error: Exception) -> None:
        """记录错误统计"""
        error_type = error.__class__.__name__
        self._error_stats[error_type] = self._error_stats.get(error_type, 0) + 1
    
    def with_retry(
        self,
        retry_config: Optional[RetryConfig] = None,
        fallback_config: Optional[FallbackConfig] = None
    ):
        """重试装饰器"""
        if retry_config is None:
            retry_config = RetryConfig()
        
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_with_retry(
                    func, args, kwargs, retry_config, fallback_config
                )
            return wrapper
        return decorator
    
    def _execute_with_retry(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        retry_config: RetryConfig,
        fallback_config: Optional[FallbackConfig] = None
    ) -> Any:
        """执行函数并处理重试"""
        last_error = None
        
        # 检查缓存
        cache_key = None
        if fallback_config and fallback_config.use_cache:
            cache_key = self._get_cache_key(func, args, kwargs)
            cached_result = self._get_cached_result(cache_key, fallback_config.cache_ttl)
            if cached_result is not None:
                self.logger.debug(f"使用缓存结果: {func.__name__}")
                return cached_result
        
        for attempt in range(1, retry_config.max_attempts + 1):
            try:
                with self.logger.operation_context(
                    operation=f"{func.__name__}",
                    attempt=attempt,
                    max_attempts=retry_config.max_attempts
                ):
                    result = func(*args, **kwargs)
                    
                    # 缓存成功结果
                    if cache_key:
                        self._set_cached_result(cache_key, result)
                    
                    return result
                    
            except Exception as error:
                last_error = error
                self._record_error(error)
                
                severity = get_error_severity(error)
                
                if attempt < retry_config.max_attempts and self._should_retry(error, retry_config):
                    delay = self._calculate_delay(attempt, retry_config)
                    
                    self.logger.warning(
                        f"操作失败，将在 {delay:.2f}s 后重试",
                        error=error,
                        attempt=attempt,
                        max_attempts=retry_config.max_attempts,
                        delay=delay,
                        severity=severity
                    )
                    
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"操作最终失败",
                        error=error,
                        attempt=attempt,
                        max_attempts=retry_config.max_attempts,
                        severity=severity
                    )
                    break
        
        # 尝试降级处理
        if fallback_config:
            return self._execute_fallback(func, args, kwargs, fallback_config, last_error)
        
        # 重新抛出最后的错误
        raise last_error
    
    def _execute_fallback(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        fallback_config: FallbackConfig,
        original_error: Exception
    ) -> Any:
        """执行降级处理"""
        try:
            if fallback_config.fallback_function:
                self.logger.info(f"执行降级函数: {fallback_config.fallback_function.__name__}")
                return fallback_config.fallback_function(*args, **kwargs)
            elif fallback_config.fallback_value is not None:
                self.logger.info(f"使用降级值: {fallback_config.fallback_value}")
                return fallback_config.fallback_value
            else:
                self.logger.warning("没有配置降级策略，重新抛出原始错误")
                raise original_error
                
        except Exception as fallback_error:
            self.logger.error(
                "降级处理也失败了",
                error=fallback_error,
                original_error=original_error
            )
            raise original_error
    
    def get_error_stats(self) -> Dict[str, int]:
        """获取错误统计"""
        return self._error_stats.copy()
    
    def reset_stats(self) -> None:
        """重置错误统计"""
        self._error_stats.clear()


# 全局错误处理器实例
_default_handler = ErrorHandler("default")


def with_error_handling(
    retry_config: Optional[RetryConfig] = None,
    fallback_config: Optional[FallbackConfig] = None,
    handler: Optional[ErrorHandler] = None
):
    """错误处理装饰器"""
    if handler is None:
        handler = _default_handler
    
    return handler.with_retry(retry_config, fallback_config)


@contextmanager
def handle_errors(
    operation_name: str,
    retry_config: Optional[RetryConfig] = None,
    fallback_config: Optional[FallbackConfig] = None,
    handler: Optional[ErrorHandler] = None
):
    """错误处理上下文管理器"""
    if handler is None:
        handler = _default_handler
    
    logger = handler.logger
    
    try:
        with logger.operation_context(operation=operation_name):
            yield
    except Exception as error:
        severity = get_error_severity(error)
        logger.error(
            f"操作 {operation_name} 发生错误",
            error=error,
            severity=severity
        )
        
        # 这里可以添加更多的错误处理逻辑
        # 比如发送告警、记录到监控系统等
        
        raise


# 便捷的装饰器实例
retry_on_failure = with_error_handling(RetryConfig(max_attempts=3))
retry_with_fallback = with_error_handling(
    RetryConfig(max_attempts=2),
    FallbackConfig(fallback_value=None)
)
