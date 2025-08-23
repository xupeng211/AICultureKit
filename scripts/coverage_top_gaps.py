#!/usr/bin/env python3
"""
覆盖率缺口分析工具
找出最值得添加测试的文件，按缺失行数排序
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


def analyze_coverage_gaps(coverage_file: Path = Path("coverage.json")) -> List[Dict]:
    """分析覆盖率缺口，返回按缺失行数排序的文件列表"""

    if not coverage_file.exists():
        print(f"❌ 覆盖率文件不存在: {coverage_file}")
        print("请先运行: pytest --cov=aiculture --cov-report=json")
        return []

    with open(coverage_file) as f:
        data = json.load(f)

    files_analysis = []
    omit_patterns = [
        "tests/",
        "__main__.py",
        "migrations/",
        "experimental/",
        "venv/",
        "build/",
        "dist/",
    ]

    for file_path, file_data in data["files"].items():
        # 跳过测试文件和其他排除文件
        if any(pattern in file_path for pattern in omit_patterns):
            continue

        summary = file_data["summary"]
        missing_lines = len(file_data["missing_lines"])
        total_lines = summary["num_statements"]
        covered_lines = summary["covered_lines"]
        coverage_percent = summary["percent_covered"]

        if total_lines > 0:  # 只分析有代码的文件
            files_analysis.append(
                {
                    "file": file_path,
                    "missing_lines": missing_lines,
                    "total_lines": total_lines,
                    "covered_lines": covered_lines,
                    "coverage_percent": coverage_percent,
                    "missing_line_ranges": _get_line_ranges(file_data["missing_lines"]),
                    "priority_score": missing_lines
                    * (1 - coverage_percent / 100),  # 缺失行数 × 覆盖率不足比例
                }
            )

    # 按优先级分数排序（缺失行数多且覆盖率低的优先）
    files_analysis.sort(key=lambda x: x["priority_score"], reverse=True)
    return files_analysis


def _get_line_ranges(missing_lines: List[int]) -> List[str]:
    """将缺失的行号转换为范围格式"""
    if not missing_lines:
        return []

    missing_lines = sorted(missing_lines)
    ranges = []
    start = missing_lines[0]
    end = start

    for line in missing_lines[1:]:
        if line == end + 1:
            end = line
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = end = line

    # 添加最后一个范围
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")

    return ranges


def print_coverage_analysis(top_n: int = 10):
    """打印覆盖率分析结果"""
    files = analyze_coverage_gaps()

    if not files:
        return

    total_files = len(files)
    print(f"\n📊 覆盖率缺口分析 (共 {total_files} 个文件)")
    print("=" * 80)

    print(f"\n🎯 前 {min(top_n, len(files))} 个最值得添加测试的文件:")
    print("-" * 80)

    for i, file_info in enumerate(files[:top_n], 1):
        file_path = file_info["file"].replace("aiculture/", "")
        missing = file_info["missing_lines"]
        total = file_info["total_lines"]
        coverage = file_info["coverage_percent"]
        ranges = file_info["missing_line_ranges"]

        print(f"\n{i:2d}. 📁 {file_path}")
        print(f"    📈 覆盖率: {coverage:.1f}% ({file_info['covered_lines']}/{total} 行)")
        print(f"    🎯 缺失: {missing} 行 (优先级分数: {file_info['priority_score']:.1f})")

        # 显示前几个缺失行范围
        if ranges:
            range_preview = ", ".join(ranges[:5])
            if len(ranges) > 5:
                range_preview += f" (+{len(ranges)-5} more)"
            print(f"    🔢 缺失行号: {range_preview}")

    # 统计信息
    total_missing = sum(f["missing_lines"] for f in files)
    total_lines = sum(f["total_lines"] for f in files)
    avg_coverage = (
        sum(f["coverage_percent"] for f in files) / len(files) if files else 0
    )

    print(f"\n📋 统计摘要:")
    print(f"    • 总行数: {total_lines}")
    print(f"    • 缺失行数: {total_missing}")
    print(f"    • 平均覆盖率: {avg_coverage:.1f}%")

    # 给出快速提升建议
    print(f"\n💡 快速提升建议:")
    print(f"    • 专注前 3-5 个文件，预计可提升 5-10% 覆盖率")
    print(f"    • 优先测试: 异常路径、边界条件、配置加载")
    print(f"    • 避免复杂集成测试，专注单元测试")


if __name__ == "__main__":
    print_coverage_analysis()
