# CI/CD 最终验收报告（Baseline）

> **仓库**：`AICultureKit`  
> **报告版本**：v1.0（基线）  
> **目标**：固化当前"先跑通再优化"的 CI/CD 策略，并提供可操作的回归验收清单与升级路径。

## 1. 总览（结论）
- **Quick Check（feature push）**：仅做**语法编译检查**+ Ruff（软失败），**不安装依赖，不导入包** → ✅ 通过即允许继续开发。
- **Quality Gate（PR → main）**：**唯一硬门禁**为 `pytest + 覆盖率阈值`（当前阈值：**0%~9%**，以工作流为准）；其他检查（ruff/mypy/bandit/detect-secrets）均为**软失败**。  
- **Docker Build（发布构建）**：**仅**在 `push: main` 或 `tags` 时触发，不与 PR/feature 冲突。
- **分支保护**：已启用 *Require a pull request before merging*、*Require status checks to pass*（只勾选 **Quality Gate**）、*Require branches to be up to date*、*Require conversation resolution*、*Do not allow bypassing the above settings*。

## 2. 工作流矩阵（应触发什么）
| 事件 | Quick Check | Quality Gate | Docker Build |
|---|---|---|---|
| push 到非 main | ✅（仅语法编译+Ruff 软失败） | ❌ | ❌ |
| 打开/更新 PR → main | ❌ | ✅（pytest + coverage 阈值） | ❌ |
| push 到 main | ❌ | ❌ | ✅ |
| push tag（如 v1.0.0） | ❌ | ❌ | ✅ |

> 参考文件：  
> - `.github/workflows/quick-check.yml`  
> - `.github/workflows/quality-gate.yml`  
> - `.github/workflows/docker-build.yml`

## 3. 当前阈值与策略
- **覆盖率阈值**（Quality Gate 内控制）：**0% ~ 9%**（按工作流中 `--cov-fail-under`/env 生效值为准）。
- **阻断项**：仅 `pytest + coverage`。  
- **软失败项**：ruff、mypy、bandit、detect-secrets（使用 `continue-on-error` 或 `|| true`）。

## 4. 分支保护（截图与勾选项）
建议在 `Settings → Branches → main` 下勾选：
- ✅ Require a pull request before merging  
- ✅ Dismiss stale pull request approvals when new commits are pushed  
- ✅ Require status checks to pass before merging → **Quality Gate**（唯一必选）  
- ✅ Require branches to be up to date before merging  
- ✅ Require conversation resolution before merging  
- ✅ Do not allow bypassing the above settings

> 分支保护配置截图：  
> ![branch-protection-1](./_images/branch-protection-1.png)
> ![branch-protection-2](./_images/branch-protection-2.png)

## 5. 验收流程（每次变更或回归）
**A. Feature push（预期）**  
- 仅跑 **Quick Check**；应 1~2 分钟内完成；失败仅因语法错误。

**B. PR → main（强约束）**  
- 仅跑 **Quality Gate**；观察 `Test with coverage (BLOCKING)` 是否绿；其它检查允许黄/红但不阻断。  
- PR 页面应显示 **可合并**。

**C. main 发布构建**  
- 合并到 `main` 后，**仅**触发 **Docker Build & Publish**；构建通过后可在 `ghcr.io/xupeng211/...` 拉取镜像（如已配置）。

## 6. 已知隔离策略
- `tests/conftest.py` + `tests/_ci_quarantine.txt` 用于 **临时隔离不稳定/未就绪用例**（如依赖 `git` 或外部资源）。  
- 原则：**先合并、后剥离隔离**，小步快跑逐步修复并移出隔离清单。

## 7. 常见失败与排查
- **Quick Check 红**：通常是语法错误或 Ruff 报告。先本地 `python -m compileall aiculture` 与 `python -m ruff format/check`。  
- **Quality Gate 红**：先看 `pytest` 日志与 `--cov-fail-under` 值，必要时暂时降低阈值，优先保障流程通畅。  
- **重复触发**：确认三条工作流触发条件是否互斥（见第 2 节表格）。

### 🚨 紧急回滚策略
- **软失败开关**：在 Quality Gate 中设置 `continue-on-error: true` 临时跳过非阻断检查
- **降低阈值**：修改工作流中 `COVERAGE_THRESHOLD_MIN` 环境变量（如从9%降到0%）
- **隔离测试**：将不稳定用例添加到 `tests/_ci_quarantine.txt`
- **分支保护调整**：临时在 GitHub Settings 中移除 Quality Gate 要求（仅紧急情况）

## 8. 升级路线（推荐节奏）
1. 阶段 0（当前）——覆盖率 0%~9%，**先跑通**  
2. 阶段 1——提升至 12% / 15%，修少量"便宜"测试  
3. 阶段 2——提升至 25%+；必要时将 Ruff 升为部分硬门禁  
4. 阶段 3——收敛软失败项，逐步转硬阻断（mypy / bandit）

### 📋 变更流程
每次调整阈值或策略时：
1. 更新本文档第3节（当前阈值）和第8节（升级计划）
2. 通过 PR 提交变更，确保留痕和评审
3. 在 PR 描述中说明变更原因和预期影响
4. 合并后在第10节记录变更历史

## 9. 一键自检（可选）
如仓库已包含脚本：  
```bash
chmod +x scripts/verify_ci_post_merge.sh
./scripts/verify_ci_post_merge.sh   # 返回 0 表示通过
```

## 10. 变更记录

* 2024-08-24  初始化基线文档（CI/CD 策略固化；单一硬门禁=pytest+coverage；三工作流分工明确；嵌入分支保护截图引用；建立紧急回滚和变更流程） 