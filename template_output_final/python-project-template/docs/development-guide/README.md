# AICultureKit 开发指南

## 📋 指南概述

本开发指南旨在帮助开发者快速理解和参与AICultureKit项目开发。

## 📚 指南内容

### 基础设置
- [环境搭建](./setup.md) - 开发环境配置和依赖安装
- [项目架构](./architecture.md) - 系统架构和设计原理

### 开发规范
- [最佳实践](./best-practices.md) - 开发最佳实践合集
- 具体规范请参考[.cursor/rules/](../../.cursor/rules/)目录

### AI集成
- [AI工具配置](../ai-integration/cursor-setup.md) - Cursor等AI工具配置
- [提示工程](../ai-integration/prompt-engineering.md) - AI提示优化技巧

## 🚀 快速开始

1. **环境准备**
   ```bash
   make env-check    # 检查环境
   make install      # 安装依赖
   ```

2. **AI工具配置**
   - 阅读[AI_WORK_GUIDE.md](../../AI_WORK_GUIDE.md)
   - 配置Cursor规则系统

3. **开始开发**
   ```bash
   make context      # 加载项目上下文
   make test         # 运行测试确认环境OK
   ```

## 🤝 贡献指南

- 遵循[Git工作流规范](../../.cursor/rules/git-workflow.mdc)
- 确保代码通过[CI检查](../../.cursor/rules/ci-pipeline.mdc)
- 编写符合[测试标准](../../.cursor/rules/testing-workflow.mdc)的测试

---

有问题？查看[FAQ](./faq.md)或提交Issue。
