"""
Lint问题修复策略
"""

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class LintFixStrategy:
    """Lint问题修复策略"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def can_fix(self, problem: Dict[str, Any]) -> bool:
        """判断是否可以修复此问题"""
        if problem.get("tool") != "ruff":
            return False

        code = problem.get("code", "")

        # 可以自动修复的错误码
        fixable_codes = [
            "F401",  # 未使用的导入
            "F841",  # 未使用的变量
            "W291",  # 行尾空白
            "W292",  # 文件末尾缺少换行
            "I001",  # 导入排序
            "E501",  # 行过长（通过格式化）
            "E302",  # 函数间缺少空行
            "E303",  # 过多空行
            "E231",  # 逗号后缺少空格
            "E225",  # 操作符周围缺少空格
        ]

        return code in fixable_codes

    def generate_fix(self, problems: List[Dict[str, Any]]) -> Tuple[str, str, float]:
        """
        生成修复补丁

        Returns:
            (patch_content, explanation, confidence)
        """

        # 按文件分组问题
        problems_by_file = {}
        for problem in problems:
            if not self.can_fix(problem):
                continue

            file_path = problem.get("file", "")
            if not file_path:
                continue

            if file_path not in problems_by_file:
                problems_by_file[file_path] = []
            problems_by_file[file_path].append(problem)

        if not problems_by_file:
            return "", "没有可修复的lint问题", 0.0

        # 生成修复
        patch_parts = []
        explanations = []
        total_confidence = 0.0
        fix_count = 0

        for file_path, file_problems in problems_by_file.items():
            file_patch, file_explanation, file_confidence = self._fix_file_problems(
                file_path, file_problems
            )

            if file_patch:
                patch_parts.append(file_patch)
                explanations.append(f"**{file_path}**: {file_explanation}")
                total_confidence += file_confidence
                fix_count += 1

        if not patch_parts:
            return "", "无法生成有效的修复补丁", 0.0

        # 合并补丁
        patch_content = "\n".join(patch_parts)
        explanation = "## Lint问题自动修复\n\n" + "\n".join(explanations)
        avg_confidence = total_confidence / fix_count if fix_count > 0 else 0.0

        return patch_content, explanation, avg_confidence

    def _fix_file_problems(
        self, file_path: str, problems: List[Dict[str, Any]]
    ) -> Tuple[str, str, float]:
        """修复单个文件的问题"""

        full_path = self.project_root / file_path
        if not full_path.exists():
            return "", f"文件不存在: {file_path}", 0.0

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            return "", f"读取文件失败: {e}", 0.0

        # 应用修复
        fixed_content = original_content
        applied_fixes = []

        # 按行号排序，从后往前修复避免行号偏移
        sorted_problems = sorted(problems, key=lambda p: p.get("line", 0), reverse=True)

        for problem in sorted_problems:
            code = problem.get("code", "")
            line_num = problem.get("line", 0)

            if line_num <= 0:
                continue

            fix_result = self._apply_single_fix(fixed_content, problem)
            if fix_result:
                fixed_content, fix_description = fix_result
                applied_fixes.append(f"{code}: {fix_description}")

        if fixed_content == original_content:
            return "", "没有应用任何修复", 0.0

        # 生成patch
        patch_content = self._generate_patch(file_path, original_content, fixed_content)
        explanation = f"修复了 {len(applied_fixes)} 个问题: {', '.join(applied_fixes)}"
        confidence = min(0.9, 0.7 + 0.1 * len(applied_fixes))  # 基于修复数量的置信度

        return patch_content, explanation, confidence

    def _apply_single_fix(
        self, content: str, problem: Dict[str, Any]
    ) -> Optional[Tuple[str, str]]:
        """应用单个修复"""

        code = problem.get("code", "")
        line_num = problem.get("line", 0)

        lines = content.split("\n")
        if line_num <= 0 or line_num > len(lines):
            return None

        line_idx = line_num - 1
        original_line = lines[line_idx]

        # 根据错误码应用修复
        if code == "F401":  # 未使用的导入
            # 删除整行导入
            if "import " in original_line:
                lines.pop(line_idx)
                return "\n".join(lines), "删除未使用的导入"

        elif code == "F841":  # 未使用的变量
            # 在变量名前加下划线
            match = re.search(r"(\w+)\s*=", original_line)
            if match:
                var_name = match.group(1)
                if not var_name.startswith("_"):
                    new_line = original_line.replace(
                        f"{var_name} =", f"_{var_name} =", 1
                    )
                    lines[line_idx] = new_line
                    return (
                        "\n".join(lines),
                        f"变量名加下划线: {var_name} -> _{var_name}",
                    )

        elif code == "W291":  # 行尾空白
            new_line = original_line.rstrip()
            lines[line_idx] = new_line
            return "\n".join(lines), "删除行尾空白"

        elif code == "W292":  # 文件末尾缺少换行
            if not content.endswith("\n"):
                return content + "\n", "添加文件末尾换行"

        elif code == "E302":  # 函数间缺少空行
            if line_idx > 0 and ("def " in original_line or "class " in original_line):
                lines.insert(line_idx, "")
                return "\n".join(lines), "添加函数前空行"

        elif code == "E303":  # 过多空行
            # 删除多余的空行
            if original_line.strip() == "" and line_idx > 0:
                # 检查前面是否有连续空行
                prev_empty_count = 0
                for i in range(line_idx - 1, -1, -1):
                    if lines[i].strip() == "":
                        prev_empty_count += 1
                    else:
                        break

                if prev_empty_count >= 2:  # 如果前面已有2个或更多空行
                    lines.pop(line_idx)
                    return "\n".join(lines), "删除多余空行"

        elif code == "E231":  # 逗号后缺少空格
            new_line = re.sub(r",(\S)", r", \1", original_line)
            if new_line != original_line:
                lines[line_idx] = new_line
                return "\n".join(lines), "逗号后添加空格"

        elif code == "E225":  # 操作符周围缺少空格
            # 简单的操作符空格修复
            new_line = original_line
            for op in ["=", "+", "-", "*", "/", "==", "!=", "<=", ">=", "<", ">"]:
                new_line = re.sub(
                    f"(\\w){re.escape(op)}(\\w)", f"\\1 {op} \\2", new_line
                )

            if new_line != original_line:
                lines[line_idx] = new_line
                return "\n".join(lines), "操作符周围添加空格"

        return None

    def _generate_patch(self, file_path: str, original: str, fixed: str) -> str:
        """生成Git patch格式"""

        # 使用git diff生成标准patch
        try:
            # 创建临时文件
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".orig", delete=False
            ) as orig_file:
                orig_file.write(original)
                orig_file_path = orig_file.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".fixed", delete=False
            ) as fixed_file:
                fixed_file.write(fixed)
                fixed_file_path = fixed_file.name

            # 生成diff
            result = subprocess.run(
                [
                    "diff",
                    "-u",
                    "--label",
                    f"a/{file_path}",
                    "--label",
                    f"b/{file_path}",
                    orig_file_path,
                    fixed_file_path,
                ],
                capture_output=True,
                text=True,
            )

            # 清理临时文件
            os.unlink(orig_file_path)
            os.unlink(fixed_file_path)

            if result.stdout:
                return result.stdout

        except Exception:
            pass

        # 回退到简单的diff格式
        return self._simple_diff(file_path, original, fixed)

    def _simple_diff(self, file_path: str, original: str, fixed: str) -> str:
        """生成简单的diff格式"""

        orig_lines = original.split("\n")
        fixed_lines = fixed.split("\n")

        patch_lines = [
            f"--- a/{file_path}",
            f"+++ b/{file_path}",
            f"@@ -1,{len(orig_lines)} +1,{len(fixed_lines)} @@",
        ]

        # 简单的逐行比较
        max_lines = max(len(orig_lines), len(fixed_lines))

        for i in range(max_lines):
            orig_line = orig_lines[i] if i < len(orig_lines) else None
            fixed_line = fixed_lines[i] if i < len(fixed_lines) else None

            if orig_line is None:
                patch_lines.append(f"+{fixed_line}")
            elif fixed_line is None:
                patch_lines.append(f"-{orig_line}")
            elif orig_line != fixed_line:
                patch_lines.append(f"-{orig_line}")
                patch_lines.append(f"+{fixed_line}")
            else:
                patch_lines.append(f" {orig_line}")

        return "\n".join(patch_lines)


def main():
    """测试函数"""
    strategy = LintFixStrategy()

    # 测试问题
    test_problems = [
        {
            "tool": "ruff",
            "code": "F401",
            "file": "test.py",
            "line": 1,
            "message": "unused import",
        }
    ]

    patch, explanation, confidence = strategy.generate_fix(test_problems)
    print(f"Patch:\n{patch}")
    print(f"Explanation: {explanation}")
    print(f"Confidence: {confidence}")


if __name__ == "__main__":
    main()
