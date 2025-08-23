#!/usr/bin/env python3
"""AICultureKit 自动质量报告生成器
生成详细的HTML质量报告，包含代码覆盖率、测试结果、代码质量指标等
"""

import json
import subprocess
from datetime import datetime


def run_command(cmd, capture_output=True) -> None:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            check=False,
            shell=True,  # TODO:    考虑使用更安全的方式, capture_output=capture_output, text=True
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def get_test_results() -> None:
    """获取测试结果"""
    cmd = (
        "python -m pytest --tb=no -q --json-report --json-report-file=test-report.json"
    )
    run_command(cmd)

    try:
        with open("test-report.json") as f:
            data = json.load(f)
        return {
            "total": data.get("summary", {}).get("total", 0),
            "passed": data.get("summary", {}).get("passed", 0),
            "failed": data.get("summary", {}).get("failed", 0),
            "duration": data.get("duration", 0),
        }
    except Exception:
        return {"total": 0, "passed": 0, "failed": 0, "duration": 0}


def get_coverage_info() -> None:
    """获取代码覆盖率信息"""
    cmd = "python -m pytest --cov=aiculture --cov-report=json --tb=no -q"
    run_command(cmd)

    try:
        with open("coverage.json") as f:
            data = json.load(f)
        return {
            "percent": data.get("totals", {}).get("percent_covered", 0),
            "lines_covered": data.get("totals", {}).get("covered_lines", 0),
            "lines_total": data.get("totals", {}).get("num_statements", 0),
        }
    except Exception:
        return {"percent": 0, "lines_covered": 0, "lines_total": 0}


def get_code_metrics() -> None:
    """获取代码指标"""
    # 代码行数
    total_lines = run_command(
        "find aiculture -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $1}'",
    )

    # 文件数量
    file_count = run_command("find aiculture -name '*.py' | wc -l")

    # Git提交信息
    commit_hash = run_command("git rev-parse --short HEAD")
    commit_date = run_command("git log -1 --format=%cd --date=short")

    return {
        "total_lines": int(total_lines) if total_lines.isdigit() else 0,
        "file_count": int(file_count) if file_count.isdigit() else 0,
        "commit_hash": commit_hash,
        "commit_date": commit_date,
    }


def get_quality_issues() -> None:
    """获取代码质量问题"""
    # Flake8检查
    flake8_output = run_command("flake8 . --count --statistics")
    flake8_count = len(flake8_output.split("\n")) if flake8_output else 0

    # MyPy检查
    mypy_output = run_command("mypy aiculture --ignore-missing-imports")
    mypy_errors = mypy_output.count("error:") if mypy_output else 0

    return {
        "flake8_issues": flake8_count,
        "mypy_errors": mypy_errors,
    }


def generate_html_report(data) -> None:
    """生成HTML报告"""
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AICultureKit 质量报告</title>
    <style>
        body {{ font-family: -apple-system,
            BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; padding: 30px; }}
        .metric {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .metric h3 {{ margin: 0 0 10px 0; color: #333; }}
        .metric .value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .metric .label {{ color: #666; font-size: 0.9em; }}
        .success {{ border-left-color: #28a745; }}
        .success .value {{ color: #28a745; }}
        .warning {{ border-left-color: #ffc107; }}
        .warning .value {{ color: #ffc107; }}
        .danger {{ border-left-color: #dc3545; }}
        .danger .value {{ color: #dc3545; }}
        .footer {{ padding: 20px 30px; background: #f8f9fa; border-radius: 0 0 8px 8px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AICultureKit 质量报告</h1>
            <p>生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 提交: {
        data["metrics"]["commit_hash"]
    } | 日期: {data["metrics"]["commit_date"]}</p>
        </div>

        <div class="metrics">
            <div class="metric {
        "success" if data["tests"]["failed"] == 0 else "danger"
    }">
                <h3>🧪 测试结果</h3>
                <div class="value">{data["tests"]["passed"]}/{
        data["tests"]["total"]
    }</div>
                <div class="label">通过/总计 ({data["tests"]["duration"]:.2f}s)</div>
            </div>

            <div class="metric {
        "success"
        if data["coverage"]["percent"] >= 80
        else "warning"
        if data["coverage"]["percent"] >= 30
        else "danger"
    }">
                <h3>📊 代码覆盖率</h3>
                <div class="value">{data["coverage"]["percent"]:.1f}%</div>
                <div class="label">{data["coverage"]["lines_covered"]}/{
        data["coverage"]["lines_total"]
    } 行</div>
            </div>

            <div class="metric">
                <h3>📏 代码规模</h3>
                <div class="value">{data["metrics"]["total_lines"]:,}</div>
                <div class="label">{data["metrics"]["file_count"]} 个Python文件</div>
            </div>

            <div class="metric {
        "success" if data["quality"]["flake8_issues"] == 0 else "warning"
    }">
                <h3>🔍 代码质量</h3>
                <div class="value">{data["quality"]["flake8_issues"]}</div>
                <div class="label">Flake8 问题</div>
            </div>

            <div class="metric {
        "success" if data["quality"]["mypy_errors"] == 0 else "warning"
    }">
                <h3>🔧 类型检查</h3>
                <div class="value">{data["quality"]["mypy_errors"]}</div>
                <div class="label">MyPy 错误</div>
            </div>

            <div class="metric success">
                <h3>🎯 质量分数</h3>
                <div class="value">{
        max(
            0,
            100
            - data["tests"]["failed"] * 10
            - data["quality"]["flake8_issues"] * 2
            - data["quality"]["mypy_errors"],
        )
    }</div>
                <div class="label">综合评分</div>
            </div>
        </div>

        <div class="footer">
            <p>🤖 由 AICultureKit 自动生成 | 让AI协作开发更有文化</p>
        </div>
    </div>
</body>
</html>
"""

    with open("quality-report.html", "w", encoding="utf-8") as f:
        f.write(html_template)


def main() -> None:
    """主函数"""
    print("🚀 生成AICultureKit质量报告...")

    # 收集数据
    data = {
        "tests": get_test_results(),
        "coverage": get_coverage_info(),
        "metrics": get_code_metrics(),
        "quality": get_quality_issues(),
    }

    # 生成报告
    generate_html_report(data)

    print("✅ 质量报告已生成: quality-report.html")
    print(f"📊 测试: {data['tests']['passed']}/{data['tests']['total']} 通过")
    print(f"📈 覆盖率: {data['coverage']['percent']:.1f}%")
    print(f"🔍 质量问题: {data['quality']['flake8_issues']} 个")


if __name__ == "__main__":
    main()
