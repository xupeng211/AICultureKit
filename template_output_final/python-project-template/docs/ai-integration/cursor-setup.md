# Cursor AI 配置和使用指南

## 🎯 配置概述

本指南帮助您正确配置Cursor AI以在AICultureKit项目中获得最佳开发体验。

## 📁 规则文件系统

### 自动加载的规则
项目包含多层级的Cursor规则系统：

```
.cursor/
├── index.mdc           # ✅ 始终生效 - 项目核心规则
└── rules/              # 🎯 按需加载 - 上下文感知规则
    ├── coding-standards.mdc    # 编程时激活
    ├── testing-workflow.mdc    # 测试时激活
    ├── git-workflow.mdc        # 提交时激活
    ├── documentation.mdc       # 写文档时激活
    └── ci-pipeline.mdc         # CI/CD时激活
```

### 配置验证
确保Cursor能够正确加载规则：

1. **检查规则加载**
   - 打开Cursor设置 → Rules
   - 验证项目规则出现在列表中

2. **测试规则生效**
   - 创建新的Python文件
   - 观察AI建议是否符合项目规范
   - 检查代码风格是否自动遵循black格式

## 🚀 使用流程

### 标准开发流程
1. **项目上下文加载**
   ```
   @AI_PROMPT.md @AI_WORK_GUIDE.md

   请帮我开始新的开发任务，首先加载项目上下文。
   ```

2. **特定任务开发**
   - 编写代码时：AI会自动应用coding-standards.mdc
   - 编写测试时：AI会自动应用testing-workflow.mdc
   - 准备提交时：AI会自动应用git-workflow.mdc

3. **质量检查**
   ```bash
   make prepush    # 提交前完整检查
   make lint       # 代码风格检查
   make test       # 运行测试
   ```

## 💡 最佳实践

### Cursor Chat 使用技巧
1. **引用项目文件**
   ```
   @AI_PROMPT.md 根据项目规范实现用户认证功能
   ```

2. **上下文管理**
   - 达到上下文限制时，使用`@AI_WORK_GUIDE.md`快速恢复状态
   - 大型重构前，先运行`make context`

3. **规则冲突处理**
   - 如果AI建议与项目规范冲突，明确引用对应的规则文件
   - 使用`@.cursor/rules/coding-standards.mdc`等明确指定规则

### 常见问题解决

**Q: AI没有遵循项目代码风格**
A: 检查.cursor/rules/coding-standards.mdc是否正确加载，或在提示中明确引用该文件

**Q: 测试生成不符合项目标准**
A: 使用`@.cursor/rules/testing-workflow.mdc`明确指定测试规范

**Q: 提交信息格式不对**
A: 参考`@.cursor/rules/git-workflow.mdc`或运行`make prepush`检查

## 🔧 高级配置

### 个人定制
在不影响团队规则的前提下，您可以：

1. **全局Cursor设置**
   - 配置个人偏好的AI行为
   - 设置代码补全偏好

2. **本地规则扩展**
   - 在`.cursor/rules/my-rules/`下添加个人规则（已在gitignore中）
   - 不会影响团队协作

### 故障排除
- 规则不生效：重启Cursor或重新加载项目
- 性能问题：检查规则文件大小，保持简洁
- 冲突解决：按优先级 index.mdc > rules/*.mdc > 全局设置

---

更多AI集成技巧请参考[提示工程指南](./prompt-engineering.md)。
