"""
监控配置管理模块
提供Grafana、Prometheus等监控系统的配置生成和管理
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .i18n import _


@dataclass
class MetricConfig:
    """指标配置"""

    name: str
    description: str
    metric_type: str  # counter, gauge, histogram, summary
    labels: List[str]
    help_text: str
    unit: str = ""
    buckets: Optional[List[float]] = None  # for histogram


@dataclass
class AlertRule:
    """告警规则"""

    name: str
    description: str
    expression: str
    duration: str
    severity: str  # critical, warning, info
    labels: Dict[str, str]
    annotations: Dict[str, str]


@dataclass
class DashboardPanel:
    """仪表板面板"""

    title: str
    panel_type: str  # graph, stat, table, heatmap
    targets: List[Dict[str, Any]]
    grid_pos: Dict[str, int]
    options: Dict[str, Any]


@dataclass
class Dashboard:
    """仪表板"""

    title: str
    description: str
    tags: List[str]
    panels: List[DashboardPanel]
    time_range: Dict[str, str]
    refresh: str


class MonitoringConfigManager:
    """监控配置管理器"""

    def __init__(self, config_dir: Path):
        """__init__函数"""
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径
        self.prometheus_config = config_dir / "prometheus.yml"
        self.grafana_config = config_dir / "grafana"
        self.alertmanager_config = config_dir / "alertmanager.yml"

        # 确保Grafana配置目录存在
        self.grafana_config.mkdir(exist_ok=True)
        (self.grafana_config / "dashboards").mkdir(exist_ok=True)
        (self.grafana_config / "datasources").mkdir(exist_ok=True)

        # 默认配置
        self.metrics: List[MetricConfig] = []
        self.alert_rules: List[AlertRule] = []
        self.dashboards: List[Dashboard] = []

    def add_metric(self, metric: MetricConfig) -> None:
        """添加指标配置"""
        self.metrics.append(metric)

    def add_alert_rule(self, rule: AlertRule) -> None:
        """添加告警规则"""
        self.alert_rules.append(rule)

    def add_dashboard(self, dashboard: Dashboard) -> None:
        """添加仪表板"""
        self.dashboards.append(dashboard)

    def generate_prometheus_config(
        self, scrape_configs: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成Prometheus配置"""
        default_scrape_configs = [
            {
                "job_name": "aiculture-app",
                "static_configs": [{"targets": ["localhost:8000"]}],
                "scrape_interval": "15s",
                "metrics_path": "/metrics",
            }
        ]

        config = {
            "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
            "rule_files": ["alert_rules.yml"],
            "scrape_configs": scrape_configs or default_scrape_configs,
            "alerting": {"alertmanagers": [{"static_configs": [{"targets": ["localhost:9093"]}]}]},
        }

        return config

    def generate_alert_rules(self) -> Dict[str, Any]:
        """生成告警规则"""
        groups = []

        if self.alert_rules:
            rules = []
            for rule in self.alert_rules:
                rule_config = {
                    "alert": rule.name,
                    "expr": rule.expression,
                    "for": rule.duration,
                    "labels": rule.labels,
                    "annotations": rule.annotations,
                }
                rules.append(rule_config)

            groups.append({"name": "aiculture.rules", "rules": rules})

        return {"groups": groups}

    def generate_grafana_datasource(
        self, prometheus_url: str = "http://localhost:9090"
    ) -> Dict[str, Any]:
        """生成Grafana数据源配置"""
        return {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "access": "proxy",
                    "url": prometheus_url,
                    "isDefault": True,
                    "editable": True,
                }
            ],
        }

    def generate_culture_dashboard(self) -> Dict[str, Any]:
        """生成文化监控仪表板"""
        panels = [
            {
                "id": 1,
                "title": _("Culture Quality Score"),
                "type": "stat",
                "targets": [{"expr": "aiculture_quality_score", "legendFormat": "Quality Score"}],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                "options": {
                    "reduceOptions": {
                        "values": False,
                        "calcs": ["lastNotNull"],
                        "fields": "",
                    },
                    "orientation": "auto",
                    "textMode": "auto",
                    "colorMode": "value",
                    "graphMode": "area",
                    "justifyMode": "auto",
                },
                "fieldConfig": {
                    "defaults": {
                        "color": {"mode": "thresholds"},
                        "thresholds": {
                            "steps": [
                                {"color": "red", "value": 0},
                                {"color": "yellow", "value": 70},
                                {"color": "green", "value": 85},
                            ]
                        },
                        "unit": "percent",
                        "min": 0,
                        "max": 100,
                    }
                },
            },
            {
                "id": 2,
                "title": _("Violations by Principle"),
                "type": "piechart",
                "targets": [
                    {
                        "expr": "sum by (principle) (aiculture_violations_total)",
                        "legendFormat": "{{principle}}",
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                "options": {
                    "reduceOptions": {
                        "values": False,
                        "calcs": ["lastNotNull"],
                        "fields": "",
                    },
                    "pieType": "pie",
                    "tooltip": {"mode": "single"},
                    "legend": {"displayMode": "visible", "placement": "bottom"},
                },
            },
            {
                "id": 3,
                "title": _("Test Coverage Over Time"),
                "type": "graph",
                "targets": [
                    {
                        "expr": "aiculture_test_coverage_percent",
                        "legendFormat": "Test Coverage",
                    }
                ],
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
                "yAxes": [{"label": "Percentage", "min": 0, "max": 100, "unit": "percent"}],
                "thresholds": [
                    {
                        "value": 80,
                        "colorMode": "critical",
                        "op": "lt",
                        "fill": True,
                        "line": True,
                    }
                ],
            },
            {
                "id": 4,
                "title": _("Security Issues"),
                "type": "table",
                "targets": [
                    {
                        "expr": "aiculture_security_issues",
                        "format": "table",
                        "instant": True,
                    }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
                "options": {"showHeader": True},
                "fieldConfig": {"defaults": {"custom": {"align": "auto", "displayMode": "auto"}}},
            },
            {
                "id": 5,
                "title": _("Performance Metrics"),
                "type": "graph",
                "targets": [
                    {
                        "expr": "aiculture_execution_time_seconds",
                        "legendFormat": "Execution Time",
                    },
                    {
                        "expr": "aiculture_memory_usage_bytes / 1024 / 1024",
                        "legendFormat": "Memory Usage (MB)",
                    },
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16},
                "yAxes": [{"label": "Time (s) / Memory (MB)", "min": 0}],
            },
        ]

        dashboard = {
            "dashboard": {
                "id": None,
                "title": _("AICultureKit Monitoring"),
                "description": _(
                    "Comprehensive monitoring dashboard for development culture metrics"
                ),
                "tags": ["aiculture", "monitoring", "culture"],
                "timezone": "browser",
                "panels": panels,
                "time": {"from": "now-1h", "to": "now"},
                "timepicker": {},
                "templating": {"list": []},
                "annotations": {"list": []},
                "refresh": "30s",
                "schemaVersion": 27,
                "version": 1,
                "links": [],
            },
            "overwrite": True,
        }

        return dashboard

    def generate_alertmanager_config(self) -> Dict[str, Any]:
        """生成Alertmanager配置"""
        return {
            "global": {
                "smtp_smarthost": "localhost:587",
                "smtp_from": "demo@placeholder.local",
            },
            "route": {
                "group_by": ["alertname"],
                "group_wait": "10s",
                "group_interval": "10s",
                "repeat_interval": "1h",
                "receiver": "web.hook",
            },
            "receivers": [
                {
                    "name": "web.hook",
                    "webhook_configs": [
                        {"url": "http://localhost:5001/webhook", "send_resolved": True}
                    ],
                }
            ],
            "inhibit_rules": [
                {
                    "source_match": {"severity": "critical"},
                    "target_match": {"severity": "warning"},
                    "equal": ["alertname", "dev", "instance"],
                }
            ],
        }

    def save_all_configs(self) -> None:
        """保存所有配置文件"""
        # Prometheus配置
        prometheus_config = self.generate_prometheus_config()
        with open(self.prometheus_config, "w") as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)

        # 告警规则
        alert_rules = self.generate_alert_rules()
        with open(self.config_dir / "alert_rules.yml", "w") as f:
            yaml.dump(alert_rules, f, default_flow_style=False)

        # Grafana数据源
        datasource_config = self.generate_grafana_datasource()
        with open(self.grafana_config / "datasources" / "prometheus.yml", "w") as f:
            yaml.dump(datasource_config, f, default_flow_style=False)

        # Grafana仪表板
        dashboard_config = self.generate_culture_dashboard()
        with open(self.grafana_config / "dashboards" / "culture_dashboard.json", "w") as f:
            json.dump(dashboard_config, f, indent=2, ensure_ascii=False)

        # Alertmanager配置
        alertmanager_config = self.generate_alertmanager_config()
        with open(self.alertmanager_config, "w") as f:
            yaml.dump(alertmanager_config, f, default_flow_style=False)

        print(_("Monitoring configurations saved to {dir}").format(dir=self.config_dir))

    def setup_default_monitoring(self) -> None:
        """设置默认监控配置"""
        # 添加默认指标
        default_metrics = [
            MetricConfig(
                name="aiculture_quality_score",
                description="Overall culture quality score",
                metric_type="gauge",
                labels=["project"],
                help_text="Culture quality score from 0 to 100",
                unit="percent",
            ),
            MetricConfig(
                name="aiculture_violations_total",
                description="Total number of culture violations",
                metric_type="counter",
                labels=["principle", "severity"],
                help_text="Total culture violations by principle and severity",
            ),
            MetricConfig(
                name="aiculture_test_coverage_percent",
                description="Test coverage percentage",
                metric_type="gauge",
                labels=["project"],
                help_text="Test coverage percentage",
                unit="percent",
            ),
            MetricConfig(
                name="aiculture_security_issues",
                description="Number of security issues",
                metric_type="gauge",
                labels=["severity", "type"],
                help_text="Number of security issues by severity and type",
            ),
            MetricConfig(
                name="aiculture_execution_time_seconds",
                description="Execution time in seconds",
                metric_type="histogram",
                labels=["operation"],
                help_text="Time spent executing operations",
                unit="seconds",
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
            ),
        ]

        for metric in default_metrics:
            self.add_metric(metric)

        # 添加默认告警规则
        default_alerts = [
            AlertRule(
                name="CultureQualityLow",
                description="Culture quality score is below threshold",
                expression="aiculture_quality_score < 70",
                duration="5m",
                severity="warning",
                labels={"team": "development"},
                annotations={
                    "summary": "Culture quality score is low",
                    "description": "Culture quality score has been below 70 for more than 5 minutes",
                },
            ),
            AlertRule(
                name="TestCoverageLow",
                description="Test coverage is below threshold",
                expression="aiculture_test_coverage_percent < 80",
                duration="10m",
                severity="warning",
                labels={"team": "development"},
                annotations={
                    "summary": "Test coverage is low",
                    "description": "Test coverage has been below 80% for more than 10 minutes",
                },
            ),
            AlertRule(
                name="SecurityIssuesHigh",
                description="High number of security issues",
                expression='sum(aiculture_security_issues{severity="high"}) > 0',
                duration="1m",
                severity="critical",
                labels={"team": "security"},
                annotations={
                    "summary": "High severity security issues detected",
                    "description": "{{ $value }} high severity security issues have been detected",
                },
            ),
        ]

        for alert in default_alerts:
            self.add_alert_rule(alert)


# 使用示例
if __name__ == "__main__":
    # 创建监控配置管理器
    config_manager = MonitoringConfigManager(Path("./monitoring"))

    # 设置默认监控
    config_manager.setup_default_monitoring()

    # 保存所有配置
    config_manager.save_all_configs()

    print(_("Monitoring setup completed!"))
