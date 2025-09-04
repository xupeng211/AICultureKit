# 🔧 AICultureKit 开发规则

## 📋 基本原则

### 1. 代码质量
- **禁止随意创建新文件**，除非任务明确要求
- **修改已有文件前自动备份**到 `backup/` 目录
- **每个新功能必须写单元测试**，测试覆盖率 >= 80%
- **小功能小commit**，每个commit描述清晰明确
- **遵守项目已有代码风格**，使用black格式化
- **优先复用已有函数/模块**，避免重复造轮子

### 2. 错误处理
- **必须处理异常和边界情况**
- **写结构化日志便于排查错误**
- **使用typing进行类型注解**
- **关键路径添加断言检查**

### 3. 开发流程
- **每次生成代码前加载项目上下文**
- **lint & test 必须通过才能提交**
- **使用语义化版本控制**
- **commit message遵循conventional commits**

## 🎯 代码规范

### Python代码风格
```python
# 使用black格式化，line-length=88
# 使用flake8检查，max-line-length=88
# 使用isort管理导入
# 使用mypy进行类型检查
```

### 文档规范
- 所有public方法必须有docstring
- 使用Google style docstring
- README.md使用中文编写
- API文档使用英文

### 测试规范
- 使用pytest框架
- 测试文件命名：test_*.py
- 测试类命名：Test*
- 测试方法命名：test_*
- 使用fixtures管理测试数据

## 📦 项目结构

```
AICultureKit/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── core/              # 核心模块
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务
│   └── utils/             # 工具函数
├── tests/                 # 测试代码
│   ├── unit/             # 单元测试
│   ├── integration/      # 集成测试
│   └── fixtures/         # 测试数据
├── logs/                 # 日志文件
├── scripts/              # 脚本工具
├── docs/                 # 文档
├── backup/               # 备份文件
├── rules.md             # 开发规则(本文件)
└── Cursor_ClosedLoop_Prompt.md  # Cursor提示词
```

## 🔄 Git工作流

### Commit规范
```
type(scope): description

类型：
- feat: 新功能
- fix: bug修复
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试相关
- chore: 构建工具等

示例：
feat(models): 添加用户数据模型
fix(services): 修复API调用超时问题
```

### 分支规范
- main: 主分支，保持稳定
- develop: 开发分支
- feature/*: 功能分支
- fix/*: 修复分支

## ⚡ 检查点清单

### 🚀 任务启动前（细节规则）
- [ ] **激活虚拟环境** (`source venv/bin/activate` 或 `conda activate <env>`)
- [ ] **确认依赖完整** (检查requirements.txt中的包是否已安装)
- [ ] **切换到feature分支** (避免直接在main/master分支开发)
- [ ] **拉取最新代码** (`git pull origin main` 避免冲突)
- [ ] **加载项目上下文** (`python scripts/context_loader.py`)
- [ ] **验证开发环境** (工具链完整性检查)

### 📋 开发准备前
- [ ] **备份要修改的文件** (自动备份到backup/目录)
- [ ] **了解相关模块和依赖** (分析现有代码结构)
- [ ] **检查是否有可复用代码** (避免重复造轮子)
- [ ] **确认任务分解合理** (大任务拆分为小模块)

### 💻 开发过程中
- [ ] **编写单元测试** (新功能必须有对应测试)
- [ ] **添加类型注解** (提升代码可读性和维护性)
- [ ] **添加异常处理** (考虑边界条件和错误场景)
- [ ] **添加结构化日志** (便于调试和监控)
- [ ] **资源安全检查** (网络请求、文件操作、数据库连接的安全边界)
- [ ] **即时格式化代码** (使用black自动格式化)

### 🔍 开发完成后
- [ ] **自动代码格式化** (`black src/ tests/ scripts/`)
- [ ] **代码风格检查** (`flake8 src/ tests/ scripts/`)
- [ ] **类型检查** (`mypy src/`)
- [ ] **运行单元测试** (`pytest tests/ -v`)
- [ ] **测试覆盖率检查** (`coverage run -m pytest && coverage report`)
- [ ] **代码复杂度分析** (`radon cc src/`)
- [ ] **依赖安全扫描** (`bandit -r src/`)

### 🚀 提交准备前
- [ ] **本地CI预演** (模拟CI流程确保远程绿灯)
- [ ] **所有检查通过** (质量检查器运行成功)
- [ ] **小粒度commit** (只包含本次任务的改动)
- [ ] **commit message规范** (遵循conventional commits)
- [ ] **更新相关文档** (README、API文档等)
- [ ] **记录迭代日志** (写入logs/iteration.log)

### 🌿 协作友好检查
- [ ] **避免覆盖他人改动** (合并前检查冲突)
- [ ] **推送前更新同步** (`git pull --rebase origin main`)
- [ ] **功能分支独立** (避免混合多个功能)
- [ ] **代码审查就绪** (代码清晰、注释完整)

## 🚨 禁止行为

- ❌ 提交未测试的代码
- ❌ 硬编码敏感信息
- ❌ 忽略异常处理
- ❌ 创建过于复杂的函数（圈复杂度>10）
- ❌ 使用过时的Python特性
- ❌ 不写注释的复杂逻辑 