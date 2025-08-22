#!/usr/bin/env python3
"""
AI修复代理 - M2起步版
从已暂存文件生成lint和安全修复补丁
"""

import argparse
import sys
from pathlib import Path
from typing import Any

from .strategies.lint_autofix import create_lint_patches
from .strategies.security_codemods import create_security_patches
from .utils import get_staged_python_files


class AIFixAgent:
    """AI修复代理主类"""

    def __init__(self):
        pass

    def run_staged_files_mode(self, output_dir: str) -> dict[str, Any]:
        """运行已暂存文件模式（M2起步版）"""

        print("🚀 AI修复代理启动 (M2起步版)")
        print("📁 处理已暂存的Python文件...")

        # 获取已暂存的Python文件
        staged_files = get_staged_python_files()

        if not staged_files:
            print("⚠️ 没有发现已暂存的Python文件")
            return {"success": False, "reason": "no_staged_files"}

        print(f"📊 发现 {len(staged_files)} 个已暂存的Python文件:")
        for file_path in staged_files:
            print(f"  - {file_path}")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {
            "success": True,
            "staged_files": staged_files,
            "patches_generated": [],
            "total_patches": 0,
            "changelog_entries": [],
        }

        # 1. 生成lint修复补丁
        print("\n🔧 生成lint修复补丁...")
        lint_result = create_lint_patches(staged_files)

        if lint_result["patches"]:
            patch_files = self._save_patches(lint_result["patches"], output_path, "lint")
            results["patches_generated"].extend(patch_files)
            results["total_patches"] += len(patch_files)
            results["changelog_entries"].append(lint_result["changelog"])
            print(f"✅ 生成 {len(patch_files)} 个lint补丁")
        else:
            print("ℹ️ 无需lint修复")

        # 2. 生成安全修复补丁
        print("\n🔒 生成安全修复补丁...")
        security_result = create_security_patches(staged_files)

        if security_result["patches"]:
            patch_files = self._save_patches(security_result["patches"], output_path, "security")
            results["patches_generated"].extend(patch_files)
            results["total_patches"] += len(patch_files)
            results["changelog_entries"].append(security_result["changelog"])
            print(f"✅ 生成 {len(patch_files)} 个安全补丁")
        else:
            print("ℹ️ 无需安全修复")

        # 3. 生成变更日志
        if results["changelog_entries"]:
            changelog_path = output_path / "CHANGELOG_ENTRY.md"
            self._create_changelog(results["changelog_entries"], changelog_path)
            print(f"📋 变更日志已保存: {changelog_path}")

        # 4. 生成应用脚本
        if results["patches_generated"]:
            apply_script_path = output_path / "apply_fixes.sh"
            self._create_apply_script(results["patches_generated"], apply_script_path)
            print(f"🔧 应用脚本已保存: {apply_script_path}")

        return results

    def run(self, output_dir: str = "artifacts/ai_fixes") -> bool:
        """运行AI修复代理"""

        # M2起步版：处理已暂存文件
        result = self.run_staged_files_mode(output_dir)
        return result["success"]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI修复代理 - M2起步版")
    parser.add_argument("--out", dest="output_dir", default="artifacts/ai_fixes", help="输出目录")

    args = parser.parse_args()

    agent = AIFixAgent()
    success = agent.run(args.output_dir)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
