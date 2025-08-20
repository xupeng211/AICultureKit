#!/usr/bin/env python3
"""
AICultureKit 实时质量监控系统
监控代码质量变化，自动生成报告和通知
"""

import json
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict


class QualityMonitor:
    """质量监控器"""

    def __init__(self, project_path: Path = None) -> None:
        """TODO: 添加函数文档字符串"""
        self.project_path = project_path or Path.cwd()
        self.db_path = self.project_path / ".quality_history.db"
        self.init_database()

    def init_database(self) -> None:
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                commit_hash TEXT,
                test_count INTEGER,
                test_passed INTEGER,
                coverage_percent REAL,
                flake8_issues INTEGER,
                mypy_errors INTEGER,
                file_count INTEGER,
                line_count INTEGER,
                quality_score INTEGER
            )
        '''
        )

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS quality_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE
            )
        '''
        )

        conn.commit()
        conn.close()

    def run_command(self, cmd: str) -> tuple[bool, str]:
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,  # TODO:    考虑使用更安全的方式, capture_output=True, text=True, cwd=self.project_path
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)

    def collect_metrics(self) -> Dict[str, Any]:
        """收集当前的质量指标"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "commit_hash": "",
            "test_count": 0,
            "test_passed": 0,
            "coverage_percent": 0.0,
            "flake8_issues": 0,
            "mypy_errors": 0,
            "file_count": 0,
            "line_count": 0,
            "quality_score": 0,
        }

        # Git信息
        success, output = self.run_command("git rev-parse --short HEAD")
        if success:
            metrics["commit_hash"] = output

        # 测试信息
        success, output = self.run_command(
            "python -m pytest --tb=no -q --json-report --json-report-file=temp_test_report.json"
        )
        if success and Path("temp_test_report.json").exists():
            try:
                with open("temp_test_report.json", "r") as f:
                    test_data = json.load(f)
                metrics["test_count"] = test_data.get("summary", {}).get("total", 0)
                metrics["test_passed"] = test_data.get("summary", {}).get("passed", 0)
                Path("temp_test_report.json").unlink()  # 清理临时文件
            except Exception:
                pass  # TODO:   添加适当的异常处理
        # 覆盖率信息
        success, output = self.run_command(
            "python -m pytest --cov=aiculture --cov-report=json --tb=no -q"
        )
        if success and Path("coverage.json").exists():
            try:
                with open("coverage.json", "r") as f:
                    cov_data = json.load(f)
                metrics["coverage_percent"] = cov_data.get("totals", {}).get("percent_covered", 0)
            except Exception:
                pass  # TODO:   添加适当的异常处理
        # Flake8问题
        success, output = self.run_command("flake8 . --count")
        if success and output.isdigit():
            metrics["flake8_issues"] = int(output)

        # MyPy错误
        success, output = self.run_command("mypy aiculture --ignore-missing-imports")
        if success:
            metrics["mypy_errors"] = output.count("error:")

        # 代码统计
        success, output = self.run_command("find aiculture -name '*.py' | wc -l")
        if success and output.isdigit():
            metrics["file_count"] = int(output)

        success, output = self.run_command(
            "find aiculture -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $1}'"
        )
        if success and output.isdigit():
            metrics["line_count"] = int(output)

        # 计算质量分数
        metrics["quality_score"] = self.calculate_quality_score(metrics)

        return metrics

    def calculate_quality_score(self, metrics: Dict[str, Any]) -> int:
        """计算质量分数"""
        score = 100

        # 测试失败扣分
        failed_tests = metrics["test_count"] - metrics["test_passed"]
        score -= failed_tests * 10

        # 覆盖率低扣分
        if metrics["coverage_percent"] < 80:
            score -= (80 - metrics["coverage_percent"]) * 0.5

        # 代码质量问题扣分
        score -= metrics["flake8_issues"] * 2
        score -= metrics["mypy_errors"] * 1

        return max(0, int(score))

    def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """保存指标到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            '''
            INSERT INTO quality_metrics
            (timestamp, commit_hash, test_count, test_passed, coverage_percent,
             flake8_issues, mypy_errors, file_count, line_count, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
            (
                metrics["timestamp"],
                metrics["commit_hash"],
                metrics["test_count"],
                metrics["test_passed"],
                metrics["coverage_percent"],
                metrics["flake8_issues"],
                metrics["mypy_errors"],
                metrics["file_count"],
                metrics["line_count"],
                metrics["quality_score"],
            ),
        )

        conn.commit()
        conn.close()

    def check_quality_alerts(self, current_metrics: Dict[str, Any]) -> None:
        """检查质量警报"""
        alerts = []

        # 获取历史数据进行对比
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT * FROM quality_metrics
            ORDER BY timestamp DESC
            LIMIT 2
        '''
        )

        rows = cursor.fetchall()
        if len(rows) >= 2:
            prev_metrics = dict(zip([col[0] for col in cursor.description], rows[1]))

            # 检查质量下降
            if current_metrics["quality_score"] < prev_metrics["quality_score"] - 5:
                alerts.append(
                    {
                        "type": "quality_decline",
                        "message": f"质量分数下降: {prev_metrics['quality_score']} → {current_metrics['quality_score']}",
                        "severity": "warning",
                    }
                )

            # 检查测试失败增加
            prev_failed = prev_metrics["test_count"] - prev_metrics["test_passed"]
            curr_failed = current_metrics["test_count"] - current_metrics["test_passed"]
            if curr_failed > prev_failed:
                alerts.append(
                    {
                        "type": "test_regression",
                        "message": f"测试失败增加: {prev_failed} → {curr_failed}",
                        "severity": "error",
                    }
                )

            # 检查覆盖率下降
            if current_metrics["coverage_percent"] < prev_metrics["coverage_percent"] - 2:
                alerts.append(
                    {
                        "type": "coverage_decline",
                        "message": f"覆盖率下降: {prev_metrics['coverage_percent']:.1f}% → {current_metrics['coverage_percent']:.1f}%",
                        "severity": "warning",
                    }
                )

        # 检查绝对阈值
        if current_metrics["coverage_percent"] < 30:
            alerts.append(
                {
                    "type": "low_coverage",
                    "message": f"代码覆盖率过低: {current_metrics['coverage_percent']:.1f}%",
                    "severity": "warning",
                }
            )

        if current_metrics["test_count"] - current_metrics["test_passed"] > 0:
            alerts.append(
                {
                    "type": "test_failures",
                    "message": f"有 {current_metrics['test_count'] - current_metrics['test_passed']} 个测试失败",
                    "severity": "error",
                }
            )

        # 保存警报
        for alert in alerts:
            cursor.execute(
                '''
                INSERT INTO quality_alerts (timestamp, alert_type, message, severity)
                VALUES (?, ?, ?, ?)
            ''',
                (
                    current_metrics["timestamp"],
                    alert["type"],
                    alert["message"],
                    alert["severity"],
                ),
            )

        conn.commit()
        conn.close()

        return alerts

    def generate_trend_report(self, days: int = 7) -> str:
        """生成趋势报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute(
            '''
            SELECT * FROM quality_metrics
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''',
            (since_date,),
        )

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        if not rows:
            return "📊 暂无历史数据"

        # 计算趋势
        latest = dict(zip(columns, rows[0]))
        oldest = dict(zip(columns, rows[-1]))

        report = f"""
