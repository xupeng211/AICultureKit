# 🤝 为 AICultureKit 贡献

感谢你对 AICultureKit 的兴趣！我们欢迎所有形式的贡献，无论是代码、文档、bug报告还是功能建议。

## 🌟 贡献原则

AICultureKit 遵循以下核心原则：

- **🤖 AI优先**: 拥抱AI辅助开发，提高效率和质量
- **🌍 包容性**: 欢迎所有背景的贡献者
- **♿ 可访问性**: 确保所有用户都能使用我们的工具
- **🔒 安全第一**: 始终考虑安全性和隐私保护
- **📚 文档驱动**: 良好的文档是优秀软件的基础

## 🚀 快速开始

### 环境准备

1. **Fork 仓库**
   ```bash
   # 在GitHub上fork仓库，然后克隆你的fork
   git clone https://github.com/YOUR_USERNAME/AICultureKit.git
   cd AICultureKit
   ```

2. **设置开发环境**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   
   # 安装依赖
   pip install -e ".[dev]"
   
   # 设置Git钩子
   chmod +x scripts/setup_hooks.sh
   ./scripts/setup_hooks.sh
   ```

3. **验证安装**
   ```bash
   # 运行测试
   python -m pytest
   
   # 检查代码质量
   python -m aiculture check
   ```

## 📝 贡献类型

### 🐛 Bug 报告

发现bug？请创建一个Issue并包含：

- **清晰的标题**：简要描述问题
- **环境信息**：Python版本、操作系统等
- **重现步骤**：详细的步骤说明
- **预期行为**：你期望发生什么
- **实际行为**：实际发生了什么
- **错误日志**：相关的错误信息

### ✨ 功能请求

有好想法？我们很乐意听到！请包含：

- **功能描述**：详细说明建议的功能
- **使用场景**：为什么需要这个功能
- **实现建议**：如果有的话，提供实现思路

### 💻 代码贡献

#### 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

2. **编写代码**
   - 遵循现有代码风格
   - 添加必要的测试
   - 更新相关文档

3. **提交代码**
   ```bash
   # 使用语义化提交信息
   git commit -m "feat: 添加新的文化检查功能"
   git commit -m "fix: 修复CLI参数解析问题"
   git commit -m "docs: 更新API文档"
   ```

4. **推送并创建PR**
   ```bash
   git push origin your-branch-name
   ```

#### 代码标准

- **Python风格**: 遵循PEP 8
- **类型提示**: 使用类型注解
- **文档字符串**: 使用Google风格的docstring
- **测试**: 保持测试覆盖率 > 80%

#### 提交信息格式

使用[约定式提交](https://www.conventionalcommits.org/zh-hans/)：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

类型包括：
- `feat`: 新功能
- `fix`: bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/test_core.py

# 生成覆盖率报告
python -m pytest --cov=aiculture --cov-report=html
```

### 编写测试

- 为新功能添加测试
- 确保测试具有描述性的名称
- 使用pytest fixtures
- 模拟外部依赖

## 📚 文档

### 文档类型

- **API文档**: 自动从docstring生成
- **用户指南**: 在`docs/`目录中
- **示例代码**: 在`examples/`目录中

### 文档标准

- 使用Markdown格式
- 包含代码示例
- 考虑不同技能水平的用户
- 支持多语言（优先中英文）

## 🔍 代码审查

### 审查标准

- **功能性**: 代码是否按预期工作
- **可读性**: 代码是否清晰易懂
- **测试**: 是否有充分的测试覆盖
- **文档**: 是否有适当的文档
- **性能**: 是否有性能影响
- **安全性**: 是否引入安全风险

### 审查流程

1. 自动化检查通过
2. 至少一个维护者审查
3. 解决所有反馈
4. 合并到主分支

## 🌍 国际化

我们致力于让AICultureKit支持多种语言：

- 使用`aiculture.i18n`模块进行国际化
- 避免硬编码文本
- 考虑不同文化的使用习惯

## ♿ 可访问性

确保所有用户都能使用我们的工具：

- 提供清晰的错误信息
- 支持屏幕阅读器
- 使用语义化的输出格式
- 提供多种交互方式

## 🆘 获得帮助

需要帮助？可以通过以下方式：

- **GitHub Issues**: 提问或报告问题
- **GitHub Discussions**: 社区讨论
- **文档**: 查看项目文档

## 📜 行为准则

我们致力于创建一个友好、包容的社区环境。请：

- 尊重所有参与者
- 使用包容性语言
- 接受建设性批评
- 关注对社区最有利的事情

## 🎉 认可贡献者

我们感谢所有贡献者的努力！贡献者将被列在：

- README.md的贡献者部分
- 发布说明中
- 项目文档中

---

**再次感谢你的贡献！让我们一起构建更好的AI开发文化！** 🚀
