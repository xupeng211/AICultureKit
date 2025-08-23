# CI/CD 使用说明（SOP）

> 适用于本仓库当前已落地的三条工作流：**Quick Check**、**Quality Gate**、**Docker Build & Publish**。  
> 分支保护已启用：仅 **Quality Gate** 为 Required，PR → main 需绿灯方可合并。

---

## 0. 快速结论（给未来的你）
- **开发分支 push**：只触发 **Quick Check**（编译级语法 + Ruff 软失败），不安装依赖，秒级反馈。
- **发起 PR → main**：只触发 **Quality Gate**（pytest + 覆盖率阈值=0%/9% 由工作流控制），Ruff/MyPy/Bandit/Detect-secrets 全部软失败，不阻断。
- **合并到 main / 打 tag**：仅在代码变更或打 tag 时触发 **Docker Build & Publish**；文档改动不会触发镜像构建。

---

## 1. 工作流矩阵

| 工作流 | 触发条件 | 作用 | 阻断策略 |
|---|---|---|---|
| 🚀 Quick Check | `push` 到非 `main` | 编译级语法检查 + Ruff（软） | **不阻断** |
| 🛡️ Quality Gate | `pull_request` → `main` | pytest + 覆盖率（阈值由工作流控制），其余检查软失败 | **仅 pytest+cov 阻断** |
| 🐳 Docker Build & Publish | `push` 到 `main`（代码改动）/ 打 `tag` | 构建并推送镜像到 GHCR | 与合并解耦，不在 PR 上阻断 |

> 触发范围已加 `paths-ignore` 和并发控制，避免文档改动或重复运行造成噪音。

---

## 2. 日常开发流程（开发者视角）

1. 新建分支：`feature/<your-task>`  
2. 开发并提交；**push** 后会自动跑 **Quick Check**（不需要安装依赖，无第三方导入）。  
3. 创建 PR → `main`：自动跑 **Quality Gate**。  
   - ✅ `pytest (+coverage)` 通过 → 可合并  
   - 🟡 `Ruff/MyPy/Bandit/Detect-secrets` 仅提示，不阻断  
4. 合并 PR：**不会**触发 Docker（文档改动）  
5. 发布：当你在 `main` 打 `tag`（如 `v0.2.0`）时，触发 **Docker Build & Publish**。

---

## 3. 覆盖率与阈值策略（只改这里即可）
- 覆盖率阈值完全由 **`.github/workflows/quality-gate.yml`** 控制：  
  - 当前为 **0%/9%**（以实际线上配置为准）  
- **升级策略建议**：  
  - 阶段 1：0% → 5%（验证 gate 稳定）  
  - 阶段 2：5% → 9%（当前基线）  
  - 阶段 3：9% → 15% / 25%（逐步提升）  
- 每次调整阈值：**只需改工作流中的阈值 + 更新本文第 3 节说明**，走一次 PR 留痕即可。

---

## 4. 隔离与稳定性
- `tests/conftest.py` + `tests/_ci_quarantine.txt` 实现了**隔离名单**机制：  
  - `-m "not quarantine"` 仅执行健康用例；疑难用例先放隔离，修复后移除，gate 即可持续绿灯。  
- `-p no:asyncio` 已在 gate 中禁用可能干扰的插件，保持稳定。

---

## 5. 分支保护（Branch Protection）
- 入口：`Settings` → `Branches` → main 规则  
- 只勾选 **Require status checks** → 选择 **Quality Gate** 为唯一 Required  
- 勾选 **Do not allow bypassing the above settings**  
- （可选）将两张截图放在 `docs/_images/`，并在文档里引用留痕。

---

## 6. Docker 发布（GHCR）
- Secrets（已配置）：`REGISTRY=ghcr.io`、`REGISTRY_USERNAME`、`REGISTRY_PASSWORD`、`IMAGE_NAME`  
- main 有代码变更或打 tag → 自动构建并推送镜像到 GHCR  
- Tag 策略：`sha` + `latest`（main）、`v*`（tag）

---

## 7. 常见故障排查（Checklist）
- **PR 红灯**：  
  - 看 `Quality Gate` 的 **pytest** 步骤（唯一阻断项）  
  - 覆盖率未达：调低阈值或补充"便宜"测试  
- **Quick Check 红灯**：  
  - 仅 Ruff 或编译错误；Ruff 为软失败，不阻断（修复更好）  
- **Docker 构建慢/超时**：  
  - 文档改动不会触发；确保 main 触发时 runner 可用

---

## 8. 附：文件定位与改动范围
- 工作流：  
  - `.github/workflows/quick-check.yml`  
  - `.github/workflows/quality-gate.yml`  
  - `.github/workflows/docker-build.yml`
- 隔离清单：`tests/_ci_quarantine.txt`  
- 本文位置：`docs/CI_SOP.md`（阈值或策略变更只需改第 3 节）

> 如需自动化验收脚本，可使用 `scripts/verify_ci_post_merge.sh`（若存在）。

