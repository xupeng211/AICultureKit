# Problem Aggregator

前置问题聚合器，在提交前本地就给出"这次提交会被拦截的所有问题清单"。

## 🎯 目标

- **前置预防**: 在提交前就发现所有可能被拦截的问题
- **一次性聚合**: 避免多次循环修复，一次性看到所有问题
- **优先级排序**: 按严重程度排序：安全>行为违规>构建阻塞>质量>风格
- **可操作建议**: 每个问题都提供具体的修复建议

## 🚀 快速开始

### 基本用法

```bash
# 检查当前变更（相对于HEAD）
python -m tools.problem_aggregator.aggregator

# 检查相对于origin/main的变更
python -m tools.problem_aggregator.aggregator --base origin/main

# 生成详细报告
python -m tools.problem_aggregator.aggregator \
  --base origin/main \
  --out artifacts/problems.json \
  --md artifacts/problems_report.md

# 严格模式（有问题时返回非0退出码）
python -m tools.problem_aggregator.aggregator --strict
```

### 检查特定文件

```bash
# 只检查指定文件
python -m tools.problem_aggregator.aggregator --files file1.py file2.py

# 检查所有Python文件
python -m tools.problem_aggregator.aggregator --files *.py
```

## 📋 检查项目

### 1. 代码风格检查 (ruff/flake8)
- 语法错误
- 代码风格问题
- 导入排序
- 未使用的变量/导入

### 2. 安全检查 (bandit + detect-secrets)
- 硬编码密码/API密钥
- 不安全的函数调用
- SQL注入风险
- 其他安全漏洞

### 3. 测试检查 (pytest)
- 测试收集失败
- 测试运行失败
- 测试覆盖率不足
- 跳过的测试

### 4. 文化规则检查
- 调试print语句
- 跳过的测试
- TODO/FIXME注释
- 其他团队约定

## 📊 输出格式

### JSON输出 (`--out`)

```json
{
  "problems": [...],
  "categories": {
    "security": [...],
    "behavior_violations": [...],
    "build_blocking": [...],
    "quality": [...],
    "style": [...],
    "system": [...]
  },
  "summary": {
    "total": 10,
    "blocking": 2,
    "by_severity": {
      "error": 2,
      "warning": 6,
      "info": 2
    }
  },
  "metadata": {
    "base": "origin/main",
    "files_checked": 5,
    "strict_mode": false
  }
}
```

### Markdown输出 (`--md`)

生成人类可读的详细报告，包括：
- 问题摘要
- 按优先级分类的问题列表
- 修复建议
- 工具统计
- 热点文件分析

## ⚙️ 配置

### 配置文件位置

系统会按以下顺序查找配置文件：
1. `--config` 参数指定的文件
2. `tools/problem_aggregator/rulesets/culture.yml`
3. `.aiculture/config.yml`
4. `aiculture.yml`

### 配置示例

```yaml
culture:
  min_test_coverage: 80.0
  forbid_skipping_tests: true
  forbid_disabling_hooks: true
  forbid_debug_prints: true
  forbid_todo_fixme: false

quality:
  max_complexity: 10
  max_function_length: 50

security:
  forbid_hardcoded_passwords: true
  forbid_hardcoded_api_keys: true
```

## 🔧 集成

### VSCode任务

在 `.vscode/tasks.json` 中添加：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "AICultureKit: Aggregate Problems",
      "type": "shell",
      "command": "python -m tools.problem_aggregator.aggregator --base origin/main --out artifacts/problems.json --md artifacts/problems_report.md",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      },
      "problemMatcher": []
    }
  ]
}
```

### Git钩子集成

在 `pre-commit` 钩子中：

```bash
#!/bin/bash
# 运行问题聚合检查
python -m tools.problem_aggregator.aggregator --strict
if [ $? -ne 0 ]; then
    echo "❌ 发现阻塞性问题，请查看报告并修复"
    python -m tools.problem_aggregator.aggregator --md artifacts/problems_report.md
    echo "📋 详细报告: artifacts/problems_report.md"
    exit 1
fi
```

### CI/CD集成

```yaml
# GitHub Actions示例
- name: Run Problem Aggregator
  run: |
    python -m tools.problem_aggregator.aggregator \
      --base origin/main \
      --out artifacts/problems.json \
      --md artifacts/problems_report.md \
      --strict

- name: Upload Problem Report
  uses: actions/upload-artifact@v3
  if: failure()
  with:
    name: problem-report
    path: artifacts/
```

## 🛠️ 开发

### 添加新的检查器

1. 在 `adapters/` 目录下创建新的适配器
2. 实现检查逻辑，返回标准格式的问题列表
3. 在 `aggregator.py` 中集成新的适配器

### 问题格式

每个问题应该包含以下字段：

```python
{
    'tool': 'tool_name',           # 工具名称
    'type': 'problem_type',        # 问题类型
    'severity': 'error|warning|info',  # 严重程度
    'file': 'path/to/file.py',     # 文件路径（可选）
    'line': 42,                    # 行号（可选）
    'column': 10,                  # 列号（可选）
    'code': 'ERROR_CODE',          # 错误码（可选）
    'message': 'Problem description',  # 问题描述
    'fix_suggestion': 'How to fix',    # 修复建议
    'blocking': True|False,        # 是否阻塞
    'metadata': {...}              # 额外信息（可选）
}
```

## 📈 最佳实践

1. **定期运行**: 在每次提交前运行检查
2. **渐进修复**: 优先修复阻塞性问题
3. **配置调优**: 根据团队需求调整配置
4. **持续改进**: 根据反馈优化检查规则

## 🔍 故障排除

### 常见问题

**Q: 检查超时怎么办？**
A: 可以通过配置文件调整超时时间，或者使用 `--files` 参数只检查变更的文件。

**Q: 误报太多怎么办？**
A: 调整配置文件中的规则，或者在代码中添加忽略注释。

**Q: 工具未安装怎么办？**
A: 系统会自动跳过未安装的工具，但建议安装所有依赖工具以获得完整检查。

### 依赖工具

确保安装以下工具：

```bash
pip install ruff black isort pytest pytest-cov bandit detect-secrets
```
