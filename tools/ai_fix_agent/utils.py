"""AI修复代理工具函数"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any


def get_staged_python_files() -> list[str]:
    """获取已暂存的Python文件列表"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "--diff-filter=ACMR"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [
            f for f in result.stdout.strip().split("\n") if f.endswith(".py") and f
        ]
        return files
    except subprocess.CalledProcessError:
        return []


def get_file_content(file_path: str) -> str:
    """读取文件内容"""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, UnicodeDecodeError):
        return ""


def write_file_content(file_path: str, content: str) -> bool:
    """写入文件内容"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False


def run_command(cmd: list[str], cwd: str | None = None) -> dict[str, Any]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=60,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timeout",
            "returncode": -1,
        }
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def create_patch(original_content: str, fixed_content: str, file_path: str) -> str:
    """创建patch文件内容"""
    if original_content == fixed_content:
        return ""

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".orig",
        delete=False,
    ) as orig_file:
        orig_file.write(original_content)
        orig_file.flush()

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".fixed",
            delete=False,
        ) as fixed_file:
            fixed_file.write(fixed_content)
            fixed_file.flush()

            try:
                result = subprocess.run(
                    ["diff", "-u", orig_file.name, fixed_file.name],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                if result.stdout:
                    # 替换临时文件名为实际文件名
                    patch_content = result.stdout
                    patch_content = patch_content.replace(
                        orig_file.name,
                        f"a/{file_path}",
                    )
                    patch_content = patch_content.replace(
                        fixed_file.name,
                        f"b/{file_path}",
                    )
                    return patch_content

            finally:
                Path(orig_file.name).unlink(missing_ok=True)
                Path(fixed_file.name).unlink(missing_ok=True)

    return ""


def backup_working_directory() -> str:
    """备份当前工作目录状态"""
    try:
        result = subprocess.run(
            ["git", "stash", "create"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def restore_working_directory(stash_id: str = None) -> bool:
    """恢复工作目录状态"""
    try:
        if stash_id:
            subprocess.run(["git", "stash", "apply", stash_id], check=True)
        else:
            subprocess.run(["git", "reset", "--hard", "HEAD"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def count_patch_lines(patch_content: str) -> int:
    """统计patch的行数"""
    if not patch_content:
        return 0
    return len(
        [
            line
            for line in patch_content.split("\n")
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
        ],
    )


def split_large_patch(patch_content: str, max_lines: int = 200) -> list[str]:
    """将大patch分割为小patch"""
    if count_patch_lines(patch_content) <= max_lines:
        return [patch_content] if patch_content else []

    # 简单实现：按文件分割
    patches = []
    current_patch = []
    current_lines = 0

    for line in patch_content.split("\n"):
        if line.startswith("diff --git"):
            if current_patch and current_lines > 0:
                patches.append("\n".join(current_patch))
                current_patch = []
                current_lines = 0

        current_patch.append(line)
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            current_lines += 1

    if current_patch:
        patches.append("\n".join(current_patch))

    return patches
