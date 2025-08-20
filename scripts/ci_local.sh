#!/bin/bash
# 本地CI检查脚本 - 在提交前运行完整的质量检查

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 输出函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python环境
check_python_env() {
    log_info "检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装"
        exit 1
    fi
    
    if ! pip list | grep -q "black\|flake8\|mypy\|pytest"; then
        log_warning "缺少开发依赖，尝试安装..."
        pip install -r requirements-dev.txt
    fi
    
    log_success "Python环境检查通过"
}

# 代码格式化检查
check_formatting() {
    log_info "检查代码格式化..."
    
    # Black 格式化检查
    if command -v black &> /dev/null; then
        if black --check .; then
            log_success "Black格式化检查通过"
        else
            log_error "Black格式化检查失败，运行 'black .' 修复"
            return 1
        fi
    else
        log_warning "Black未安装，跳过格式化检查"
    fi
    
    # isort 导入排序检查
    if command -v isort &> /dev/null; then
        if isort --check-only .; then
            log_success "isort导入排序检查通过"
        else
            log_error "isort导入排序检查失败，运行 'isort .' 修复"
            return 1
        fi
    else
        log_warning "isort未安装，跳过导入排序检查"
    fi
}

# 静态代码检查
check_linting() {
    log_info "运行静态代码检查..."
    
    # Flake8检查
    if command -v flake8 &> /dev/null; then
        if flake8 .; then
            log_success "Flake8检查通过"
        else
            log_error "Flake8检查失败"
            return 1
        fi
    else
        log_warning "Flake8未安装，跳过静态检查"
    fi
    
    # MyPy类型检查
    if command -v mypy &> /dev/null; then
        if mypy .; then
            log_success "MyPy类型检查通过"
        else
            log_error "MyPy类型检查失败"
            return 1
        fi
    else
        log_warning "MyPy未安装，跳过类型检查"
    fi
}

# 安全检查
check_security() {
    log_info "运行安全检查..."
    
    # Bandit安全检查
    if command -v bandit &> /dev/null; then
        if bandit -r . -f json -o bandit-report.json; then
            log_success "Bandit安全检查通过"
        else
            log_warning "Bandit安全检查发现问题，查看 bandit-report.json"
        fi
    else
        log_warning "Bandit未安装，跳过安全检查"
    fi
    
    # 检查是否有密钥泄漏
    if command -v detect-secrets &> /dev/null; then
        if detect-secrets scan --baseline .secrets.baseline; then
            log_success "密钥泄漏检查通过"
        else
            log_error "检测到可能的密钥泄漏"
            return 1
        fi
    else
        log_warning "detect-secrets未安装，跳过密钥检查"
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试用例..."
    
    if command -v pytest &> /dev/null; then
        if pytest --cov=aiculture --cov-report=term-missing --cov-report=html; then
            log_success "测试用例全部通过"
        else
            log_error "部分测试用例失败"
            return 1
        fi
    else
        log_warning "Pytest未安装，跳过测试"
    fi
}

# 构建检查
check_build() {
    log_info "检查包构建..."
    
    if command -v python3 &> /dev/null; then
        # 清理之前的构建
        rm -rf build/ dist/ *.egg-info/
        
        # 构建包
        if python -m build; then
            log_success "包构建成功"
        else
            log_error "包构建失败"
            return 1
        fi
        
        # 检查包
        if command -v twine &> /dev/null; then
            if twine check dist/*; then
                log_success "包检查通过"
            else
                log_error "包检查失败"
                return 1
            fi
        fi
    fi
}

# Docker构建检查
check_docker() {
    if [ -f "Dockerfile" ] && command -v docker &> /dev/null; then
        log_info "检查Docker构建..."
        
        if docker build -t aiculture-kit:local .; then
            log_success "Docker构建成功"
        else
            log_error "Docker构建失败"
            return 1
        fi
    else
        log_info "跳过Docker检查（无Dockerfile或Docker未安装）"
    fi
}

# 主执行函数
main() {
    echo "🚀 开始本地CI检查..."
    echo "========================================"
    
    local exit_code=0
    
    # 执行所有检查
    check_python_env || exit_code=1
    check_formatting || exit_code=1
    check_linting || exit_code=1
    check_security || exit_code=1
    run_tests || exit_code=1
    check_build || exit_code=1
    check_docker || exit_code=1
    
    echo "========================================"
    
    if [ $exit_code -eq 0 ]; then
        log_success "🎉 所有检查通过！代码准备就绪"
        echo
        echo "📋 后续操作建议："
        echo "  1. git add ."
        echo "  2. git commit -m 'feat: 新功能描述'"
        echo "  3. git push"
    else
        log_error "💥 部分检查失败，请修复后重试"
        echo
        echo "🔧 常见修复命令："
        echo "  black .          # 自动格式化代码"
        echo "  isort .          # 自动排序导入"
        echo "  pip install -r requirements-dev.txt  # 安装缺失依赖"
    fi
    
    exit $exit_code
}

# 帮助信息
show_help() {
    echo "AICultureKit 本地CI检查脚本"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  --format-only  仅运行格式化检查"
    echo "  --test-only    仅运行测试"
    echo "  --no-build     跳过构建检查"
    echo "  --no-docker    跳过Docker检查"
    echo
    echo "示例:"
    echo "  $0                # 运行完整检查"
    echo "  $0 --format-only  # 只检查格式化"
    echo "  $0 --test-only    # 只运行测试"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --format-only)
            check_python_env
            check_formatting
            exit $?
            ;;
        --test-only)
            check_python_env
            run_tests
            exit $?
            ;;
        --no-build)
            SKIP_BUILD=1
            shift
            ;;
        --no-docker)
            SKIP_DOCKER=1
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 执行主函数
main 