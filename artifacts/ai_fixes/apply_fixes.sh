#!/bin/bash
set -euo pipefail

echo '🚀 应用AI修复补丁...'
echo '========================='

# 备份当前状态
BACKUP_STASH=$(git stash create || echo '')
if [ -n "$BACKUP_STASH" ]; then
    echo "📦 备份创建: $BACKUP_STASH"
fi

# 应用补丁
APPLIED_COUNT=0
FAILED_COUNT=0

echo '📄 应用补丁: lint_001.patch'
if git apply --index 'lint_001.patch'; then
    echo '✅ 补丁应用成功'
    APPLIED_COUNT=$((APPLIED_COUNT + 1))
else
    echo '❌ 补丁应用失败: lint_001.patch'
    FAILED_COUNT=$((FAILED_COUNT + 1))
fi
echo

echo '📄 应用补丁: lint_002.patch'
if git apply --index 'lint_002.patch'; then
    echo '✅ 补丁应用成功'
    APPLIED_COUNT=$((APPLIED_COUNT + 1))
else
    echo '❌ 补丁应用失败: lint_002.patch'
    FAILED_COUNT=$((FAILED_COUNT + 1))
fi
echo

echo '📄 应用补丁: lint_003.patch'
if git apply --index 'lint_003.patch'; then
    echo '✅ 补丁应用成功'
    APPLIED_COUNT=$((APPLIED_COUNT + 1))
else
    echo '❌ 补丁应用失败: lint_003.patch'
    FAILED_COUNT=$((FAILED_COUNT + 1))
fi
echo

echo '📄 应用补丁: lint_004.patch'
if git apply --index 'lint_004.patch'; then
    echo '✅ 补丁应用成功'
    APPLIED_COUNT=$((APPLIED_COUNT + 1))
else
    echo '❌ 补丁应用失败: lint_004.patch'
    FAILED_COUNT=$((FAILED_COUNT + 1))
fi
echo

echo '========================='
echo "📊 应用结果: $APPLIED_COUNT 成功, $FAILED_COUNT 失败"

if [ $FAILED_COUNT -gt 0 ]; then
    echo '⚠️ 部分补丁应用失败，请手工检查'
    exit 1
else
    echo '🎉 所有补丁应用成功！'
    echo '💡 建议运行: pre-commit run --all-files || true'
    exit 0
fi
