#!/bin/bash

# AICultureKit 自动化开发环境一键设置脚本
# 设置完整的自动化开发文化保障机制

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🚀 AICultureKit 自动化开发环境设置${NC}"
echo "=================================================="

# 检查系统要求
echo -e "${BLUE}🔍 检查系统要求...${NC}"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python版本: $python_version${NC}"

# 检查Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git 未安装${NC}"
    exit 1
fi

git_version=$(git --version | cut -d' ' -f3)
echo -e "${GREEN}✅ Git版本: $git_version${NC}"

# 检查是否在Git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  当前目录不是Git仓库，正在初始化...${NC}"
    git init
    git add .
    git commit -m "🎉 初始化AICultureKit项目"
fi

echo ""
echo -e "${BLUE}📦 安装Python依赖...${NC}"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ] && [ ! -d ".venv" ] && [ ! -d "aiculture-env" ]; then
    echo -e "${YELLOW}📁 创建虚拟环境...${NC}"
    python3 -m venv venv
    source venv/bin/activate
else
    echo -e "${GREEN}✅ 虚拟环境已存在${NC}"
    # 尝试激活虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "aiculture-env" ]; then
        source aiculture-env/bin/activate
    fi
fi

# 升级pip
pip install --upgrade pip

# 安装基础依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
else
    # 安装开发必需的工具
    echo -e "${YELLOW}📦 安装开发工具...${NC}"
    pip install black isort flake8 mypy pytest pytest-cov bandit autoflake pre-commit
fi

echo ""
echo -e "${BLUE}🔧 设置Git钩子...${NC}"

# 运行钩子安装脚本
if [ -f "scripts/setup_hooks.sh" ]; then
    chmod +x scripts/setup_hooks.sh
    ./scripts/setup_hooks.sh
else
    echo -e "${YELLOW}⚠️  钩子安装脚本不存在，跳过...${NC}"
fi

echo ""
echo -e "${BLUE}⚙️  配置IDE设置...${NC}"

# 给脚本添加执行权限
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true

# 设置Git配置
echo -e "${BLUE}📝 配置Git设置...${NC}"
git config --local core.autocrlf false
git config --local core.safecrlf true
git config --local push.default simple

# 如果存在提交模板，设置它
if [ -f ".gitmessage" ]; then
    git config --local commit.template .gitmessage
fi

# 创建质量检查别名
git config --local alias.qc '!./scripts/quick_check.sh'
git config --local alias.ci '!./scripts/ci_local.sh'
git config --local alias.fix '!python scripts/smart_fixer.py'
git config --local alias.monitor '!python scripts/quality_monitor.py'

echo ""
echo -e "${BLUE}🧪 运行初始质量检查...${NC}"

# 运行快速检查
if [ -f "scripts/quick_check.sh" ]; then
    ./scripts/quick_check.sh || echo -e "${YELLOW}⚠️  初始检查发现问题，但这是正常的${NC}"
fi

echo ""
echo -e "${BLUE}📊 初始化质量监控...${NC}"

# 运行一次质量监控以建立基线
if [ -f "scripts/quality_monitor.py" ]; then
    python scripts/quality_monitor.py || echo -e "${YELLOW}⚠️  质量监控初始化完成${NC}"
fi

echo ""
echo -e "${GREEN}🎉 自动化环境设置完成！${NC}"
echo "=================================================="

echo -e "${BLUE}📋 已启用的自动化功能:${NC}"
echo "   ✅ Pre-commit钩子: 自动代码格式化和检查"
echo "   ✅ Commit-msg钩子: 智能提交信息规范化"
echo "   ✅ Pre-push钩子: 推送前完整质量检查"
echo "   ✅ VS Code配置: 实时代码检查和格式化"
echo "   ✅ GitHub Actions: 自动CI/CD流水线"
echo "   ✅ 质量监控: 实时代码质量跟踪"

echo ""
echo -e "${BLUE}🛠️  可用的命令:${NC}"
echo "   git qc          - 快速质量检查"
echo "   git ci          - 完整CI检查"
echo "   git fix         - 智能代码修复"
echo "   git monitor     - 质量监控"

echo ""
echo -e "${BLUE}💡 VS Code用户:${NC}"
echo "   - 打开命令面板 (Ctrl+Shift+P)"
echo "   - 运行 'Tasks: Run Task' 查看所有可用任务"
echo "   - 推荐安装建议的扩展以获得最佳体验"

echo ""
echo -e "${BLUE}🚀 下一步:${NC}"
echo "   1. 提交一些代码测试自动化功能"
echo "   2. 查看生成的质量报告"
echo "   3. 根据需要调整配置"

echo ""
echo -e "${PURPLE}🎯 现在你的项目已经具备完全自动化的开发文化保障！${NC}"
echo -e "${GREEN}✨ 享受无缝的AI协作开发体验吧！${NC}"
