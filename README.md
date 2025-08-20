# AICultureKit 🤖✨

> 企业级AI主导开发文化标准化工具包 - 让AI协作开发更专业、更可靠

[![CI/CD](https://github.com/xupeng211/AICultureKit/workflows/CI/badge.svg)](https://github.com/xupeng211/AICultureKit/actions)
[![Quality Gate](https://github.com/xupeng211/AICultureKit/workflows/Quality%20Gate/badge.svg)](https://github.com/xupeng211/AICultureKit/actions)
[![Culture Check](https://github.com/xupeng211/AICultureKit/workflows/Culture%20Check/badge.svg)](https://github.com/xupeng211/AICultureKit/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code Coverage](https://img.shields.io/badge/coverage-39%25-yellow.svg)](https://github.com/xupeng211/AICultureKit)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/xupeng211/AICultureKit?style=social)](https://github.com/xupeng211/AICultureKit/stargazers)

## 🎯 项目愿景

AICultureKit 旨在解决AI主导开发中的质量和一致性问题。通过标准化开发文化、自动化质量检查和提供最佳实践模板，确保无论是人工开发还是AI协助开发，都能保持高质量和可维护性。

## 📊 项目统计

- 🏗️ **190+ 文件** - 完整的项目结构
- 🧪 **39% 测试覆盖率** - 持续提升中
- 🔧 **13个核心模块** - 模块化架构
- 📚 **50+ 示例** - 丰富的使用案例
- 🌍 **多语言支持** - 中英文文档
- ⚡ **智能错误处理** - 企业级可靠性

## 🎬 演示视频

> 📹 **即将推出**: 完整的使用演示视频和教程

## 🌟 主要亮点

- ✅ **零配置启动** - 一键创建标准化项目
- ✅ **AI协作优化** - 专为AI辅助开发设计
- ✅ **企业级质量** - 完整的CI/CD和质量门禁
- ✅ **包容性设计** - 支持可访问性和国际化
- ✅ **持续演进** - 基于实际使用反馈优化

## ✨ 核心特性

### 🚀 一键项目初始化

- **智能脚手架**: 类似cookiecutter，但专为AI协作优化
- **多语言支持**: Python、JavaScript/TypeScript项目模板
- **完整CI/CD**: 预配置GitHub Actions工作流
- **质量保证**: 自动集成linting、测试、安全检查

### 🔧 质量工具集成

- **代码格式化**: Black、Prettier自动配置
- **静态分析**: flake8、ESLint、mypy类型检查
- **安全扫描**: Bandit安全漏洞检测
- **测试覆盖**: pytest、Jest测试框架集成
- **pre-commit**: 提交前自动质量检查

### 🤖 AI协作优化

- **智能提示词**: 为AI助手提供项目特定的上下文
- **增量开发**: 支持AI驱动的迭代开发流程
- **文档优先**: 自动生成AI协作指南和最佳实践

### 🔄 可持续演进

- **插件化架构**: 易于扩展和自定义
- **版本管理**: 规范的语义化版本控制
- **远程更新**: 支持规则和模板的热更新

## 🚀 快速开始

### 📦 安装

```bash
# 方式1: 从PyPI安装 (推荐)
pip install aiculture-kit

# 方式2: 从源码安装 (开发版本)
git clone https://github.com/xupeng211/AICultureKit.git
cd AICultureKit
pip install -e ".[dev]"

# 方式3: 使用pipx安装 (隔离环境)
pipx install aiculture-kit
```

### ⚡ 30秒体验

```bash
# 1. 创建新项目
aiculture create my-awesome-project --template python

# 2. 进入项目目录
cd my-awesome-project

# 3. 查看生成的结构
tree -a -L 2

# 4. 运行质量检查
aiculture check

# 5. 启动开发环境
python -m pytest  # 运行测试
```

### 🎯 核心命令

```bash
# 项目管理
aiculture create <project-name>     # 创建新项目
aiculture init                      # 为现有项目添加文化规范
cd existing-project
aiculture setup

# 运行质量检查
aiculture check

# 生成AI协作指南
aiculture guide --template python
```

### 高级用法

```bash
# 创建不同类型的项目
aiculture create web-app --template javascript
aiculture create api-service --template python --with-docker

# 自定义配置
aiculture culture  # 查看当前文化配置
aiculture check --fix  # 自动修复代码质量问题

# 本地质量检查脚本
./scripts/ci_local.sh  # 运行完整的本地CI流程
```

## 📁 项目结构

生成的项目将包含以下标准化结构：

```
my-project/
├── .github/
│   └── workflows/
│       ├── ci.yml          # 持续集成
│       └── cd.yml          # 持续部署
├── aiculture/              # 核心业务逻辑
│   ├── __init__.py
│   ├── core.py
│   └── cli.py
├── tests/                  # 测试文件
├── scripts/
│   └── ci_local.sh         # 本地CI脚本
├── docs/
│   ├── DEV_CULTURE.md      # 开发文化说明
│   └── AI_GUIDE.md         # AI协作指南
├── .pre-commit-config.yaml # pre-commit配置
├── .gitignore
├── pyproject.toml          # 项目配置
├── requirements.txt        # 生产依赖
├── requirements-dev.txt    # 开发依赖
├── env.example             # 环境变量示例
└── README.md
```

## 🎨 文化原则

### YAGNI - You Aren't Gonna Need It

- ✅ 只实现当前明确需要的功能
- ❌ 避免为未来可能的需求过度设计

### KISS - Keep It Simple, Stupid

- ✅ 优先选择简单易懂的解决方案
- ❌ 避免不必要的复杂性和抽象

### SOLID 面向对象设计原则

- **S**ingle Responsibility - 单一职责
- **O**pen/Closed - 开放/封闭
- **L**iskov Substitution - 里氏替换
- **I**nterface Segregation - 接口隔离
- **D**ependency Inversion - 依赖倒置

### AI协作友好

- 📝 清晰的文档和注释
- 🔄 增量式开发和测试
- 🎯 明确的任务边界和上下文

## 🔍 代码质量检查

AICultureKit 集成了多层次的质量保证机制：

### 本地开发

```bash
# 格式化代码
black .
isort .

# 静态检查
flake8 .
mypy .

# 安全检查
bandit -r .

# 运行测试
pytest --cov
```

### pre-commit 钩子

提交前自动运行：

- 代码格式化检查
- 静态代码分析
- 测试用例执行
- 安全漏洞扫描
- 密钥泄漏检测

### CI/CD 流水线

- ✅ 多Python版本兼容性测试
- ✅ 代码覆盖率检查（>80%）
- ✅ 安全漏洞扫描
- ✅ 构建和打包验证
- ✅ 自动化部署

## 🤖 AI协作指南

### 开始AI协作前

1. 运行 `aiculture guide` 生成项目特定的AI指南
2. 将指南内容提供给AI助手作为上下文
3. 确保AI理解项目的文化原则和技术约束

### 协作流程

1. **明确任务**: 清晰描述要实现的功能
2. **增量开发**: 将大任务拆分成小步骤
3. **测试驱动**: 先编写测试用例
4. **代码实现**: 编写满足测试的最小代码
5. **质量检查**: 运行 `aiculture check`
6. **文档更新**: 更新相关文档和注释

### AI提示词模板

```
你是我的AI编程伙伴，请遵循以下开发文化：

🎯 核心原则：
- YAGNI: 只实现当前需要的功能
- KISS: 保持代码简单清晰
- SOLID: 遵循面向对象设计原则

🐍 Python规范：
- 使用Black格式化（行长度88）
- 使用type hints
- 编写docstring文档
- 测试覆盖率>80%

🔧 开发流程：
1. 先编写测试用例
2. 实现最小可工作代码
3. 重构和优化
4. 更新文档

请在编写代码时严格遵循这些规范。
```

## 📚 文档和资源

- [开发文化详细说明](docs/DEV_CULTURE.md)
- [API文档](docs/api.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)
- [常见问题](docs/FAQ.md)

## 🛣️ 发展路线图

### v0.1.0 - MVP ✅

- [x] 基础项目模板
- [x] Python项目支持
- [x] CLI命令行工具
- [x] pre-commit集成
- [x] GitHub Actions模板

### v0.2.0 - 扩展支持

- [ ] JavaScript/TypeScript模板
- [ ] Docker容器化支持
- [ ] 更多质量工具集成
- [ ] 项目模板自定义

### v0.3.0 - AI增强

- [ ] 智能代码审查
- [ ] AI提示词优化
- [ ] 自动化重构建议
- [ ] 性能分析集成

### v1.0.0 - 企业级

- [ ] 企业级安全扫描
- [ ] 多团队协作支持
- [ ] 合规性检查
- [ ] 高级报告和分析

## 🤝 参与贡献

我们欢迎任何形式的贡献！

### 贡献方式

- 🐛 报告Bug
- 💡 提出新功能
- 📝 改进文档
- 🔧 提交代码

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-username/AICultureKit.git
cd AICultureKit

# 安装开发依赖（推荐方式）
pip install -e ".[dev]"

# 或使用传统方式
# pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install

# 运行测试
pytest

# 验证安装
aiculture --version
```

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 添加JavaScript项目模板
fix: 修复pre-commit配置问题
docs: 更新README文档
```

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 👥 贡献者

感谢所有为AICultureKit做出贡献的开发者！

<!-- 贡献者列表将自动更新 -->
<a href="https://github.com/xupeng211/AICultureKit/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=xupeng211/AICultureKit" />
</a>

### 🏆 特别感谢

- **[@xupeng211](https://github.com/xupeng211)** - 项目创始人和主要维护者
- **AI助手们** - Claude、GPT等AI伙伴的协作支持
- **开源社区** - 提供了优秀的基础工具和灵感

## 🙏 致谢

本项目基于以下优秀的开源项目构建：

- [Black](https://github.com/psf/black) - Python代码格式化
- [pre-commit](https://pre-commit.com/) - Git钩子管理
- [Click](https://click.palletsprojects.com/) - 命令行接口框架
- [pytest](https://pytest.org/) - 测试框架
- [Cookiecutter](https://cookiecutter.readthedocs.io/) - 项目模板灵感

## 📞 联系我们

- 🐛 **问题报告**: [GitHub Issues](https://github.com/xupeng211/AICultureKit/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/xupeng211/AICultureKit/discussions)
- 📖 **文档**: [项目文档](https://github.com/xupeng211/AICultureKit/tree/main/docs)
- 🔗 **项目主页**: [AICultureKit](https://github.com/xupeng211/AICultureKit)

---

**开始你的AI协作开发之旅！** 🚀

```bash
pip install aiculture-kit
aiculture create my-next-project
```
