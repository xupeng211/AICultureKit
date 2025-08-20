#!/usr/bin/env python3
"""
AI Fix Agent - 生成可审阅的修复补丁

AI不直接在仓库大改，而是针对聚合问题生成统一patch，开发者人工确认应用
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .strategies.lint_fix import LintFixStrategy
from .strategies.security_fix import SecurityFixStrategy
from .strategies.test_scaffold import TestScaffoldStrategy


class AIFixAgent:
    """AI修复代理主类"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

        # 初始化修复策略
        self.strategies = {
            'lint': LintFixStrategy(str(self.project_root)),
            'security': SecurityFixStrategy(str(self.project_root)),
            'test_scaffold': TestScaffoldStrategy(str(self.project_root)),
        }

    def generate_fixes(self, problems_file: str, output_dir: str) -> Dict[str, Any]:
        """
        生成修复补丁

        Args:
            problems_file: 问题JSON文件路径
            output_dir: 输出目录路径

        Returns:
            修复结果摘要
        """

        print(f"🤖 AI修复代理启动...")
        print(f"   输入: {problems_file}")
        print(f"   输出: {output_dir}")

        # 加载问题
        try:
            with open(problems_file, 'r', encoding='utf-8') as f:
                problems_data = json.load(f)
        except Exception as e:
            print(f"❌ 加载问题文件失败: {e}")
            return {'success': False, 'error': str(e)}

        problems = problems_data.get('problems', [])
        if not problems:
            print("ℹ️  没有发现问题，无需生成修复")
            return {'success': True, 'patches': [], 'message': '没有问题需要修复'}

        print(f"📊 分析 {len(problems)} 个问题...")

        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 按策略分类问题
        categorized_problems = self._categorize_problems(problems)

        # 生成修复
        results = {}
        patch_files = []

        for strategy_name, strategy_problems in categorized_problems.items():
            if not strategy_problems:
                continue

            print(f"🔧 处理 {strategy_name} 问题 ({len(strategy_problems)} 个)...")

            strategy = self.strategies.get(strategy_name)
            if not strategy:
                print(f"⚠️  未找到策略: {strategy_name}")
                continue

            # 生成修复
            patch_content, explanation, confidence = strategy.generate_fix(
                strategy_problems
            )

            if patch_content and confidence > 0.5:  # 只生成高置信度的补丁
                # 保存补丁文件
                patch_file = output_path / f"{strategy_name}_fix.patch"
                with open(patch_file, 'w', encoding='utf-8') as f:
                    f.write(patch_content)

                # 保存说明文件
                explanation_file = output_path / f"{strategy_name}_explanation.md"
                with open(explanation_file, 'w', encoding='utf-8') as f:
                    f.write(explanation)

                patch_files.append(
                    {
                        'strategy': strategy_name,
                        'patch_file': str(patch_file),
                        'explanation_file': str(explanation_file),
                        'confidence': confidence,
                        'problems_count': len(strategy_problems),
                    }
                )

                print(f"✅ 生成 {strategy_name} 补丁 (置信度: {confidence:.1%})")

            else:
                # 生成手工修复指南
                if hasattr(strategy, 'generate_manual_guide'):
                    guide = strategy.generate_manual_guide(strategy_problems)
                    guide_file = output_path / f"{strategy_name}_manual_guide.md"
                    with open(guide_file, 'w', encoding='utf-8') as f:
                        f.write(guide)

                    print(f"📋 生成 {strategy_name} 手工修复指南")
                else:
                    print(f"⚠️  {strategy_name} 问题置信度过低，跳过自动修复")

            results[strategy_name] = {
                'problems_count': len(strategy_problems),
                'patch_generated': patch_content != "",
                'confidence': confidence,
                'explanation': explanation,
            }

        # 生成总体变更日志
        changelog = self._generate_changelog(patch_files, problems_data)
        changelog_file = output_path / "CHANGELOG_ENTRY.md"
        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(changelog)

        # 生成应用脚本
        apply_script = self._generate_apply_script(patch_files)
        script_file = output_path / "apply_fixes.sh"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(apply_script)
        script_file.chmod(0o755)  # 设置执行权限

        print(f"📄 生成变更日志: {changelog_file}")
        print(f"🚀 生成应用脚本: {script_file}")

        summary = {
            'success': True,
            'patches': patch_files,
            'total_problems': len(problems),
            'strategies_used': list(results.keys()),
            'output_directory': str(output_path),
            'changelog_file': str(changelog_file),
            'apply_script': str(script_file),
        }

        print(f"🎉 AI修复完成: 生成了 {len(patch_files)} 个补丁文件")

        return summary

    def _categorize_problems(
        self, problems: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """按修复策略分类问题"""

        categorized = {'lint': [], 'security': [], 'test_scaffold': []}

        for problem in problems:
            # 检查每个策略是否可以处理此问题
            for strategy_name, strategy in self.strategies.items():
                if strategy.can_fix(problem):
                    categorized[strategy_name].append(problem)
                    break  # 每个问题只分配给一个策略

        return categorized

    def _generate_changelog(
        self, patch_files: List[Dict[str, Any]], problems_data: Dict[str, Any]
    ) -> str:
        """生成变更日志条目"""

        lines = []

        # 标题
        lines.append("# AI自动修复变更日志")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 摘要
        total_problems = problems_data.get('summary', {}).get('total', 0)
        blocking_problems = problems_data.get('summary', {}).get('blocking', 0)

        lines.append("## 📊 修复摘要")
        lines.append("")
        lines.append(f"- **总问题数**: {total_problems}")
        lines.append(f"- **阻塞性问题**: {blocking_problems}")
        lines.append(f"- **生成补丁**: {len(patch_files)}")
        lines.append("")

        # 安全性说明
        lines.append("## 🛡️ 安全性说明")
        lines.append("")
        lines.append("所有修复补丁均由AI生成，**请在应用前仔细审查**：")
        lines.append("")
        lines.append("1. **代码审查**: 检查修复逻辑是否正确")
        lines.append("2. **测试验证**: 应用补丁后运行完整测试套件")
        lines.append("3. **回滚准备**: 确保可以快速回滚更改")
        lines.append("4. **分步应用**: 建议逐个应用补丁，而非批量应用")
        lines.append("")

        # 详细修复说明
        if patch_files:
            lines.append("## 🔧 修复详情")
            lines.append("")

            for i, patch_info in enumerate(patch_files, 1):
                strategy = patch_info['strategy']
                confidence = patch_info['confidence']
                problems_count = patch_info['problems_count']

                lines.append(f"### {i}. {strategy.title()} 修复")
                lines.append("")
                lines.append(f"- **补丁文件**: `{Path(patch_info['patch_file']).name}`")
                lines.append(
                    f"- **说明文件**: `{Path(patch_info['explanation_file']).name}`"
                )
                lines.append(f"- **置信度**: {confidence:.1%}")
                lines.append(f"- **修复问题数**: {problems_count}")
                lines.append("")

                # 风险评估
                if confidence >= 0.8:
                    risk_level = "🟢 低风险"
                elif confidence >= 0.6:
                    risk_level = "🟡 中等风险"
                else:
                    risk_level = "🔴 高风险"

                lines.append(f"- **风险评估**: {risk_level}")
                lines.append("")

        # 应用指南
        lines.append("## 🚀 应用指南")
        lines.append("")
        lines.append("### 推荐步骤")
        lines.append("")
        lines.append("1. **备份当前状态**:")
        lines.append("   ```bash")
        lines.append("   git stash  # 保存未提交的更改")
        lines.append("   git branch backup-$(date +%Y%m%d-%H%M%S)  # 创建备份分支")
        lines.append("   ```")
        lines.append("")
        lines.append("2. **逐个应用补丁**:")
        lines.append("   ```bash")
        lines.append("   # 检查补丁内容")
        lines.append("   cat artifacts/ai_fixes/lint_fix.patch")
        lines.append("   ")
        lines.append("   # 应用补丁")
        lines.append("   git apply artifacts/ai_fixes/lint_fix.patch --index")
        lines.append("   ")
        lines.append("   # 验证更改")
        lines.append("   git diff --cached")
        lines.append("   ```")
        lines.append("")
        lines.append("3. **验证修复效果**:")
        lines.append("   ```bash")
        lines.append("   # 重新运行问题检查")
        lines.append("   python -m tools.problem_aggregator.aggregator")
        lines.append("   ")
        lines.append("   # 运行测试")
        lines.append("   pytest")
        lines.append("   ```")
        lines.append("")
        lines.append("4. **提交更改**:")
        lines.append("   ```bash")
        lines.append("   git commit -m \"fix: apply AI-generated fixes\"")
        lines.append("   ```")
        lines.append("")

        # 回滚指南
        lines.append("### 回滚指南")
        lines.append("")
        lines.append("如果修复出现问题，可以快速回滚：")
        lines.append("")
        lines.append("```bash")
        lines.append("# 回滚到应用补丁前的状态")
        lines.append("git reset --hard HEAD~1")
        lines.append("")
        lines.append("# 或者使用备份分支")
        lines.append("git checkout backup-YYYYMMDD-HHMMSS")
        lines.append("```")
        lines.append("")

        return '\n'.join(lines)

    def _generate_apply_script(self, patch_files: List[Dict[str, Any]]) -> str:
        """生成应用补丁的脚本"""

        lines = []

        # 脚本头
        lines.append("#!/bin/bash")
        lines.append("# AI修复补丁应用脚本")
        lines.append("# 自动生成，请谨慎使用")
        lines.append("")
        lines.append("set -e  # 遇到错误时退出")
        lines.append("")

        # 检查Git状态
        lines.append("echo '🔍 检查Git状态...'")
        lines.append("if ! git diff-index --quiet HEAD --; then")
        lines.append("    echo '⚠️  工作区有未提交的更改，请先提交或stash'")
        lines.append("    exit 1")
        lines.append("fi")
        lines.append("")

        # 创建备份分支
        lines.append("echo '💾 创建备份分支...'")
        lines.append("BACKUP_BRANCH=\"backup-$(date +%Y%m%d-%H%M%S)\"")
        lines.append("git branch \"$BACKUP_BRANCH\"")
        lines.append("echo \"✅ 备份分支已创建: $BACKUP_BRANCH\"")
        lines.append("")

        # 应用补丁
        if patch_files:
            lines.append("echo '🔧 开始应用补丁...'")
            lines.append("")

            for i, patch_info in enumerate(patch_files, 1):
                patch_file = Path(patch_info['patch_file']).name
                strategy = patch_info['strategy']
                confidence = patch_info['confidence']

                lines.append(
                    f"echo '📋 {i}/{len(patch_files)}: 应用 {strategy} 补丁 (置信度: {confidence:.1%})...'"
                )
                lines.append(f"if git apply --check {patch_file} 2>/dev/null; then")
                lines.append(f"    git apply {patch_file} --index")
                lines.append(f"    echo '✅ {strategy} 补丁应用成功'")
                lines.append("else")
                lines.append(f"    echo '❌ {strategy} 补丁应用失败，跳过'")
                lines.append("    echo '💡 请手动检查补丁内容并应用'")
                lines.append("fi")
                lines.append("")

        # 验证结果
        lines.append("echo '🧪 验证修复效果...'")
        lines.append("if command -v python >/dev/null 2>&1; then")
        lines.append("    echo '运行问题检查...'")
        lines.append(
            "    python -m tools.problem_aggregator.aggregator --out artifacts/post_fix_problems.json"
        )
        lines.append("    echo '📊 修复后问题报告: artifacts/post_fix_problems.json'")
        lines.append("fi")
        lines.append("")

        # 提示下一步
        lines.append("echo '🎉 补丁应用完成！'")
        lines.append("echo ''")
        lines.append("echo '下一步建议:'")
        lines.append("echo '1. 检查修改内容: git diff --cached'")
        lines.append("echo '2. 运行测试: pytest'")
        lines.append("echo '3. 提交更改: git commit -m \"fix: apply AI-generated fixes\"'")
        lines.append("echo '4. 如有问题回滚: git reset --hard HEAD~1'")
        lines.append("echo \"5. 或使用备份分支: git checkout $BACKUP_BRANCH\"")

        return '\n'.join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI Fix Agent - 生成可审阅的修复补丁')
    parser.add_argument('--in', dest='input_file', required=True, help='输入的问题JSON文件')
    parser.add_argument('--out', dest='output_dir', required=True, help='输出目录')
    parser.add_argument('--project-root', default='.', help='项目根目录')

    args = parser.parse_args()

    # 创建AI修复代理
    agent = AIFixAgent(args.project_root)

    # 生成修复
    result = agent.generate_fixes(args.input_file, args.output_dir)

    if result['success']:
        print(f"\n📋 修复摘要:")
        print(f"   生成补丁: {len(result['patches'])} 个")
        print(f"   输出目录: {result['output_directory']}")
        print(f"   变更日志: {result['changelog_file']}")
        print(f"   应用脚本: {result['apply_script']}")

        if result['patches']:
            print(f"\n🚀 应用补丁:")
            print(f"   cd {result['output_directory']}")
            print(f"   ./apply_fixes.sh")

        sys.exit(0)
    else:
        print(f"❌ 修复失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
