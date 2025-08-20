#!/bin/bash
# 🔧 AICultureKit 环境设置脚本
# 使用方法: bash setup_environment.sh

set -e  # 遇到错误时退出

echo "🎯 AICultureKit 开发环境自动设置脚本"
echo "================================================"

# 🔍 检查Python版本
echo "📍 检查Python环境..."
python_version=$(python --version 2>&1)
echo "🐍 当前Python版本: $python_version"

# 验证Python版本（需要3.8+）
python_major=$(python -c "import sys; print(sys.version_info.major)")
python_minor=$(python -c "import sys; print(sys.version_info.minor)")

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
    echo "❌ 错误: 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过"

# 🔧 创建虚拟环境
VENV_NAME="aiculture-env"
if [ ! -d "$VENV_NAME" ]; then
    echo "🔧 创建虚拟环境: $VENV_NAME"
    python -m venv $VENV_NAME
else
    echo "📂 虚拟环境已存在: $VENV_NAME"
fi

# 🌟 激活虚拟环境
echo "🌟 激活虚拟环境..."
source $VENV_NAME/bin/activate

# ✅ 验证虚拟环境
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ 错误: 虚拟环境激活失败"
    exit 1
fi

echo "✅ 虚拟环境激活成功: $VIRTUAL_ENV"
echo "📍 Python路径: $(which python)"

# 📦 升级pip
echo "📦 升级pip..."
pip install --upgrade pip --quiet

# 📋 安装生产依赖
echo "📋 安装生产依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "✅ 生产依赖安装完成"
else
    echo "⚠️  警告: requirements.txt 文件不存在"
fi

# 🧪 安装开发依赖
echo "🧪 安装开发依赖..."
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt --quiet
    echo "✅ 开发依赖安装完成"
else
    echo "⚠️  警告: requirements-dev.txt 文件不存在"
fi

# 🔧 安装项目本身（开发模式）
echo "🔧 安装AICultureKit项目（开发模式）..."
pip install -e . --quiet
echo "✅ 项目安装完成"

# 🔒 生成依赖锁定文件
echo "🔒 生成依赖锁定文件..."
pip freeze > requirements.freeze
echo "✅ 依赖锁定文件已生成: requirements.freeze"

# ✅ 验证安装
echo "✅ 验证安装..."
python -c "import aiculture; print('✅ AICultureKit导入成功')" 2>/dev/null || {
    echo "❌ 错误: AICultureKit导入失败"
    exit 1
}

# 📊 显示环境信息
echo ""
echo "📊 环境设置完成！环境信息："
echo "================================================"
echo "🐍 Python版本: $(python --version)"
echo "📍 Python路径: $(which python)"
echo "🌟 虚拟环境: $VIRTUAL_ENV"
echo "📦 已安装包数量: $(pip list --format=freeze | wc -l)"
echo ""

# 💡 使用说明
echo "💡 使用说明："
echo "================================================"
echo "🌟 激活环境: source $VENV_NAME/bin/activate"
echo "❌ 退出环境: deactivate"
echo "🔍 检查状态: python -m aiculture.cli culture-status --path ."
echo "🧪 运行测试: pytest"
echo "🔧 代码检查: python -m aiculture.cli validate --path ."
echo ""

# 🎯 自动运行基本检查
echo "🎯 运行基本环境检查..."
echo "================================================"

# 检查AICultureKit命令是否可用
if python -m aiculture.cli --help > /dev/null 2>&1; then
    echo "✅ AICultureKit CLI可用"
else
    echo "❌ AICultureKit CLI不可用"
fi

# 运行快速验证
echo "🔍 运行快速质量检查..."
python -m aiculture.cli validate --path . > /dev/null 2>&1 && {
    echo "✅ 项目质量检查通过"
} || {
    echo "⚠️  质量检查发现问题，请检查"
}

echo ""
echo "🎉 环境设置完成！开始愉快的开发吧！"
echo "💡 记得在新的终端会话中运行: source $VENV_NAME/bin/activate" 