📊 AICultureKit 质量趋势报告 (最近{days}天)
{'='*50}

📈 总体趋势:
  质量分数: {oldest['quality_score']} → {latest['quality_score']} ({latest['quality_score'] - oldest['quality_score']:+d})
  测试通过: {oldest['test_passed']}/{oldest['test_count']} → {latest['test_passed']}/{latest['test_count']}
  代码覆盖率: {oldest['coverage_percent']:.1f}% → {latest['coverage_percent']:.1f}% ({latest['coverage_percent'] - oldest['coverage_percent']:+.1f}%)
  代码行数: {oldest['line_count']} → {latest['line_count']} ({latest['line_count'] - oldest['line_count']:+d})

🔍 质量问题:
  Flake8问题: {oldest['flake8_issues']} → {latest['flake8_issues']} ({latest['flake8_issues'] - oldest['flake8_issues']:+d})
  MyPy错误: {oldest['mypy_errors']} → {latest['mypy_errors']} ({latest['mypy_errors'] - oldest['mypy_errors']:+d})

📅 数据点数: {len(rows)}
🕐 最后更新: {latest['timestamp']}
"""

        conn.close()
        return report

    def monitor_once(self) -> Dict[str, Any]:
        """执行一次监控"""
        print("🔍 收集质量指标...")
        metrics = self.collect_metrics()

        print("💾 保存指标...")
        self.save_metrics(metrics)

        print("🚨 检查警报...")
        alerts = self.check_quality_alerts(metrics)

        # 显示结果
        print(f"\n📊 当前质量指标:")
        print(f"  质量分数: {metrics['quality_score']}/100")
        print(f"  测试通过: {metrics['test_passed']}/{metrics['test_count']}")
        print(f"  代码覆盖率: {metrics['coverage_percent']:.1f}%")
        print(f"  代码问题: {metrics['flake8_issues']} flake8, {metrics['mypy_errors']} mypy")

        if alerts:
            print(f"\n🚨 发现 {len(alerts)} 个警报:")
            for alert in alerts:
                emoji = "🔴" if alert["severity"] == "error" else "🟡"
                print(f"  {emoji} {alert['message']}")
        else:
            print("\n✅ 无质量警报")

        return {"metrics": metrics, "alerts": alerts}


def watch_mode(monitor: QualityMonitor, interval: int = 300) -> None:
    """监控模式，定期检查质量"""
    print(f"🔄 启动监控模式，每 {interval} 秒检查一次...")

    try:
        while True:
            result = monitor.monitor_once()

            # 如果有严重警报，立即通知
            critical_alerts = [a for a in result["alerts"] if a["severity"] == "error"]
            if critical_alerts:
                print(f"\n🚨 发现 {len(critical_alerts)} 个严重问题，建议立即处理！")

            print(f"\n⏰ 下次检查时间: {datetime.now() + timedelta(seconds=interval)}")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n👋 监控已停止")


def main() -> None:
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="AICultureKit 质量监控系统")
    parser.add_argument("--watch", action="store_true", help="启动监控模式")
    parser.add_argument("--interval", type=int, default=300, help="监控间隔(秒)")
    parser.add_argument("--trend", type=int, default=7, help="趋势报告天数")

    args = parser.parse_args()

    monitor = QualityMonitor()

    if args.watch:
        watch_mode(monitor, args.interval)
    else:
        # 执行一次监控
        result = monitor.monitor_once()

        # 生成趋势报告
        print("\n" + "=" * 50)
        trend_report = monitor.generate_trend_report(args.trend)
        print(trend_report)


if __name__ == "__main__":
    main()
