#!/usr/bin/env python3
"""
监控配置测试
"""

import pytest
import tempfile
from pathlib import Path

from aiculture.monitoring_config import MonitoringConfigManager, MetricConfig


class TestMonitoringConfigManager:
    """测试监控配置管理器"""

    def setup_method(self):
        """设置测试"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = MonitoringConfigManager(self.temp_dir)

    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager.project_path == self.temp_dir
        assert hasattr(self.manager, "metrics")
        assert isinstance(self.manager.metrics, dict)
        assert hasattr(self.manager, "alerts")
        assert isinstance(self.manager.alerts, dict)

    def test_add_metric(self):
        """测试添加指标"""
        metric = MetricConfig(
            name="response_time",
            type="histogram",
            description="API response time",
            labels=["endpoint", "method"],
            thresholds={"warning": 1.0, "critical": 5.0},
        )

        self.manager.add_metric("api_response_time", metric)
        assert "api_response_time" in self.manager.metrics
        assert self.manager.metrics["api_response_time"] == metric

    def test_get_metric(self):
        """测试获取指标"""
        metric = MetricConfig(
            name="cpu_usage", type="gauge", description="CPU usage percentage"
        )

        self.manager.add_metric("cpu", metric)

        # 获取存在的指标
        retrieved_metric = self.manager.get_metric("cpu")
        assert retrieved_metric == metric

        # 获取不存在的指标
        assert self.manager.get_metric("nonexistent") is None

    def test_remove_metric(self):
        """测试移除指标"""
        metric = MetricConfig(
            name="memory_usage", type="gauge", description="Memory usage"
        )

        self.manager.add_metric("memory", metric)
        assert "memory" in self.manager.metrics

        # 移除指标
        success = self.manager.remove_metric("memory")
        assert success
        assert "memory" not in self.manager.metrics

        # 移除不存在的指标
        assert not self.manager.remove_metric("nonexistent")

    def test_update_metric_thresholds(self):
        """测试更新指标阈值"""
        metric = MetricConfig(
            name="error_rate",
            type="counter",
            description="Error rate",
            thresholds={"warning": 0.05, "critical": 0.1},
        )

        self.manager.add_metric("errors", metric)

        # 更新阈值
        new_thresholds = {"warning": 0.03, "critical": 0.08}
        success = self.manager.update_metric_thresholds("errors", new_thresholds)
        assert success

        updated_metric = self.manager.get_metric("errors")
        assert updated_metric.thresholds == new_thresholds

        # 更新不存在的指标
        assert not self.manager.update_metric_thresholds("nonexistent", new_thresholds)

    def test_add_alert_rule(self):
        """测试添加告警规则"""
        alert_rule = {
            "name": "high_cpu_usage",
            "condition": "cpu_usage > 80",
            "severity": "warning",
            "notification": ["email", "slack"],
        }

        self.manager.add_alert_rule("cpu_alert", alert_rule)
        assert "cpu_alert" in self.manager.alerts
        assert self.manager.alerts["cpu_alert"] == alert_rule

    def test_get_alert_rule(self):
        """测试获取告警规则"""
        alert_rule = {
            "name": "disk_space_low",
            "condition": "disk_usage > 90",
            "severity": "critical",
        }

        self.manager.add_alert_rule("disk_alert", alert_rule)

        # 获取存在的规则
        retrieved_rule = self.manager.get_alert_rule("disk_alert")
        assert retrieved_rule == alert_rule

        # 获取不存在的规则
        assert self.manager.get_alert_rule("nonexistent") is None

    def test_remove_alert_rule(self):
        """测试移除告警规则"""
        alert_rule = {
            "name": "memory_leak",
            "condition": "memory_growth > 10",
            "severity": "warning",
        }

        self.manager.add_alert_rule("memory_alert", alert_rule)
        assert "memory_alert" in self.manager.alerts

        # 移除规则
        success = self.manager.remove_alert_rule("memory_alert")
        assert success
        assert "memory_alert" not in self.manager.alerts

        # 移除不存在的规则
        assert not self.manager.remove_alert_rule("nonexistent")

    def test_generate_prometheus_config(self):
        """测试生成Prometheus配置"""
        # 添加一些指标
        metric1 = MetricConfig(
            name="http_requests_total",
            type="counter",
            description="Total HTTP requests",
        )
        metric2 = MetricConfig(
            name="http_request_duration",
            type="histogram",
            description="HTTP request duration",
        )

        self.manager.add_metric("requests", metric1)
        self.manager.add_metric("duration", metric2)

        # 生成配置
        config = self.manager.generate_prometheus_config()
        assert isinstance(config, dict)
        assert "global" in config
        assert "scrape_configs" in config
        assert "rule_files" in config

    def test_generate_grafana_dashboard(self):
        """测试生成Grafana仪表板"""
        # 添加一些指标
        metric1 = MetricConfig(
            name="cpu_usage", type="gauge", description="CPU usage percentage"
        )
        metric2 = MetricConfig(
            name="memory_usage", type="gauge", description="Memory usage percentage"
        )

        self.manager.add_metric("cpu", metric1)
        self.manager.add_metric("memory", metric2)

        # 生成仪表板
        dashboard = self.manager.generate_grafana_dashboard("System Metrics")
        assert isinstance(dashboard, dict)
        assert "dashboard" in dashboard
        assert dashboard["dashboard"]["title"] == "System Metrics"
        assert "panels" in dashboard["dashboard"]

    def test_validate_metric_config(self):
        """测试验证指标配置"""
        # 有效配置
        valid_metric = MetricConfig(
            name="valid_metric", type="counter", description="A valid metric"
        )
        assert self.manager.validate_metric_config(valid_metric)

        # 无效配置 - 缺少名称
        invalid_metric = MetricConfig(
            name="", type="counter", description="Invalid metric"
        )
        assert not self.manager.validate_metric_config(invalid_metric)

        # 无效配置 - 无效类型
        invalid_type_metric = MetricConfig(
            name="invalid_type", type="invalid_type", description="Invalid type metric"
        )
        assert not self.manager.validate_metric_config(invalid_type_metric)

    def test_export_config(self):
        """测试导出配置"""
        # 添加一些配置
        metric = MetricConfig(
            name="test_metric", type="gauge", description="Test metric"
        )
        alert = {
            "name": "test_alert",
            "condition": "test_metric > 100",
            "severity": "warning",
        }

        self.manager.add_metric("test", metric)
        self.manager.add_alert_rule("test_alert", alert)

        # 导出配置
        config = self.manager.export_config()
        assert isinstance(config, dict)
        assert "metrics" in config
        assert "alerts" in config
        assert "test" in config["metrics"]
        assert "test_alert" in config["alerts"]

    def test_import_config(self):
        """测试导入配置"""
        config = {
            "metrics": {
                "imported_metric": {
                    "name": "imported_metric",
                    "type": "counter",
                    "description": "Imported metric",
                }
            },
            "alerts": {
                "imported_alert": {
                    "name": "imported_alert",
                    "condition": "imported_metric > 50",
                    "severity": "critical",
                }
            },
        }

        success = self.manager.import_config(config)
        assert success
        assert "imported_metric" in self.manager.metrics
        assert "imported_alert" in self.manager.alerts

        # 测试无效配置
        invalid_config = {"invalid": "config"}
        assert not self.manager.import_config(invalid_config)

    def test_get_metrics_summary(self):
        """测试获取指标摘要"""
        # 添加不同类型的指标
        counter_metric = MetricConfig(
            name="counter1", type="counter", description="Counter"
        )
        gauge_metric = MetricConfig(name="gauge1", type="gauge", description="Gauge")
        histogram_metric = MetricConfig(
            name="hist1", type="histogram", description="Histogram"
        )

        self.manager.add_metric("c1", counter_metric)
        self.manager.add_metric("g1", gauge_metric)
        self.manager.add_metric("h1", histogram_metric)

        summary = self.manager.get_metrics_summary()
        assert isinstance(summary, dict)
        assert "total_metrics" in summary
        assert "by_type" in summary
        assert summary["total_metrics"] == 3
        assert summary["by_type"]["counter"] == 1
        assert summary["by_type"]["gauge"] == 1
        assert summary["by_type"]["histogram"] == 1

    def test_get_alerts_summary(self):
        """测试获取告警摘要"""
        # 添加不同严重程度的告警
        warning_alert = {"name": "warn1", "severity": "warning"}
        critical_alert = {"name": "crit1", "severity": "critical"}
        info_alert = {"name": "info1", "severity": "info"}

        self.manager.add_alert_rule("w1", warning_alert)
        self.manager.add_alert_rule("c1", critical_alert)
        self.manager.add_alert_rule("i1", info_alert)

        summary = self.manager.get_alerts_summary()
        assert isinstance(summary, dict)
        assert "total_alerts" in summary
        assert "by_severity" in summary
        assert summary["total_alerts"] == 3
        assert summary["by_severity"]["warning"] == 1
        assert summary["by_severity"]["critical"] == 1
        assert summary["by_severity"]["info"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
