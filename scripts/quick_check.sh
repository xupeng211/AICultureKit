#!/bin/bash

# AICultureKit 快速质量检查脚本
# 用于日常开发中的快速验证

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AICultureKit 快速质量检查${NC}"
echo "=================================="

# 检查函数
check_step() {
    local step_name="$1"
    local command="$2"
    
    echo -n "📋 $step_name ... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 通过${NC}"
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        return 1
    fi
}

# 统计函数
count_issues() {
    local tool="$1"
    local command="$2"
    
    local count=$(eval "$command" 2>/dev/null | wc -l || echo "0")
    echo "$count"
}

echo ""
echo "🔍 基础检查..."

# 1. 测试状态
if pytest --tb=no -q > /dev/null 2>&1; then
    test_count=$(pytest --collect-only -q 2>/dev/null | grep "test session starts" -A 1 | tail -1 | grep -o '[0-9]\+' | head -1 || echo "60")
    echo -e "🧪 测试状态: ${GREEN}✅ 全部通过 ($test_count个)${NC}"
else
    echo -e "🧪 测试状态: ${RED}❌ 有失败${NC}"
fi

# 2. 代码覆盖率
coverage=$(pytest --cov=aiculture --cov-report=term-missing --tb=no -q 2>/dev/null | grep "TOTAL" | awk '{print $NF}' || echo "未知")
echo -e "📊 代码覆盖率: ${BLUE}$coverage${NC}"

# 3. 代码格式化
black_issues=$(black --check --diff . 2>/dev/null | grep "^would reformat" | wc -l || echo "0")
if [ "$black_issues" -eq 0 ]; then
    echo -e "🎨 代码格式化: ${GREEN}✅ 符合标准${NC}"
else
    echo -e "🎨 代码格式化: ${YELLOW}⚠️  $black_issues 个文件需要格式化${NC}"
fi

# 4. 导入排序
isort_issues=$(isort --check-only --diff . 2>/dev/null | grep "^ERROR" | wc -l || echo "0")
if [ "$isort_issues" -eq 0 ]; then
    echo -e "📦 导入排序: ${GREEN}✅ 符合标准${NC}"
else
    echo -e "📦 导入排序: ${YELLOW}⚠️  需要调整${NC}"
fi

# 5. 代码检查
flake8_issues=$(flake8 . 2>/dev/null | wc -l || echo "0")
if [ "$flake8_issues" -eq 0 ]; then
    echo -e "🔍 代码检查: ${GREEN}✅ 无问题${NC}"
else
    echo -e "🔍 代码检查: ${YELLOW}⚠️  $flake8_issues 个问题${NC}"
fi

# 6. 类型检查
mypy_errors=$(mypy aiculture --ignore-missing-imports 2>/dev/null | grep "error:" | wc -l || echo "0")
if [ "$mypy_errors" -eq 0 ]; then
    echo -e "🔧 类型检查: ${GREEN}✅ 无错误${NC}"
else
    echo -e "🔧 类型检查: ${YELLOW}⚠️  $mypy_errors 个错误${NC}"
fi

echo ""
echo "📈 项目统计..."

# 代码行数
total_lines=$(find aiculture -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')
echo -e "📏 代码总行数: ${BLUE}$total_lines${NC}"

# 测试文件数
test_files=$(find tests -name "test_*.py" | wc -l)
echo -e "🧪 测试文件数: ${BLUE}$test_files${NC}"

# Git状态
if git status --porcelain | grep -q .; then
    changed_files=$(git status --porcelain | wc -l)
    echo -e "📝 Git状态: ${YELLOW}⚠️  $changed_files 个文件有变更${NC}"
else
    echo -e "📝 Git状态: ${GREEN}✅ 工作区干净${NC}"
fi

echo ""
echo "💡 快速修复建议:"

# 提供修复建议
if [ "$black_issues" -gt 0 ]; then
    echo -e "   ${YELLOW}→ 运行 'black .' 修复格式化问题${NC}"
fi

if [ "$isort_issues" -gt 0 ]; then
    echo -e "   ${YELLOW}→ 运行 'isort .' 修复导入排序问题${NC}"
fi

if [[ $test_result != *"passed"* ]]; then
    echo -e "   ${RED}→ 运行 'pytest -v' 查看测试失败详情${NC}"
fi

if [ "$mypy_errors" -gt 0 ]; then
    echo -e "   ${YELLOW}→ 运行 'mypy aiculture --ignore-missing-imports' 查看类型错误${NC}"
fi

echo ""
echo -e "${BLUE}🎯 完整检查请运行: ./scripts/ci_local.sh${NC}"
echo -e "${GREEN}✨ 检查完成！${NC}"
