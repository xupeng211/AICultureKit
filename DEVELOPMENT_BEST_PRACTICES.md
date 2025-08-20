# AICultureKit 开发最佳实践指南

## 🎯 开发文化原则

作为一个倡导AI协作开发文化的项目，我们必须**言行一致**，在自己的项目中严格践行所倡导的开发标准。

---

## 🔄 日常开发流程

### 📝 提交前检查清单

在每次提交代码前，请按以下顺序执行：

```bash
# 1. 运行本地CI检查
./scripts/ci_local.sh

# 2. 如果有格式化问题，自动修复
black .
isort .

# 3. 运行测试确保功能正常
pytest --cov=aiculture --cov-report=term-missing

# 4. 检查代码覆盖率是否下降
# 目标：保持在32%以上，逐步提升到80%

# 5. 提交代码
git add .
git commit -m "你的提交信息"
```

### 🚀 Pre-commit钩子

项目已配置pre-commit钩子，会在提交时自动运行：
- ✅ Black代码格式化
- ✅ isort导入排序
- ✅ flake8代码检查
- ⚠️ mypy类型检查(有错误但不阻塞)

如果pre-commit失败，请修复问题后重新提交。

---

## 📊 质量标准

### 🎯 代码覆盖率目标
- **当前**: 32%
- **短期目标**: 50%
- **长期目标**: 80%

### 📏 代码质量指标
- **测试通过率**: 100% (必须)
- **代码格式化**: 100%合规 (必须)
- **类型检查**: 逐步减少错误
- **文档覆盖率**: 每个公共方法都有文档字符串

---

## 🧪 测试策略

### 📋 测试原则
1. **测试驱动开发**: 新功能先写测试
2. **回归测试**: 修复bug时添加对应测试
3. **集成测试**: 确保模块间协作正常
4. **边界测试**: 测试异常情况和边界条件

### 🔧 测试工具使用
```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_culture_enforcer.py

# 运行测试并生成覆盖率报告
pytest --cov=aiculture --cov-report=html

# 运行测试并显示详细输出
pytest -v --tb=short
```

---

## 🏗️ 代码结构规范

### 📁 模块组织
- **核心功能**: `aiculture/core.py`
- **文化执行**: `aiculture/culture_enforcer.py`
- **环境检查**: `aiculture/environment_checker.py`
- **CLI接口**: `aiculture/cli.py`
- **测试代码**: `tests/`

### 📝 代码风格
- **行长度**: 最大88字符
- **导入顺序**: 标准库 → 第三方库 → 本地模块
- **命名规范**: 
  - 类名: PascalCase
  - 函数名: snake_case
  - 常量: UPPER_CASE

---

## 🔧 工具配置

### ⚙️ 开发环境设置
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install

# 更新pre-commit钩子
pre-commit autoupdate
```

### 📋 配置文件说明
- **pyproject.toml**: 项目配置和工具设置
- **.pre-commit-config.yaml**: Pre-commit钩子配置
- **.flake8**: 代码检查规则
- **pytest.ini**: 测试配置(在pyproject.toml中)

---

## 🚨 常见问题解决

### ❌ 测试失败
```bash
# 查看详细错误信息
pytest -v --tb=long

# 只运行失败的测试
pytest --lf

# 调试特定测试
pytest tests/test_xxx.py::test_function_name -s
```

### 🔧 格式化问题
```bash
# 自动修复格式化
black .
isort .

# 检查格式化状态
black --check .
isort --check-only .
```

### 📊 覆盖率下降
```bash
# 生成详细覆盖率报告
pytest --cov=aiculture --cov-report=html
# 查看 htmlcov/index.html

# 查找未覆盖的代码
pytest --cov=aiculture --cov-report=term-missing
```

---

## 📈 持续改进计划

### 🎯 短期目标 (1-2周)
- [ ] 修复所有mypy类型检查错误
- [ ] 提升代码覆盖率到50%
- [ ] 修复bandit安全检查配置
- [ ] 清理未使用的导入

### 🚀 中期目标 (1个月)
- [ ] 重构大文件(cli.py拆分)
- [ ] 完善文档字符串
- [ ] 添加性能测试
- [ ] 建立CI/CD流水线

### 🌟 长期目标 (3个月)
- [ ] 代码覆盖率达到80%
- [ ] 完整的类型注解
- [ ] 性能基准测试
- [ ] 自动化发布流程

---

## 💡 AI协作开发建议

### 🤖 与AI协作的最佳实践
1. **明确需求**: 给AI提供详细的上下文和要求
2. **增量开发**: 小步快跑，及时验证
3. **测试驱动**: 让AI先写测试，再写实现
4. **代码审查**: 仔细审查AI生成的代码
5. **文档同步**: 确保AI更新相关文档

### 📋 AI代码质量检查
- 运行所有测试确保功能正确
- 检查代码风格是否符合项目标准
- 验证类型注解的正确性
- 确保异常处理的完整性

---

## 🎉 成功指标

项目成功践行开发文化的标志：
- ✅ 所有测试持续通过
- ✅ 代码覆盖率稳步提升
- ✅ Pre-commit钩子正常工作
- ✅ 新功能都有对应测试
- ✅ 代码质量工具零错误
- ✅ 文档与代码同步更新

---

*让我们一起将AICultureKit打造成AI时代开发文化的典范！* 🚀
