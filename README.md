# 🧠 AICultureKit - Cursor 闭环开发系统

一个完整的AI辅助开发闭环系统，让Cursor能够自动化地完成从任务分解到代码生成、测试、提交的整个开发流程。

## 🎯 系统特色

- **🔄 完整闭环**: 从任务描述到代码提交的全自动化流程
- **🛡️ 质量保证**: 多层次的代码质量检查和自动修复
- **📊 智能分析**: 深度项目上下文分析和依赖关系检测
- **🔧 自动修复**: 智能识别和修复常见代码问题
- **📝 详细日志**: 完整的开发过程记录和迭代追踪

## 📦 项目结构

```
AICultureKit/
├── src/                           # 源代码目录
│   ├── __init__.py
│   ├── core/                     # 核心模块
│   ├── models/                   # 数据模型
│   ├── services/                 # 业务服务
│   └── utils/                    # 工具函数
├── tests/                        # 测试代码
│   ├── unit/                    # 单元测试
│   ├── integration/             # 集成测试
│   └── fixtures/                # 测试数据
├── scripts/                      # 核心脚本
│   ├── env_checker.py           # 开发环境检查器
│   ├── context_loader.py        # 项目上下文加载器
│   ├── quality_checker.py       # 代码质量检查器
│   ├── cursor_runner.py         # 闭环执行器
│   └── setup_project.py         # 项目初始化脚本
├── logs/                         # 日志文件
├── docs/                         # 文档目录
├── backup/                       # 文件备份
├── rules.md                      # 开发规则
├── Cursor_ClosedLoop_Prompt.md   # Cursor提示词模板
└── README.md                     # 项目说明（本文件）
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd AICultureKit

# 使用Makefile一键初始化（推荐）
make init

# 或手动初始化
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 使用Makefile自动化工具

```bash
# 查看所有可用命令
make help

# 🔥 最常用的命令：
make dev          # 快速准备开发环境
make env-check    # 环境检查
make prepush      # 提交前完整检查+推送+Issue同步
make status       # 查看项目状态

# 📋 开发工作流：
make format       # 代码格式化
make test         # 运行测试
make quality      # 完整质量检查
make ci           # 本地CI模拟

# 📋 Issue管理：
make sync         # 同步ISSUES.md到远程仓库
make sync-config  # 配置Issue同步环境
```

### 3. Issue自动同步功能

本系统支持自动将本地的`ISSUES.md`文件同步到GitHub/Gitee：

```bash
# 1. 配置Issue同步
make sync-config

# 2. 编辑ISSUES.md文件，每行一个Issue标题

# 3. 同步到远程仓库
make sync

# 或者在prepush中自动同步
make prepush
```

**支持的平台：**
- GitHub（需要 gh CLI）
- Gitee（需要 tea CLI）

**配置示例：**
```bash
# GitHub配置
export GIT_PLATFORM=github
gh auth login

# Gitee配置  
export GIT_PLATFORM=gitee
tea login add
```

### 3. 传统方式（手动执行）

```bash
# 1. 环境检查（新增）
python scripts/env_checker.py --summary --fix-suggestions

# 2. 加载项目上下文
python scripts/context_loader.py --summary

# 3. 运行质量检查
python scripts/quality_checker.py --summary

# 4. 完整闭环执行
python scripts/cursor_runner.py --task "你的任务" --summary

# 5. 查看结果
cat logs/project_context.json
cat logs/quality_check.json
cat logs/cursor_execution.json
cat logs/iteration.log
```

### 4. 失败保护机制

本系统具有完整的失败保护机制，确保代码质量：

```bash
make prepush    # 一键完成所有检查+推送+同步
```

**保护层级：**
1. 🔍 **环境检查** - 虚拟环境、依赖、Git分支
2. 📋 **项目上下文** - 加载项目结构和Git历史
3. 🔧 **代码质量** - 格式化、lint、类型检查、安全检查
4. 🧪 **单元测试** - 测试通过率和覆盖率
5. 📦 **Git推送** - 只有所有检查通过才推送
6. 📋 **Issues同步** - 推送成功后同步Issues

**如果任何检查失败，整个流程自动停止，避免推送半成品代码！**

详细演示请查看：[失败保护机制演示](docs/FAILURE_PROTECTION_DEMO.md)

## 🔧 核心组件

### 🔍 开发环境检查器 (`scripts/env_checker.py`)

执行任务启动前的细节规则检查，确保开发环境处于最佳状态：

```bash
# 基础环境检查
python scripts/env_checker.py

# 显示检查摘要和修复建议
python scripts/env_checker.py --summary --fix-suggestions

# 指定项目目录
python scripts/env_checker.py --project-root /path/to/project
```

**检查项目：**
- 🌐 虚拟环境状态检查
- 📦 依赖完整性验证
- 🌿 Git分支和同步状态
- 🔧 开发工具完整性
- 📁 项目结构完整性
- 🛡️ 环境安全检查

### 📋 项目上下文加载器 (`scripts/context_loader.py`)

自动收集项目信息，为AI提供完整的开发上下文：

```bash
# 基础使用
python scripts/context_loader.py

