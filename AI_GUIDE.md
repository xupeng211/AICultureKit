# Python项目AI协作指南

## 🎯 项目原则
- **YAGNI**: 不要实现当前不需要的功能
- **KISS**: 保持代码简单清晰
- **SOLID**: 遵循面向对象设计原则
- 优雅代码，避免过度设计

## 🐍 Python代码规范
- 使用 Black 格式化 (行长度88)
- 使用 isort 整理导入
- 使用 flake8 进行静态检查
- 使用 mypy 进行类型检查
- 测试覆盖率 > 80%

## 🤖 AI协作要求
1. **增量开发**: 每次只专注一个功能点
2. **测试驱动**: 先写测试再写实现
3. **文档优先**: 复杂逻辑要有清晰注释
4. **类型安全**: 所有函数都要有类型提示

## ✅ 提交前检查清单
- [ ] 代码已格式化 (black)
- [ ] 导入已整理 (isort)
- [ ] 通过静态检查 (flake8, mypy)
- [ ] 测试通过 (pytest)
- [ ] 提交信息规范 (conventional commits)

## 🔧 常用命令
```bash
# 格式化代码
black .
isort .

# 质量检查
flake8 .
mypy .

# 运行测试
pytest --cov

# pre-commit检查
pre-commit run --all-files
```
