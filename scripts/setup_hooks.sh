#!/bin/bash

# AICultureKit Git钩子自动安装脚本
# 一键安装所有自动化质量保障钩子

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 AICultureKit 自动化钩子安装程序${NC}"
echo "========================================"

# 检查是否在Git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ 当前目录不是Git仓库${NC}"
    exit 1
fi

# 创建钩子目录
hooks_dir=".git/hooks"
custom_hooks_dir=".githooks"

echo -e "${BLUE}📁 设置Git钩子目录...${NC}"

# 设置Git钩子路径
git config core.hooksPath "$custom_hooks_dir"

# 给钩子文件添加执行权限
echo -e "${BLUE}🔑 设置钩子执行权限...${NC}"
chmod +x "$custom_hooks_dir"/*

# 安装pre-commit
echo -e "${BLUE}📦 安装pre-commit...${NC}"
if ! command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}⚠️  pre-commit未安装，正在安装...${NC}"
    pip install pre-commit
fi

# 安装pre-commit钩子
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit install --hook-type pre-push

# 安装额外的依赖
echo -e "${BLUE}📦 安装代码质量工具...${NC}"
pip install autoflake

# 设置Git提交模板
echo -e "${BLUE}📝 设置Git提交模板...${NC}"
git config commit.template .gitmessage

# 设置Git配置
echo -e "${BLUE}⚙️  配置Git设置...${NC}"
git config core.autocrlf false
git config core.safecrlf true
git config push.default simple

# 创建质量检查别名
echo -e "${BLUE}🔗 创建Git别名...${NC}"
git config alias.quality-check '!./scripts/quick_check.sh'
git config alias.full-check '!./scripts/ci_local.sh'
git config alias.auto-fix '!black . && isort . && autoflake --in-place --remove-all-unused-imports --recursive .'

# 测试钩子
echo -e "${BLUE}🧪 测试钩子安装...${NC}"
if pre-commit run --all-files > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Pre-commit钩子测试通过${NC}"
else
    echo -e "${YELLOW}⚠️  Pre-commit钩子测试有警告，但已安装${NC}"
fi

echo ""
echo -e "${GREEN}🎉 自动化钩子安装完成！${NC}"
echo ""
echo -e "${BLUE}📋 已安装的功能:${NC}"
echo "   ✅ Pre-commit: 自动代码格式化和基础检查"
echo "   ✅ Commit-msg: 智能提交信息规范化"
echo "   ✅ Pre-push: 推送前完整质量检查"
echo "   ✅ Git别名: quality-check, full-check, auto-fix"
echo ""
echo -e "${BLUE}💡 使用方法:${NC}"
echo "   - 正常提交代码，钩子会自动运行"
echo "   - 运行 'git quality-check' 进行快速检查"
echo "   - 运行 'git full-check' 进行完整检查"
echo "   - 运行 'git auto-fix' 自动修复代码问题"
echo ""
echo -e "${YELLOW}🔄 下次提交时，所有质量检查将自动运行！${NC}"