# 自定义输出
python scripts/context_loader.py --output custom_context.json --summary

# 指定项目目录
python scripts/context_loader.py --project-root /path/to/project
```

**功能特性：**
- 📁 目录结构扫描
- 🌿 Git历史分析
- 📦 模块依赖检测
- 🧪 测试文件识别
- 📊 项目统计信息

### ✅ 代码质量检查器 (`scripts/quality_checker.py`)

执行全面的代码质量检查和自动修复：

```bash
# 基础检查
python scripts/quality_checker.py

# 自定义重试次数
python scripts/quality_checker.py --max-retries 5

# 指定输出文件
python scripts/quality_checker.py --output quality_report.json --summary
```

**检查项目：**
- 🔧 Black代码格式化
- 📏 Flake8风格检查
- 🔍 MyPy类型检查
- 🧪 Pytest单元测试
- 📊 Coverage覆盖率分析
- 🎯 Radon复杂度检查

## 📝 开发工作流

### 标准开发流程

1. **🔍 环境检查**
   ```bash
   # 检查开发环境是否就绪
   python scripts/env_checker.py --summary --fix-suggestions
   ```

2. **📋 任务分解**
   ```bash
   # 明确任务描述
   TASK="实现数据分析模块"
   ```

3. **🔍 上下文加载**
   ```bash
   python scripts/context_loader.py --summary
   ```

3. **💻 代码开发**
   - 按照 `rules.md` 中的规范编写代码
   - 遵循模块化、可测试的原则

4. **✅ 质量检查**
   ```bash
   python scripts/quality_checker.py --summary
   ```

5. **🔧 问题修复**
   - 系统会自动尝试修复可修复的问题
   - 手动解决复杂问题

6. **🚀 提交代码**
   ```bash
   git add .
   git commit -m "feat(module): 实现数据分析模块"
   git push origin main
   ```

### Cursor集成工作流

```bash
# 在Cursor中粘贴以下内容：

TASK: 实现球队赛果预测模块

请按照以下步骤执行完整的开发闭环：

1. 加载项目上下文（运行 scripts/context_loader.py）
2. 分析已有模块和依赖关系
3. 拆解任务为可测试的子模块
4. 生成高质量代码（包含类型注解、异常处理、日志）
5. 编写对应的单元测试
6. 运行质量检查（scripts/quality_checker.py）
7. 自动修复发现的问题
8. 提交代码并记录日志

要求：
- 严格遵守 rules.md 中的规范
- 确保测试覆盖率 >= 80%
- 代码复杂度 <= 10
- 所有检查必须通过才能提交
```

## 📊 监控和日志

### 日志文件说明

- **`logs/project_context.json`**: 项目上下文快照
- **`logs/quality_check.json`**: 质量检查详细结果
- **`logs/iteration.log`**: 开发迭代历史记录

### 查看系统状态

```bash
# 查看最新的上下文信息
jq '.project_stats' logs/project_context.json

# 查看质量检查摘要
jq '.checks | to_entries[] | {name: .value.name, success: .value.success, message: .value.message}' logs/quality_check.json

# 查看最近的迭代日志
tail -10 logs/iteration.log
```

## 🎨 自定义配置

### 环境变量

```bash
# 代码质量阈值
export CODE_QUALITY_THRESHOLD=85
export TEST_COVERAGE_MIN=90
export MAX_COMPLEXITY=8

# 自定义目录
export BACKUP_DIR="backup/custom"
export LOG_FILE="logs/custom_iteration.log"
```

### 规则自定义

编辑 `rules.md` 文件来自定义项目的开发规范：

- 代码风格规则
- 测试要求
- 提交规范
- 文档标准

## 🔧 故障排除

### 常见问题

1. **依赖缺失**
   ```bash
   # 安装缺失的工具
   pip install black flake8 mypy pytest coverage radon isort
   ```

2. **权限问题**
   ```bash
   # 确保脚本有执行权限
   chmod +x scripts/*.py
   ```

3. **Git配置**
   ```bash
   # 初始化Git仓库（如果需要）
   git init
   git remote add origin <your-repo-url>
   ```

### 调试模式

```bash
# 启用详细输出
python scripts/context_loader.py --summary
python scripts/quality_checker.py --summary

# 查看具体错误
cat logs/quality_check.json | jq '.checks | to_entries[] | select(.value.success == false)'
```

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 遵循 `rules.md` 中的开发规范
4. 确保所有检查通过
5. 提交变更 (`git commit -m 'feat: add amazing feature'`)
6. 推送分支 (`git push origin feature/amazing-feature`)
7. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🎯 下一步计划

- [ ] 支持更多编程语言
- [ ] 集成更多代码质量工具
- [ ] 添加可视化仪表盘
- [ ] 支持云端协作
- [ ] 集成CI/CD流水线

---

**�� 享受高效的AI辅助开发体验！** 