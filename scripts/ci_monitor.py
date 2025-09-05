#!/usr/bin/env python3
"""
CI监控工具 - 实时跟踪GitHub Actions工作流状态和日志分析

主要功能：
1. 获取最新CI运行状态
2. 实时监控工作流执行过程
3. 下载并解析CI日志
4. 智能分析失败原因并提供修复建议
5. 支持多种查看模式和输出格式

设计理念：
- 提供开发者友好的CI状态可视化
- 快速定位CI失败的根本原因
- 减少盲目推送和等待的时间成本
"""

import argparse
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests


class GitHubCIMonitor:
    """GitHub Actions CI监控器 - 提供完整的CI状态跟踪和分析能力"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.token = self._get_github_token()
        self.repo_info = self._get_repository_info()
        self.api_base = "https://api.github.com"

        # API请求头配置 - 确保有足够的权限访问CI信息
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AICultureKit-CI-Monitor/1.0",
        }

    def _get_github_token(self) -> Optional[str]:
        """获取GitHub访问令牌 - 支持多种配置方式，优先级递减"""
        # 优先级1: 环境变量GITHUB_TOKEN
        token = os.getenv("GITHUB_TOKEN")
        if token:
            return token

        # 优先级2: 环境变量GH_TOKEN (GitHub CLI使用的标准变量)
        token = os.getenv("GH_TOKEN")
        if token:
            return token

        # 优先级3: Git配置中的token
        try:
            result = subprocess.run(
                ["git", "config", "--get", "github.token"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass

        print("⚠️  未找到GitHub访问令牌")
        print("💡 请设置环境变量: export GITHUB_TOKEN=your_token")
        return None

    def _get_repository_info(self) -> Dict[str, str]:
        """从Git远程仓库获取GitHub仓库信息 - 解析owner/repo格式"""
        try:
            # 获取远程origin的URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode != 0:
                raise Exception("无法获取Git远程仓库URL")

            remote_url = result.stdout.strip()

            # 解析不同格式的GitHub URL (HTTPS和SSH)
            if remote_url.startswith("git@github.com:"):
                # SSH格式: git@github.com:owner/repo.git
                repo_path = remote_url.replace("git@github.com:", "")
            elif "github.com" in remote_url:
                # HTTPS格式: https://github.com/owner/repo.git
                parsed = urlparse(remote_url)
                repo_path = parsed.path.lstrip("/")
            else:
                raise Exception(f"不支持的远程仓库URL格式: {remote_url}")

            # 移除.git后缀并分割owner/repo
            repo_path = repo_path.replace(".git", "")
            parts = repo_path.split("/")

            if len(parts) != 2:
                raise Exception(f"无法解析仓库路径: {repo_path}")

            return {"owner": parts[0], "repo": parts[1], "full_name": repo_path}

        except Exception as e:
            print(f"❌ 获取仓库信息失败: {e}")
            print("💡 请确保在Git仓库目录中运行，且已配置GitHub远程仓库")
            return {}

    def get_latest_workflows(self, limit: int = 10) -> List[Dict]:
        """获取最新的工作流运行记录 - 按时间倒序排列，便于快速查看最新状态"""
        if not self.token or not self.repo_info:
            return []

        url = f"{self.api_base}/repos/{self.repo_info['full_name']}/actions/runs"
        params = {
            "per_page": limit,
            "status": "completed,in_progress,queued",  # 包含所有状态的运行
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get("workflow_runs", [])

        except Exception as e:
            print(f"❌ 获取工作流失败: {e}")
            return []

    def get_workflow_jobs(self, run_id: int) -> List[Dict]:
        """获取特定工作流运行的所有作业详情 - 用于详细分析每个Job的执行状态"""
        if not self.token or not self.repo_info:
            return []

        url = f"{self.api_base}/repos/{self.repo_info['full_name']}/actions/runs/{run_id}/jobs"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return data.get("jobs", [])

        except requests.RequestException as e:
            print(f"❌ 获取作业详情失败: {e}")
            return []

    def get_job_logs(self, job_id: int) -> str:
        """获取特定作业的日志内容 - 用于详细分析失败原因"""
        if not self.token or not self.repo_info:
            return ""

        url = f"{self.api_base}/repos/{self.repo_info['full_name']}/actions/jobs/{job_id}/logs"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            return response.text

        except requests.RequestException as e:
            print(f"❌ 获取作业日志失败: {e}")
            return ""

    def analyze_failure_reason(self, logs: str) -> Dict[str, Any]:
        """智能分析CI失败原因 - 使用正则匹配和关键词识别常见问题"""
        analysis: Dict[str, Any] = {
            "failure_type": "unknown",
            "details": [],
            "suggestions": [],
            "severity": "medium",
        }

        # 定义常见失败模式和对应的修复建议
        failure_patterns: List[Dict[str, Any]] = [
            {
                "name": "dependency_conflict",
                "pattern": r"(?i)(dependency.*conflict|version.*conflict|packaging.*conflict)",
                "severity": "high",
                "suggestions": [
                    "检查requirements.txt和requirements-dev.txt中的版本冲突",
                    "尝试升级冲突的包到兼容版本",
                    "运行本地环境检查: make env-check",
                ],
            },
            {
                "name": "missing_dependency",
                "pattern": r"(?i)(ModuleNotFoundError|ImportError|No module named)",
                "severity": "high",
                "suggestions": [
                    "检查缺失的依赖包是否在requirements文件中",
                    "确保所有依赖版本正确指定",
                    "运行: pip install -r requirements-dev.txt",
                ],
            },
            {
                "name": "code_style",
                "pattern": r"(?i)(flake8.*error|black.*would reformat|isort.*would reformat)",
                "severity": "low",
                "suggestions": [
                    "运行代码格式化: make fix",
                    "检查代码风格: make quality",
                    "提交前运行: make prepush",
                ],
            },
            {
                "name": "test_failure",
                "pattern": r"(?i)(test.*failed|assertion.*error|pytest.*failed)",
                "severity": "medium",
                "suggestions": ["本地运行测试: make test", "检查测试用例是否需要更新", "查看具体的测试失败日志"],
            },
            {
                "name": "type_error",
                "pattern": r"(?i)(mypy.*error|type.*error)",
                "severity": "medium",
                "suggestions": ["运行类型检查: mypy src/", "添加缺失的类型注解", "修复类型不匹配问题"],
            },
        ]

        # 逐一检查失败模式
        for pattern_info in failure_patterns:
            if re.search(pattern_info["pattern"], logs):
                analysis["failure_type"] = pattern_info["name"]
                analysis["severity"] = pattern_info["severity"]
                analysis["suggestions"].extend(pattern_info["suggestions"])

                # 提取具体错误详情
                matches = re.findall(
                    pattern_info["pattern"] + r".*", logs, re.IGNORECASE
                )
                analysis["details"].extend(matches[:3])  # 最多显示3个匹配项
                break

        return analysis

    def display_workflow_status(self, workflows: List[Dict]) -> None:
        """美观地显示工作流状态列表 - 提供清晰的状态概览和快速诊断信息"""
        if not workflows:
            print("📭 未找到工作流运行记录")
            return

        print("\n🚀 GitHub Actions CI状态监控")
        print("=" * 80)

        for i, workflow in enumerate(workflows):
            # 状态图标映射 - 直观显示运行结果
            status_icons = {
                "completed": "✅" if workflow.get("conclusion") == "success" else "❌",
                "in_progress": "🔄",
                "queued": "⏳",
                "requested": "📋",
            }

            icon = status_icons.get(workflow.get("status", ""), "❓")
            conclusion = workflow.get("conclusion", workflow.get("status", "unknown"))

            # 时间格式化 - 显示相对时间更直观
            created_at = datetime.fromisoformat(
                workflow["created_at"].replace("Z", "+00:00")
            )
            time_ago = self._format_time_ago(created_at)

            print(
                f"\n{i+1}. {icon} #{workflow['run_number']} - {workflow['head_commit']['message'][:60]}..."
            )
            print(f"   📅 {time_ago} | 🌿 {workflow['head_branch']} | 📊 {conclusion}")
            print(f"   🔗 {workflow['html_url']}")

            # 对于失败的工作流，提供快速诊断选项
            if workflow.get("conclusion") == "failure":
                print(
                    f"   💡 快速诊断: python scripts/ci_monitor.py --analyze {workflow['id']}"
                )

    def display_detailed_analysis(self, run_id: int) -> None:
        """显示特定工作流运行的详细分析 - 深度诊断失败原因和修复建议"""
        print(f"\n🔍 分析工作流运行 #{run_id}")
        print("=" * 60)

        jobs = self.get_workflow_jobs(run_id)
        if not jobs:
            print("❌ 无法获取作业信息")
            return

        for job in jobs:
            print(f"\n📋 作业: {job['name']}")
            print(f"   状态: {job['status']} | 结论: {job.get('conclusion', 'N/A')}")

            if job.get("conclusion") == "failure":
                print("   📜 获取失败日志...")
                logs = self.get_job_logs(job["id"])

                if logs:
                    analysis = self.analyze_failure_reason(logs)

                    print(f"   🎯 失败类型: {analysis['failure_type']}")
                    print(f"   ⚡ 严重程度: {analysis['severity']}")

                    if analysis["details"]:
                        print("   📄 错误详情:")
                        for detail in analysis["details"]:
                            print(f"      • {detail}")

                    if analysis["suggestions"]:
                        print("   💡 修复建议:")
                        for suggestion in analysis["suggestions"]:
                            print(f"      🔧 {suggestion}")
                else:
                    print("   ⚠️  无法获取日志内容")

    def monitor_realtime(self, interval: int = 30) -> None:
        """实时监控CI状态 - 持续跟踪最新推送的CI执行过程"""
        print(f"🔄 启动实时CI监控 (每{interval}秒刷新)")
        print("💡 按 Ctrl+C 停止监控\n")

        last_run_id = None

        try:
            while True:
                workflows = self.get_latest_workflows(limit=1)

                if workflows:
                    current_workflow = workflows[0]
                    current_run_id = current_workflow["id"]

                    # 检测到新的工作流运行
                    if last_run_id != current_run_id:
                        print(f"\n🚀 检测到新的CI运行 #{current_workflow['run_number']}")
                        print(
                            f"📝 提交: {current_workflow['head_commit']['message'][:80]}"
                        )
                        last_run_id = current_run_id

                    # 显示当前状态
                    status = current_workflow.get("status")
                    conclusion = current_workflow.get("conclusion")

                    if status == "in_progress":
                        print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] CI正在运行...")
                    elif status == "completed":
                        if conclusion == "success":
                            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] CI成功完成！")
                            break
                        else:
                            print(
                                f"❌ [{datetime.now().strftime('%H:%M:%S')}] CI失败: {conclusion}"
                            )
                            print(
                                f"💡 运行详细分析: python scripts/ci_monitor.py --analyze {current_run_id}"
                            )
                            break

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n⏹️  监控已停止")

    def _format_time_ago(self, dt: datetime) -> str:
        """格式化相对时间显示 - 提供人性化的时间描述"""
        now = datetime.now(timezone.utc)
        diff = now - dt.replace(tzinfo=timezone.utc)

        if diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"


def main():
    """主程序入口 - 提供命令行接口和多种使用模式"""
    parser = argparse.ArgumentParser(
        description="GitHub Actions CI监控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python scripts/ci_monitor.py                    # 查看最新CI状态
  python scripts/ci_monitor.py --monitor          # 实时监控CI执行
  python scripts/ci_monitor.py --analyze 123456   # 深度分析特定运行
  python scripts/ci_monitor.py --history 20       # 查看历史记录
        """,
    )

    parser.add_argument("--monitor", "-m", action="store_true", help="启动实时监控模式")

    parser.add_argument("--analyze", "-a", type=int, help="深度分析指定的工作流运行ID")

    parser.add_argument(
        "--history", "-H", type=int, default=10, help="显示历史运行记录数量 (默认: 10)"
    )

    parser.add_argument(
        "--interval", "-i", type=int, default=30, help="实时监控刷新间隔(秒) (默认: 30)"
    )

    args = parser.parse_args()

    # 初始化CI监控器
    monitor = GitHubCIMonitor()

    if not monitor.token:
        print("❌ 需要GitHub访问令牌才能监控CI状态")
        return 1

    if not monitor.repo_info:
        print("❌ 无法识别当前仓库信息")
        return 1

    # 根据参数执行对应功能
    if args.monitor:
        monitor.monitor_realtime(args.interval)
    elif args.analyze:
        monitor.display_detailed_analysis(args.analyze)
    else:
        workflows = monitor.get_latest_workflows(args.history)
        monitor.display_workflow_status(workflows)

    return 0


if __name__ == "__main__":
    exit(main())
