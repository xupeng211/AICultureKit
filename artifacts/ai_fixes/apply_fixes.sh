#!/bin/bash
# AI修复补丁应用脚本
# 自动生成，请谨慎使用

set -e  # 遇到错误时退出

echo '🔍 检查Git状态...'
if ! git diff-index --quiet HEAD --; then
    echo '⚠️  工作区有未提交的更改，请先提交或stash'
    exit 1
fi

echo '💾 创建备份分支...'
BACKUP_BRANCH="backup-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP_BRANCH"
echo "✅ 备份分支已创建: $BACKUP_BRANCH"

echo '🧪 验证修复效果...'
if command -v python >/dev/null 2>&1; then
    echo '运行问题检查...'
    python -m tools.problem_aggregator.aggregator --out artifacts/post_fix_problems.json
    echo '📊 修复后问题报告: artifacts/post_fix_problems.json'
fi

echo '🎉 补丁应用完成！'
echo ''
echo '下一步建议:'
echo '1. 检查修改内容: git diff --cached'
echo '2. 运行测试: pytest'
echo '3. 提交更改: git commit -m "fix: apply AI-generated fixes"'
echo '4. 如有问题回滚: git reset --hard HEAD~1'
echo "5. 或使用备份分支: git checkout $BACKUP_BRANCH"
