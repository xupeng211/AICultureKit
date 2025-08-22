"""Lint adapter for ruff/flake8"""

import json
import subprocess
from pathlib import Path
from typing import Any


class LintAdapter:
    """Lint工具适配器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def run_ruff(self, files: list[str] = None) -> list[dict[str, Any]]:
        """运行ruff检查"""
        problems = []

        try:
            cmd = ["python", "-m", "ruff", "check", "--output-format=json"]
            if files:
                cmd.extend(files)
            else:
                cmd.append(".")

            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                ruff_issues = json.loads(result.stdout)
                for issue in ruff_issues:
                    problems.append(
                        {
                            "tool": "ruff",
                            "type": "lint",
                            "severity": self._map_ruff_severity(issue.get("code", "")),
                            "file": issue.get("filename", ""),
                            "line": issue.get("location", {}).get("row", 0),
                            "column": issue.get("location", {}).get("column", 0),
                            "code": issue.get("code", ""),
                            "message": issue.get("message", ""),
                            "fix_suggestion": self._get_ruff_fix_suggestion(issue),
                            "blocking": self._is_blocking_lint_issue(
                                issue.get("code", ""),
                            ),
                        },
                    )

        except subprocess.TimeoutExpired:
            problems.append(
                {
                    "tool": "ruff",
                    "type": "system",
                    "severity": "error",
                    "message": "Ruff检查超时",
                    "blocking": True,
                },
            )
        except FileNotFoundError:
            problems.append(
                {
                    "tool": "ruff",
                    "type": "system",
                    "severity": "warning",
                    "message": "Ruff未安装，跳过lint检查",
                    "blocking": False,
                },
            )
        except Exception as e:
            problems.append(
                {
                    "tool": "ruff",
                    "type": "system",
                    "severity": "error",
                    "message": f"Ruff检查失败: {e}",
                    "blocking": False,
                },
            )

        return problems

    def run_flake8(self, files: list[str] = None) -> list[dict[str, Any]]:
        """运行flake8检查（备用）"""
        problems = []

        try:
            cmd = ["python", "-m", "flake8", "--format=json"]
            if files:
                cmd.extend(files)
            else:
                cmd.append(".")

            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # flake8没有原生JSON输出，需要解析文本输出
            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line:
                        parts = line.split(":", 3)
                        if len(parts) >= 4:
                            problems.append(
                                {
                                    "tool": "flake8",
                                    "type": "lint",
                                    "severity": "warning",
                                    "file": parts[0],
                                    "line": int(parts[1]) if parts[1].isdigit() else 0,
                                    "column": (
                                        int(parts[2]) if parts[2].isdigit() else 0
                                    ),
                                    "message": parts[3].strip(),
                                    "blocking": False,
                                },
                            )

        except Exception as e:
            problems.append(
                {
                    "tool": "flake8",
                    "type": "system",
                    "severity": "warning",
                    "message": f"Flake8检查失败: {e}",
                    "blocking": False,
                },
            )

        return problems

    def _map_ruff_severity(self, code: str) -> str:
        """映射ruff错误码到严重度"""
        if code.startswith("E"):
            return "error" if code in ["E999"] else "warning"
        if code.startswith("W"):
            return "warning"
        if code.startswith("F"):
            return "error"
        if code.startswith("B"):
            return "warning"
        return "info"

    def _get_ruff_fix_suggestion(self, issue: dict[str, Any]) -> str:
        """获取ruff修复建议"""
        code = issue.get("code", "")
        message = issue.get("message", "")

        suggestions = {
            "F401": "删除未使用的导入",
            "F841": "删除未使用的变量或添加下划线前缀",
            "E501": "使用black自动格式化或手动换行",
            "W291": "删除行尾空白字符",
            "W292": "在文件末尾添加换行符",
            "I001": "使用isort排序导入语句",
        }

        return suggestions.get(code, f"参考ruff文档修复: {message}")

    def _is_blocking_lint_issue(self, code: str) -> bool:
        """判断是否为阻塞性lint问题"""
        blocking_codes = [
            "F999",  # 语法错误
            "E999",  # 语法错误
            "F821",  # 未定义变量
            "F822",  # 未定义变量在__all__中
        ]
        return code in blocking_codes


def main():
    """测试函数"""
    adapter = LintAdapter()
    problems = adapter.run_ruff()

    print(f"发现 {len(problems)} 个lint问题:")
    for problem in problems[:5]:  # 只显示前5个
        print(
            f"  {problem['severity']}: {problem.get('file', 'N/A')}:{problem.get('line', 0)} - {problem['message']}",
        )


if __name__ == "__main__":
    main()
