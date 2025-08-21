"""
Tests and coverage adapter for pytest
"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List


class TestsAdapter:
    """测试和覆盖率适配器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def collect_tests(self) -> List[Dict[str, Any]]:
        """收集测试信息"""
        problems = []

        try:
            # 使用pytest --collect-only收集测试
            cmd = ["python", "-m", "pytest", "--collect-only", "--quiet", "--tb=no"]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                problems.append(
                    {
                        "tool": "pytest",
                        "type": "test_collection",
                        "severity": "error",
                        "message": f"测试收集失败: {result.stderr[:200]}",
                        "fix_suggestion": "检查测试文件语法和导入",
                        "blocking": True,
                    }
                )
            else:
                # 解析收集到的测试数量
                output_lines = result.stdout.split("\n")
                test_count = 0
                for line in output_lines:
                    if "collected" in line and "item" in line:
                        try:
                            test_count = int(line.split()[0])
                        except (ValueError, IndexError):
                            pass

                if test_count == 0:
                    problems.append(
                        {
                            "tool": "pytest",
                            "type": "test_coverage",
                            "severity": "warning",
                            "message": "未发现任何测试用例",
                            "fix_suggestion": "添加测试文件和测试用例",
                            "blocking": False,
                        }
                    )

        except subprocess.TimeoutExpired:
            problems.append(
                {
                    "tool": "pytest",
                    "type": "system",
                    "severity": "error",
                    "message": "测试收集超时",
                    "blocking": False,
                }
            )
        except FileNotFoundError:
            problems.append(
                {
                    "tool": "pytest",
                    "type": "system",
                    "severity": "warning",
                    "message": "Pytest未安装，跳过测试检查",
                    "blocking": False,
                }
            )
        except Exception as e:
            problems.append(
                {
                    "tool": "pytest",
                    "type": "system",
                    "severity": "warning",
                    "message": f"测试收集失败: {e}",
                    "blocking": False,
                }
            )

        return problems

    def run_tests_quick(self) -> List[Dict[str, Any]]:
        """快速运行测试（仅检查是否能运行）"""
        problems = []

        try:
            # 快速测试运行，最多失败1个就停止
            cmd = ["python", "-m", "pytest", "--maxfail=1", "--tb=short", "--quiet"]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, timeout=120
            )

            if result.returncode != 0:
                # 解析测试失败信息
                stderr_lines = result.stderr.split("\n")
                stdout_lines = result.stdout.split("\n")

                failure_info = []
                for line in stdout_lines + stderr_lines:
                    if "FAILED" in line or "ERROR" in line:
                        failure_info.append(line.strip())

                problems.append(
                    {
                        "tool": "pytest",
                        "type": "test_failure",
                        "severity": "error",
                        "message": f'测试失败: {"; ".join(failure_info[:3])}',
                        "fix_suggestion": "修复失败的测试用例",
                        "blocking": True,
                    }
                )

        except subprocess.TimeoutExpired:
            problems.append(
                {
                    "tool": "pytest",
                    "type": "test_failure",
                    "severity": "error",
                    "message": "测试运行超时",
                    "fix_suggestion": "优化测试性能或增加超时时间",
                    "blocking": True,
                }
            )
        except Exception as e:
            problems.append(
                {
                    "tool": "pytest",
                    "type": "system",
                    "severity": "warning",
                    "message": f"测试运行失败: {e}",
                    "blocking": False,
                }
            )

        return problems

    def get_coverage_info(self, min_coverage: float = 80.0) -> List[Dict[str, Any]]:
        """获取测试覆盖率信息"""
        problems = []

        try:
            # 运行覆盖率测试
            cmd = [
                "python",
                "-m",
                "pytest",
                "--cov=aiculture",
                "--cov-report=xml:coverage.xml",
                "--cov-report=term-missing",
                "--quiet",
            ]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, timeout=180
            )

            # 尝试解析XML覆盖率报告
            coverage_xml = self.project_root / "coverage.xml"
            if coverage_xml.exists():
                try:
                    tree = ET.parse(coverage_xml)
                    root = tree.getroot()

                    # 获取总体覆盖率
                    coverage_elem = root.find(".//coverage")
                    if coverage_elem is not None:
                        line_rate = float(coverage_elem.get("line-rate", 0)) * 100
                        branch_rate = float(coverage_elem.get("branch-rate", 0)) * 100

                        if line_rate < min_coverage:
                            problems.append(
                                {
                                    "tool": "coverage",
                                    "type": "test_coverage",
                                    "severity": "error",
                                    "message": f"测试覆盖率不足: {line_rate:.1f}% < {min_coverage}%",
                                    "fix_suggestion": f"需要增加测试用例提升覆盖率到{min_coverage}%以上",
                                    "blocking": True,
                                    "metadata": {
                                        "current_coverage": line_rate,
                                        "required_coverage": min_coverage,
                                        "branch_coverage": branch_rate,
                                    },
                                }
                            )

                        # 检查低覆盖率文件
                        for package in root.findall(".//package"):
                            for class_elem in package.findall(".//class"):
                                filename = class_elem.get("filename", "")
                                class_line_rate = (
                                    float(class_elem.get("line-rate", 0)) * 100
                                )

                                if (
                                    class_line_rate < min_coverage * 0.7
                                ):  # 低于70%的文件
                                    problems.append(
                                        {
                                            "tool": "coverage",
                                            "type": "file_coverage",
                                            "severity": "warning",
                                            "file": filename,
                                            "message": f"文件覆盖率过低: {class_line_rate:.1f}%",
                                            "fix_suggestion": "为此文件添加更多测试用例",
                                            "blocking": False,
                                            "metadata": {
                                                "file_coverage": class_line_rate
                                            },
                                        }
                                    )

                except ET.ParseError:
                    problems.append(
                        {
                            "tool": "coverage",
                            "type": "system",
                            "severity": "warning",
                            "message": "覆盖率报告解析失败",
                            "blocking": False,
                        }
                    )
            else:
                # 尝试从stdout解析覆盖率
                coverage_line = None
                for line in result.stdout.split("\n"):
                    if "TOTAL" in line and "%" in line:
                        coverage_line = line
                        break

                if coverage_line:
                    try:
                        # 提取覆盖率百分比
                        parts = coverage_line.split()
                        for part in parts:
                            if part.endswith("%"):
                                current_coverage = float(part.rstrip("%"))
                                if current_coverage < min_coverage:
                                    problems.append(
                                        {
                                            "tool": "coverage",
                                            "type": "test_coverage",
                                            "severity": "error",
                                            "message": f"测试覆盖率不足: {current_coverage:.1f}% < {min_coverage}%",
                                            "fix_suggestion": f"需要增加测试用例提升覆盖率到{min_coverage}%以上",
                                            "blocking": True,
                                            "metadata": {
                                                "current_coverage": current_coverage,
                                                "required_coverage": min_coverage,
                                            },
                                        }
                                    )
                                break
                    except ValueError:
                        pass
                else:
                    problems.append(
                        {
                            "tool": "coverage",
                            "type": "test_coverage",
                            "severity": "warning",
                            "message": "无法获取覆盖率信息",
                            "fix_suggestion": "确保安装了pytest-cov插件",
                            "blocking": False,
                        }
                    )

        except subprocess.TimeoutExpired:
            problems.append(
                {
                    "tool": "coverage",
                    "type": "system",
                    "severity": "error",
                    "message": "覆盖率检查超时",
                    "blocking": False,
                }
            )
        except FileNotFoundError:
            problems.append(
                {
                    "tool": "coverage",
                    "type": "system",
                    "severity": "info",
                    "message": "Pytest-cov未安装，跳过覆盖率检查",
                    "blocking": False,
                }
            )
        except Exception as e:
            problems.append(
                {
                    "tool": "coverage",
                    "type": "system",
                    "severity": "warning",
                    "message": f"覆盖率检查失败: {e}",
                    "blocking": False,
                }
            )

        return problems

    def check_test_patterns(self) -> List[Dict[str, Any]]:
        """检查测试模式和约定"""
        problems = []

        try:
            # 检查是否有跳过的测试
            cmd = ["python", "-m", "pytest", "--collect-only", "-v"]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, timeout=60
            )

            if "SKIPPED" in result.stdout:
                skip_count = result.stdout.count("SKIPPED")
                problems.append(
                    {
                        "tool": "pytest",
                        "type": "test_quality",
                        "severity": "warning",
                        "message": f"发现 {skip_count} 个跳过的测试",
                        "fix_suggestion": "检查跳过的测试是否有合理原因",
                        "blocking": False,
                    }
                )

        except Exception as e:
            problems.append(
                {
                    "tool": "pytest",
                    "type": "system",
                    "severity": "info",
                    "message": f"测试模式检查失败: {e}",
                    "blocking": False,
                }
            )

        return problems


def main():
    """测试函数"""
    adapter = TestsAdapter()

    print("收集测试信息...")
    collection_problems = adapter.collect_tests()
    print(f"测试收集问题: {len(collection_problems)}")

    print("检查测试覆盖率...")
    coverage_problems = adapter.get_coverage_info(80.0)
    print(f"覆盖率问题: {len(coverage_problems)}")

    print("检查测试模式...")
    pattern_problems = adapter.check_test_patterns()
    print(f"测试模式问题: {len(pattern_problems)}")

    all_problems = collection_problems + coverage_problems + pattern_problems
    blocking_problems = [p for p in all_problems if p.get("blocking", False)]

    print(
        f"总计: {len(all_problems)} 个测试问题，其中 {len(blocking_problems)} 个阻塞性问题"
    )


if __name__ == "__main__":
    main()
