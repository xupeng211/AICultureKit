"""
Lint自动修复策略
处理ruff/black/isort等格式化问题
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List

from ..utils import create_patch, get_file_content, run_command


class LintAutoFixStrategy:
    """Lint自动修复策略"""

    def __init__(self):
        self.name = "lint_autofix"
        self.description = "自动修复ruff/black/isort格式化问题"

    def can_fix(self, file_path: str, content: str) -> bool:
        """判断是否可以修复该文件"""
        return file_path.endswith(".py") and content.strip()

    def fix_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """修复单个文件的lint问题"""

        result = {
            "success": False,
            "original_content": content,
            "fixed_content": content,
            "changes": [],
            "errors": [],
        }

        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as temp_file:
                temp_file.write(content)
                temp_file.flush()
                temp_path = temp_file.name

            try:
                # 1. 运行isort
                isort_result = self._run_isort(temp_path)
                if isort_result["success"]:
                    result["changes"].append("isort: 导入排序")
                else:
                    result["errors"].append(f"isort failed: {isort_result['stderr']}")

                # 2. 运行black
                black_result = self._run_black(temp_path)
                if black_result["success"]:
                    result["changes"].append("black: 代码格式化")
                else:
                    result["errors"].append(f"black failed: {black_result['stderr']}")

                # 3. 运行ruff --fix
                ruff_result = self._run_ruff_fix(temp_path)
                if ruff_result["success"]:
                    result["changes"].append("ruff: 自动修复")
                else:
                    result["errors"].append(f"ruff failed: {ruff_result['stderr']}")

                # 读取修复后的内容
                fixed_content = get_file_content(temp_path)
                if fixed_content and fixed_content != content:
                    result["fixed_content"] = fixed_content
                    result["success"] = True
                elif not result["errors"]:
                    # 没有错误但也没有变化，说明文件已经是正确的
                    result["success"] = True
                    result["changes"].append("无需修复")

            finally:
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            result["errors"].append(f"处理文件时出错: {str(e)}")

        return result

    def _run_isort(self, file_path: str) -> Dict[str, Any]:
        """运行isort"""
        return run_command(["isort", file_path])

    def _run_black(self, file_path: str) -> Dict[str, Any]:
        """运行black"""
        return run_command(["black", file_path])

    def _run_ruff_fix(self, file_path: str) -> Dict[str, Any]:
        """运行ruff --fix"""
        return run_command(["ruff", "check", "--fix", file_path])

    def generate_patches(self, files: List[str]) -> List[Dict[str, Any]]:
        """为文件列表生成lint修复补丁"""

        patches = []
        total_changes = 0

        for file_path in files:
            content = get_file_content(file_path)
            if not self.can_fix(file_path, content):
                continue

            fix_result = self.fix_file(file_path, content)

            if (
                fix_result["success"]
                and fix_result["fixed_content"] != fix_result["original_content"]
            ):
                patch_content = create_patch(
                    fix_result["original_content"],
                    fix_result["fixed_content"],
                    file_path,
                )

                if patch_content:
                    patches.append(
                        {
                            "file_path": file_path,
                            "patch_content": patch_content,
                            "changes": fix_result["changes"],
                            "errors": fix_result["errors"],
                        }
                    )
                    total_changes += 1

        return patches

    def create_changelog_entry(self, patches: List[Dict[str, Any]]) -> str:
        """创建变更日志条目"""

        if not patches:
            return "## Lint自动修复\n\n无需修复的文件。\n"

        lines = ["## Lint自动修复", ""]
        lines.append(f"修复了 {len(patches)} 个文件的格式化问题：")
        lines.append("")

        for patch in patches:
            lines.append(f"### {patch['file_path']}")
            lines.append("")

            if patch["changes"]:
                lines.append("**修复内容：**")
                for change in patch["changes"]:
                    lines.append(f"- {change}")
                lines.append("")

            if patch["errors"]:
                lines.append("**警告：**")
                for error in patch["errors"]:
                    lines.append(f"- {error}")
                lines.append("")

        lines.append("**风险评估：** 低风险 - 仅格式化修改，不影响业务逻辑")
        lines.append("")
        lines.append("**应用方法：**")
        lines.append("```bash")
        lines.append("git apply artifacts/ai_fixes/lint_*.patch --index")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)


def create_lint_patches(files: List[str]) -> Dict[str, Any]:
    """创建lint修复补丁的便捷函数"""

    strategy = LintAutoFixStrategy()
    patches = strategy.generate_patches(files)

    return {
        "strategy": strategy.name,
        "patches": patches,
        "changelog": strategy.create_changelog_entry(patches),
        "total_files": len(patches),
    }
