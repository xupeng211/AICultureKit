#!/bin/bash
# AICultureKit 依赖管理脚本
# 用于自动化依赖管理任务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查虚拟环境
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        log_warning "未检测到虚拟环境，建议在虚拟环境中运行"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_info "虚拟环境: $VIRTUAL_ENV"
    fi
}

# 安装生产依赖
install_prod() {
    log_info "安装生产依赖..."
    pip install -e .
    log_success "生产依赖安装完成"
}

# 安装开发依赖
install_dev() {
    log_info "安装开发依赖..."
    pip install -e ".[dev]"
    log_success "开发依赖安装完成"
}

# 安装传统方式依赖
install_legacy() {
    log_info "使用传统方式安装依赖..."
    pip install -r requirements-dev.txt
    log_success "传统方式依赖安装完成"
}

# 更新依赖
update_deps() {
    log_info "检查过时的依赖..."
    pip list --outdated

    log_info "更新依赖..."
    pip install --upgrade pip setuptools wheel
    pip install -e ".[dev]" --upgrade

    log_success "依赖更新完成"
}

# 生成锁定文件
generate_lock() {
    log_info "生成依赖锁定文件..."
    pip freeze > requirements.lock
    log_success "锁定文件已生成: requirements.lock"
}

# 安全检查
security_check() {
    log_info "执行安全检查..."

    # 检查是否安装了安全工具
    if ! command -v safety &> /dev/null; then
        log_warning "safety 未安装，正在安装..."
        pip install safety
    fi

    if ! command -v pip-audit &> /dev/null; then
        log_warning "pip-audit 未安装，正在安装..."
        pip install pip-audit
    fi

    # 运行安全检查
    log_info "运行 safety 检查..."
    safety check || log_warning "发现安全问题，请检查上述输出"

    log_info "运行 pip-audit 检查..."
    pip-audit || log_warning "发现漏洞，请检查上述输出"

    log_success "安全检查完成"
}

# 清理环境
clean_env() {
    log_info "清理pip缓存..."
    pip cache purge

    log_info "清理Python缓存..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true

    log_success "环境清理完成"
}

# 验证安装
verify_install() {
    log_info "验证安装..."

    # 检查主要命令
    if command -v aiculture &> /dev/null; then
        log_success "aiculture 命令可用: $(aiculture --version)"
    else
        log_error "aiculture 命令不可用"
        return 1
    fi

    # 检查开发工具
    local tools=("black" "flake8" "mypy" "pytest")
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            log_success "$tool 可用"
        else
            log_warning "$tool 不可用"
        fi
    done

    log_success "安装验证完成"
}

# 显示帮助
show_help() {
    cat << EOF
AICultureKit 依赖管理脚本

用法: $0 [命令]

命令:
    install-prod     安装生产依赖 (推荐)
    install-dev      安装开发依赖 (推荐)
    install-legacy   使用传统方式安装依赖
    update           更新所有依赖
    lock             生成依赖锁定文件
    security         运行安全检查
    clean            清理环境
    verify           验证安装
    help             显示此帮助信息

示例:
    $0 install-dev   # 安装开发环境
    $0 update        # 更新依赖
    $0 security      # 安全检查

EOF
}

# 主函数
main() {
    case "${1:-help}" in
        "install-prod")
            check_venv
            install_prod
            verify_install
            ;;
        "install-dev")
            check_venv
            install_dev
            verify_install
            ;;
        "install-legacy")
            check_venv
            install_legacy
            verify_install
            ;;
        "update")
            check_venv
            update_deps
            generate_lock
            ;;
        "lock")
            generate_lock
            ;;
        "security")
            security_check
            ;;
        "clean")
            clean_env
            ;;
        "verify")
            verify_install
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
