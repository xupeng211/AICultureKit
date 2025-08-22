"""
告警规则模板 - 标准化的告警规则和通知机制

提供：
1. 标准告警规则模板
2. 告警级别定义
3. 通知渠道配置
4. 告警抑制和聚合
5. 告警规则验证
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

# 常量定义
SECONDS_PER_HOUR = 3600


class AlertSeverity(Enum):
    """告警严重程度"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(Enum):
    """告警状态"""

    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertRule:
    """告警规则"""

    name: str
    description: str
    severity: AlertSeverity
    condition: str  # 告警条件表达式
    threshold: float
    duration: str = "5m"  # 持续时间
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class Alert:
    """告警实例"""

    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    timestamp: float
    labels: dict[str, str] = field(default_factory=dict)
    annotations: dict[str, str] = field(default_factory=dict)
    resolved_at: float | None = None


@dataclass
class NotificationChannel:
    """通知渠道"""

    name: str
    type: str  # email, slack, webhook, sms
    config: dict[str, Any]
    enabled: bool = True
    severity_filter: list[AlertSeverity] = field(default_factory=lambda: list(AlertSeverity))


class AlertingRulesManager:
    """告警规则管理器"""

    def __init__(self, project_path: Path):
        """__init__函数"""
        self.project_path = project_path
        self.config_dir = project_path / ".aiculture" / "alerting"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.rules: dict[str, AlertRule] = {}
        self.channels: dict[str, NotificationChannel] = {}
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: list[Alert] = []

        self._load_default_rules()
        self._load_config()

    def _load_default_rules(self) -> None:
        """加载默认告警规则"""
        default_rules = {
            # 性能相关告警
            "high_response_time": AlertRule(
                name="high_response_time",
                description="API响应时间过高",
                severity=AlertSeverity.WARNING,
                condition="avg_response_time > threshold",
                threshold=500.0,  # 500ms
                duration="2m",
                labels={"category": "performance"},
                annotations={
                    "summary": "API响应时间超过阈值",
                    "description": "平均响应时间 {{ $value }}ms 超过阈值 {{ $threshold }}ms",
                    "runbook": "检查系统负载和数据库性能",
                },
            ),
            "memory_usage_high": AlertRule(
                name="memory_usage_high",
                description="内存使用率过高",
                severity=AlertSeverity.WARNING,
                condition="memory_usage_percent > threshold",
                threshold=80.0,  # 80%
                duration="5m",
                labels={"category": "resource"},
                annotations={
                    "summary": "内存使用率过高",
                    "description": "内存使用率 {{ $value }}% 超过阈值 {{ $threshold }}%",
                    "runbook": "检查内存泄漏和优化内存使用",
                },
            ),
            "cpu_usage_high": AlertRule(
                name="cpu_usage_high",
                description="CPU使用率过高",
                severity=AlertSeverity.WARNING,
                condition="cpu_usage_percent > threshold",
                threshold=85.0,  # 85%
                duration="3m",
                labels={"category": "resource"},
                annotations={
                    "summary": "CPU使用率过高",
                    "description": "CPU使用率 {{ $value }}% 超过阈值 {{ $threshold }}%",
                    "runbook": "检查CPU密集型任务和优化算法",
                },
            ),
            # 错误相关告警
            "error_rate_high": AlertRule(
                name="error_rate_high",
                description="错误率过高",
                severity=AlertSeverity.CRITICAL,
                condition="error_rate > threshold",
                threshold=5.0,  # 5%
                duration="1m",
                labels={"category": "error"},
                annotations={
                    "summary": "错误率过高",
                    "description": "错误率 {{ $value }}% 超过阈值 {{ $threshold }}%",
                    "runbook": "检查错误日志和修复问题",
                },
            ),
            "service_down": AlertRule(
                name="service_down",
                description="服务不可用",
                severity=AlertSeverity.CRITICAL,
                condition="service_availability < threshold",
                threshold=1.0,  # 100%
                duration="30s",
                labels={"category": "availability"},
                annotations={
                    "summary": "服务不可用",
                    "description": "服务可用性 {{ $value }}% 低于阈值 {{ $threshold }}%",
                    "runbook": "立即检查服务状态和重启服务",
                },
            ),
            # 业务相关告警
            "test_coverage_low": AlertRule(
                name="test_coverage_low",
                description="测试覆盖率过低",
                severity=AlertSeverity.WARNING,
                condition="test_coverage < threshold",
                threshold=80.0,  # 80%
                duration="0s",  # 立即触发
                labels={"category": "quality"},
                annotations={
                    "summary": "测试覆盖率过低",
                    "description": "测试覆盖率 {{ $value }}% 低于阈值 {{ $threshold }}%",
                    "runbook": "增加单元测试和集成测试",
                },
            ),
            "security_vulnerability": AlertRule(
                name="security_vulnerability",
                description="发现安全漏洞",
                severity=AlertSeverity.CRITICAL,
                condition="security_issues > threshold",
                threshold=0.0,  # 任何安全问题都告警
                duration="0s",
                labels={"category": "security"},
                annotations={
                    "summary": "发现安全漏洞",
                    "description": "发现 {{ $value }} 个安全问题",
                    "runbook": "立即修复安全漏洞",
                },
            ),
            # 数据质量告警
            "data_quality_issue": AlertRule(
                name="data_quality_issue",
                description="数据质量问题",
                severity=AlertSeverity.WARNING,
                condition="data_quality_score < threshold",
                threshold=90.0,  # 90%
                duration="5m",
                labels={"category": "data"},
                annotations={
                    "summary": "数据质量问题",
                    "description": "数据质量评分 {{ $value }}% 低于阈值 {{ $threshold }}%",
                    "runbook": "检查数据源和数据处理流程",
                },
            ),
        }

        self.rules.update(default_rules)

    def _load_config(self) -> None:
        """加载配置"""
        config_file = self.config_dir / "alerting_config.yaml"
        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                # 加载自定义规则
                for rule_data in config.get("rules", []):
                    rule = AlertRule(**rule_data)
                    self.rules[rule.name] = rule

                # 加载通知渠道
                for channel_data in config.get("channels", []):
                    channel = NotificationChannel(**channel_data)
                    self.channels[channel.name] = channel

            except Exception as e:
                print(f"加载告警配置失败: {e}")

    def _save_config(self) -> None:
        """保存配置"""
        config = {
            "rules": [
                {
                    "name": rule.name,
                    "description": rule.description,
                    "severity": rule.severity.value,
                    "condition": rule.condition,
                    "threshold": rule.threshold,
                    "duration": rule.duration,
                    "labels": rule.labels,
                    "annotations": rule.annotations,
                    "enabled": rule.enabled,
                }
                for rule in self.rules.values()
            ],
            "channels": [
                {
                    "name": channel.name,
                    "type": channel.type,
                    "config": channel.config,
                    "enabled": channel.enabled,
                    "severity_filter": [s.value for s in channel.severity_filter],
                }
                for channel in self.channels.values()
            ],
        }

        config_file = self.config_dir / "alerting_config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    def add_rule(self, rule: AlertRule) -> None:
        """添加告警规则"""
        self.rules[rule.name] = rule
        self._save_config()

    def remove_rule(self, rule_name: str) -> None:
        """删除告警规则"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            self._save_config()

    def add_notification_channel(self, channel: NotificationChannel) -> None:
        """添加通知渠道"""
        self.channels[channel.name] = channel
        self._save_config()

    def evaluate_rules(self, metrics: dict[str, float]) -> list[Alert]:
        """评估告警规则"""
        new_alerts = []

        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue

            # 简单的条件评估（实际实现中应该更复杂）
            should_fire = self._evaluate_condition(rule, metrics)

            existing_alert = self.active_alerts.get(rule_name)

            if should_fire and not existing_alert:
                # 创建新告警
                alert = Alert(
                    rule_name=rule_name,
                    severity=rule.severity,
                    status=AlertStatus.FIRING,
                    message=self._format_message(rule, metrics),
                    timestamp=time.time(),
                    labels=rule.labels.copy(),
                    annotations=rule.annotations.copy(),
                )

                self.active_alerts[rule_name] = alert
                self.alert_history.append(alert)
                new_alerts.append(alert)

                # 发送通知
                self._send_notifications(alert)

            elif not should_fire and existing_alert and existing_alert.status == AlertStatus.FIRING:
                # 解决告警
                existing_alert.status = AlertStatus.RESOLVED
                existing_alert.resolved_at = time.time()
                del self.active_alerts[rule_name]

                # 发送解决通知
                self._send_notifications(existing_alert)

        return new_alerts

    def _evaluate_condition(self, rule: AlertRule, metrics: dict[str, float]) -> bool:
        """评估告警条件"""
        # 这是一个简化的实现，实际应该支持更复杂的表达式
        condition = rule.condition
        threshold = rule.threshold

        if "avg_response_time > threshold" in condition:
            return metrics.get("avg_response_time", 0) > threshold
        elif "memory_usage_percent > threshold" in condition:
            return metrics.get("memory_usage_percent", 0) > threshold
        elif "cpu_usage_percent > threshold" in condition:
            return metrics.get("cpu_usage_percent", 0) > threshold
        elif "error_rate > threshold" in condition:
            return metrics.get("error_rate", 0) > threshold
        elif "service_availability < threshold" in condition:
            return metrics.get("service_availability", 100) < threshold
        elif "test_coverage < threshold" in condition:
            return metrics.get("test_coverage", 100) < threshold
        elif "security_issues > threshold" in condition:
            return metrics.get("security_issues", 0) > threshold
        elif "data_quality_score < threshold" in condition:
            return metrics.get("data_quality_score", 100) < threshold

        return False

    def _format_message(self, rule: AlertRule, metrics: dict[str, float]) -> str:
        """格式化告警消息"""
        message = rule.annotations.get("description", rule.description)

        # 简单的模板替换
        for key, value in metrics.items():
            message = message.replace(f"{{{{ ${key} }}}}", str(value))

        message = message.replace("{{ $threshold }}", str(rule.threshold))

        return message

    def _send_notifications(self, alert: Alert) -> None:
        """发送通知"""
        for channel in self.channels.values():
            if not channel.enabled:
                continue

            if alert.severity not in channel.severity_filter:
                continue

            try:
                if channel.type == "email":
                    self._send_email_notification(channel, alert)
                elif channel.type == "slack":
                    self._send_slack_notification(channel, alert)
                elif channel.type == "webhook":
                    self._send_webhook_notification(channel, alert)
                elif channel.type == "console":
                    self._send_console_notification(channel, alert)

            except Exception as e:
                print(f"发送通知失败 ({channel.name}): {e}")

    def _send_console_notification(self, channel: NotificationChannel, alert: Alert) -> None:
        """发送控制台通知"""
        status_emoji = "🔥" if alert.status == AlertStatus.FIRING else "✅"
        severity_emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}[alert.severity.value]

        print(
            """
{status_emoji} {severity_emoji} 告警通知
规则: {alert.rule_name}
严重程度: {alert.severity.value.upper()}
状态: {alert.status.value.upper()}
消息: {alert.message}
时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.timestamp))}
标签: {alert.labels}
"""
        )

    def _send_email_notification(self, channel: NotificationChannel, alert: Alert) -> None:
        """发送邮件通知（占位符实现）"""
        print(f"📧 发送邮件通知到 {channel.config.get('recipients', [])}: {alert.message}")

    def _send_slack_notification(self, channel: NotificationChannel, alert: Alert) -> None:
        """发送Slack通知（占位符实现）"""
        print(f"💬 发送Slack通知到 {channel.config.get('webhook_url', '')}: {alert.message}")

    def _send_webhook_notification(self, channel: NotificationChannel, alert: Alert) -> None:
        """发送Webhook通知（占位符实现）"""
        print(f"🔗 发送Webhook通知到 {channel.config.get('url', '')}: {alert.message}")

    def get_active_alerts(self) -> list[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())

    def get_alert_history(self, hours: int = 24) -> list[Alert]:
        """获取告警历史"""
        cutoff_time = time.time() - (hours * SECONDS_PER_HOUR)
        return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]

    def generate_prometheus_rules(self) -> str:
        """生成Prometheus告警规则"""
        rules = {"groups": [{"name": "aiculture_alerts", "rules": []}]}

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            prometheus_rule = {
                "alert": rule.name,
                "expr": self._convert_to_prometheus_expr(rule.condition, rule.threshold),
                "for": rule.duration,
                "labels": rule.labels,
                "annotations": rule.annotations,
            }

            rules["groups"][0]["rules"].append(prometheus_rule)

        return yaml.dump(rules, default_flow_style=False)

    def _convert_to_prometheus_expr(self, condition: str, threshold: float) -> str:
        """转换为Prometheus表达式"""
        # 简化的转换逻辑
        if "avg_response_time > threshold" in condition:
            return f"avg(response_time_seconds) > {threshold/1000}"
        elif "memory_usage_percent > threshold" in condition:
            return (
                f"(process_resident_memory_bytes / node_memory_MemTotal_bytes) * 100 > {threshold}"
            )
        elif "cpu_usage_percent > threshold" in condition:
            return (
                f'100 - (avg(irate(node_cpu_seconds_total{{mode="idle"}}[5m])) * 100) > {threshold}'
            )
        elif "error_rate > threshold" in condition:
            return f'(rate(http_requests_total{{status=~"5.."}}) / rate(http_requests_total)) * 100 > {threshold}'
        else:
            return "up == 0"  # 默认表达式

    def validate_rules(self) -> dict[str, list[str]]:
        """验证告警规则"""
        validation_results = {}

        for rule_name, rule in self.rules.items():
            errors = []

            # 检查必填字段
            if not rule.name:
                errors.append("规则名称不能为空")
            if not rule.description:
                errors.append("规则描述不能为空")
            if not rule.condition:
                errors.append("告警条件不能为空")

            # 检查阈值
            if rule.threshold < 0:
                errors.append("阈值不能为负数")

            # 检查持续时间格式
            if not rule.duration.endswith(("s", "m", "h")):
                errors.append("持续时间格式不正确，应该以s、m或h结尾")

            if errors:
                validation_results[rule_name] = errors

        return validation_results


# 使用示例
if __name__ == "__main__":
    # 初始化告警管理器
    alerting = AlertingRulesManager(Path("."))

    # 添加控制台通知渠道
    console_channel = NotificationChannel(
        name="console",
        type="console",
        config={},
        severity_filter=[AlertSeverity.CRITICAL, AlertSeverity.WARNING],
    )
    alerting.add_notification_channel(console_channel)

    # 模拟指标数据
    metrics = {
        "avg_response_time": 600,  # 600ms，超过阈值
        "memory_usage_percent": 85,  # 85%，超过阈值
        "cpu_usage_percent": 70,  # 70%，正常
        "error_rate": 2,  # 2%，正常
        "service_availability": 100,  # 100%，正常
        "test_coverage": 75,  # 75%，低于阈值
        "security_issues": 1,  # 1个安全问题
        "data_quality_score": 95,  # 95%，正常
    }

    # 评估告警规则
    new_alerts = alerting.evaluate_rules(metrics)
    print(f"新产生的告警数量: {len(new_alerts)}")

    # 获取活跃告警
    active_alerts = alerting.get_active_alerts()
    print(f"活跃告警数量: {len(active_alerts)}")

    # 验证规则
    validation_results = alerting.validate_rules()
    if validation_results:
        print(f"规则验证问题: {validation_results}")
    else:
        print("所有规则验证通过")

    # 生成Prometheus规则
    prometheus_rules = alerting.generate_prometheus_rules()
    print(f"Prometheus规则:\n{prometheus_rules}")
