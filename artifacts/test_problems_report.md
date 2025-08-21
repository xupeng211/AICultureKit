# 🔍 AICultureKit 问题聚合报告

**生成时间**: 2025-08-21 01:30:37
**检查基准**: HEAD
**检查文件**: 1
**严格模式**: 否

## 📊 问题摘要

- **总计**: 2 个问题
- **阻塞性**: 1 个
- **错误**: 1 个
- **警告**: 1 个
- **信息**: 0 个

## 🛑 构建阻塞

1. ❌ 🚫 [pytest]  测试收集失败:
   💡 **修复建议**: 检查测试文件语法和导入


## ⚙️ 系统问题

1. ⚠️ [coverage]  无法获取覆盖率信息
   💡 **修复建议**: 确保安装了pytest-cov插件


## 🎯 修复建议

### ⚡ 立即处理 (1 个阻塞性问题)

1. **N/A:0** - 测试收集失败:
   💡 检查测试文件语法和导入

### 📈 按工具统计

- **pytest**: 1 个问题 (1 个阻塞)
- **coverage**: 1 个问题 (0 个阻塞)

## 🚀 建议的下一步行动

1. **立即修复阻塞性问题** - 这些问题会阻止代码提交
2. **修复 1 个错误** - 这些是严重问题
3. **处理 1 个警告** - 提升代码质量
4. **运行自动修复工具** - 使用 `black`, `isort`, `ruff --fix` 等
5. **重新运行检查** - 确认问题已解决

## 🛠️ 有用的命令

```bash
# 自动修复代码格式
python -m black .
python -m isort .
python -m ruff check --fix .

# 运行测试和覆盖率
python -m pytest --cov=aiculture --cov-report=term-missing

# 重新运行问题聚合
python -m tools.problem_aggregator.aggregator --md artifacts/problems_report.md
```
