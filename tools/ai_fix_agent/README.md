# AI Fix Agent

AI生成可审阅的修复补丁，不直接修改仓库。

## 🎯 设计理念

- **安全第一**: AI不直接修改代码，而是生成补丁供人工审查
- **分类修复**: 按问题类型生成独立的小补丁（≤200行）
- **可回滚**: 所有修复都可以干净地应用和回滚
- **置信度控制**: 只生成高置信度的补丁，低置信度问题提供手工指南

## 🚀 快速开始

### 基本用法

```bash
# 1. 先运行问题聚合
python -m tools.problem_aggregator.aggregator --out artifacts/problems.json

# 2. 生成AI修复补丁
python -m tools.ai_fix_agent.agent --in artifacts/problems.json --out artifacts/ai_fixes

# 3. 查看生成的补丁
ls -la artifacts/ai_fixes/
```

### 应用补丁

```bash
# 进入输出目录
cd artifacts/ai_fixes/

# 查看变更日志
cat CHANGELOG_ENTRY.md

# 自动应用所有补丁（推荐）
./apply_fixes.sh

# 或手动应用单个补丁
git apply lint_fix.patch --index
git apply security_fix.patch --index
```

## 📋 支持的修复类型

### 1. Lint修复 (`lint_fix.patch`)

**可修复的问题**:
- `F401`: 未使用的导入
- `F841`: 未使用的变量
- `W291`: 行尾空白
- `W292`: 文件末尾缺少换行
- `I001`: 导入排序
- `E302`: 函数间缺少空行
- `E303`: 过多空行
- `E231`: 逗号后缺少空格
- `E225`: 操作符周围缺少空格

**置信度**: 70-90%

### 2. 安全修复 (`security_fix.patch`)

**可修复的问题**:
- `B101`: assert语句 → 异常检查
- `B102`: exec使用 → 添加安全警告
- `B108`: 不安全临时文件 → 使用mkstemp
- `B311`: 不安全随机数 → 建议使用secrets
- `B324`: 不安全哈希 → 建议使用SHA-256
- `B501`: 未验证SSL → 添加警告注释
- `B601/B602`: shell注入 → 添加验证提醒

**置信度**: 60%（需要人工审查）

### 3. 测试脚手架 (`test_scaffold.patch`)

**功能**:
- 为低覆盖率文件生成测试模板
- 自动识别类和函数
- 生成基础测试结构
- 包含TODO提醒

**置信度**: 80%

## 🔧 修复策略

### 高置信度修复（自动生成补丁）

- **Lint问题**: 语法和格式问题，修复逻辑明确
- **简单安全问题**: 添加警告注释，不改变逻辑
- **测试脚手架**: 生成标准模板

### 低置信度修复（生成手工指南）

- **复杂安全问题**: 需要业务逻辑理解
- **密钥泄漏**: 需要人工判断真假
- **复杂重构**: 涉及架构变更

## 📊 输出文件说明

### 补丁文件
- `lint_fix.patch`: Lint问题修复
- `security_fix.patch`: 安全问题修复
- `test_scaffold.patch`: 测试脚手架生成

### 说明文件
- `lint_explanation.md`: Lint修复详细说明
- `security_explanation.md`: 安全修复详细说明
- `test_scaffold_explanation.md`: 测试脚手架说明

### 手工指南
- `security_manual_guide.md`: 无法自动修复的安全问题指南
- `test_scaffold_manual_guide.md`: 测试改进TODO清单

### 元数据文件
- `CHANGELOG_ENTRY.md`: 完整的变更日志和应用指南
- `apply_fixes.sh`: 自动应用脚本

## 🛡️ 安全保障

### 应用前检查

```bash
# 1. 检查补丁内容
cat artifacts/ai_fixes/lint_fix.patch

# 2. 验证补丁可应用
git apply --check artifacts/ai_fixes/lint_fix.patch

# 3. 查看影响范围
git apply --stat artifacts/ai_fixes/lint_fix.patch
```

### 备份和回滚

```bash
# 创建备份分支
git branch backup-$(date +%Y%m%d-%H%M%S)

# 应用补丁
git apply artifacts/ai_fixes/lint_fix.patch --index

# 如果有问题，立即回滚
git reset --hard HEAD~1
```

### 分步验证

```bash
# 1. 应用单个补丁
git apply lint_fix.patch --index

# 2. 运行测试
pytest

# 3. 检查问题是否解决
python -m tools.problem_aggregator.aggregator

# 4. 提交这个修复
git commit -m "fix: apply lint fixes"

# 5. 继续下一个补丁
git apply security_fix.patch --index
```

## 🔍 故障排除

### 补丁应用失败

```bash
# 查看冲突详情
git apply --reject artifacts/ai_fixes/lint_fix.patch

# 手动合并冲突文件
# 编辑 *.rej 文件，手动应用更改

# 清理拒绝文件
find . -name "*.rej" -delete
```

### 修复效果验证

```bash
# 重新运行问题检查
python -m tools.problem_aggregator.aggregator --out artifacts/post_fix_problems.json

# 比较修复前后
diff artifacts/problems.json artifacts/post_fix_problems.json
```

### 性能优化

```bash
# 只修复特定类型的问题
python -m tools.ai_fix_agent.agent \
  --in artifacts/problems.json \
  --out artifacts/ai_fixes \
  --strategy lint  # 只生成lint修复
```

## 🧪 开发和扩展

### 添加新的修复策略

1. 在 `strategies/` 目录创建新策略文件
2. 实现 `can_fix()` 和 `generate_fix()` 方法
3. 在 `agent.py` 中注册新策略

### 策略接口

```python
class MyFixStrategy:
    def can_fix(self, problem: Dict[str, Any]) -> bool:
        """判断是否可以修复此问题"""
        pass

    def generate_fix(self, problems: List[Dict[str, Any]]) -> Tuple[str, str, float]:
        """生成修复补丁

        Returns:
            (patch_content, explanation, confidence)
        """
        pass
```

## 📈 最佳实践

1. **小步快跑**: 逐个应用补丁，不要批量应用
2. **充分测试**: 每个补丁应用后都要运行测试
3. **代码审查**: 所有AI生成的代码都需要人工审查
4. **备份优先**: 始终在应用补丁前创建备份
5. **渐进修复**: 优先修复高置信度的问题

## 🔗 集成

### VSCode集成

在 `.vscode/tasks.json` 中添加：

```json
{
  "label": "AI Generate Fixes",
  "type": "shell",
  "command": "python -m tools.ai_fix_agent.agent --in artifacts/problems.json --out artifacts/ai_fixes",
  "group": "build"
}
```

### CI/CD集成

```yaml
- name: Generate AI Fixes
  run: |
    python -m tools.problem_aggregator.aggregator --out artifacts/problems.json
    python -m tools.ai_fix_agent.agent --in artifacts/problems.json --out artifacts/ai_fixes

- name: Upload Fixes
  uses: actions/upload-artifact@v3
  with:
    name: ai-fixes
    path: artifacts/ai_fixes/
```
