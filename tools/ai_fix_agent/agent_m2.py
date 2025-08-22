#!/usr/bin/env python3
"""
AI修复代理 - M2起步版
从已暂存文件生成lint和安全修复补丁
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .strategies.lint_autofix import create_lint_patches
from .strategies.security_codemods import create_security_patches
from .utils import get_staged_python_files, split_large_patch


class AIFixAgentM2:
    """AI修复代理M2起步版"""

    def __init__(self):
        pass

    def run_staged_files_mode(self, output_dir: str) -> Dict[str, Any]:
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

    def _save_patches(
        self, patches: List[Dict[str, Any]], output_path: Path, prefix: str
    ) -> List[str]:
        """保存补丁文件"""

        patch_files = []

        for i, patch in enumerate(patches):
            # 分割大补丁
            patch_parts = split_large_patch(patch["patch_content"], max_lines=200)

            for j, patch_content in enumerate(patch_parts):
                if len(patch_parts) > 1:
                    filename = f"{prefix}_{i+1:03d}_{j+1:02d}.patch"
                else:
                    filename = f"{prefix}_{i+1:03d}.patch"

                patch_file = output_path / filename
                patch_file.write_text(patch_content, encoding="utf-8")
                patch_files.append(str(patch_file))

        return patch_files

    def _create_changelog(self, changelog_entries: List[str], changelog_path: Path) -> None:
        """创建变更日志"""

        lines = [
            "# AI修复代理变更日志 (M2起步版)",
            "",
            f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "**代理版本:** M2起步版",
            "",
            "---",
            "",
        ]

        for entry in changelog_entries:
            lines.append(entry)
            lines.append("")

        lines.extend(
            [
                "---",
                "",
                "## 应用指南",
                "",
                "1. **审查补丁内容:**",
                "   ```bash",
                "   ls artifacts/ai_fixes/*.patch",
                "   cat artifacts/ai_fixes/lint_*.patch",
                "   cat artifacts/ai_fixes/security_*.patch",
                "   ```",
                "",
                "2. **应用补丁:**",
                "   ```bash",
                "   cd artifacts/ai_fixes",
                "   chmod +x apply_fixes.sh",
                "   ./apply_fixes.sh",
                "   ```",
                "",
                "3. **验证修复效果:**",
                "   ```bash",
                "   pre-commit run --all-files || true",
                "   git diff --staged",
                "   ```",
                "",
                "4. **回滚（如需要）:**",
                "   ```bash",
                "   git reset --hard HEAD",
                "   ```",
            ]
        )

        changelog_path.write_text("\n".join(lines), encoding="utf-8")

    def _create_apply_script(self, patch_files: List[str], script_path: Path) -> None:
        """创建应用脚本"""

        lines = [
            "#!/bin/bash",
            "set -euo pipefail",
            "",
            "echo '🚀 应用AI修复补丁...'",
            "echo '========================='",
            "",
            "# 备份当前状态",
            "BACKUP_STASH=$(git stash create || echo '')",
            'if [ -n "$BACKUP_STASH" ]; then',
            '    echo "📦 备份创建: $BACKUP_STASH"',
            "fi",
            "",
            "# 应用补丁",
            "APPLIED_COUNT=0",
            "FAILED_COUNT=0",
            "",
        ]

        for patch_file in patch_files:
            patch_name = Path(patch_file).name
            lines.extend(
                [
                    f"echo '📄 应用补丁: {patch_name}'",
                    f"if git apply --index '{patch_name}'; then",
                    "    echo '✅ 补丁应用成功'",
                    "    APPLIED_COUNT=$((APPLIED_COUNT + 1))",
                    "else",
                    f"    echo '❌ 补丁应用失败: {patch_name}'",
                    "    FAILED_COUNT=$((FAILED_COUNT + 1))",
                    "fi",
                    "echo",
                    "",
                ]
            )

        lines.extend(
            [
                "echo '========================='",
                'echo "📊 应用结果: $APPLIED_COUNT 成功, $FAILED_COUNT 失败"',
                "",
                "if [ $FAILED_COUNT -gt 0 ]; then",
                "    echo '⚠️ 部分补丁应用失败，请手工检查'",
                "    exit 1",
                "else",
                "    echo '🎉 所有补丁应用成功！'",
                "    echo '💡 建议运行: pre-commit run --all-files || true'",
                "    exit 0",
                "fi",
            ]
        )

        script_path.write_text("\n".join(lines), encoding="utf-8")
        script_path.chmod(0o755)

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

    agent = AIFixAgentM2()
    success = agent.run(args.output_dir)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
