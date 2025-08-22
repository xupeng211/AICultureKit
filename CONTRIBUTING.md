# 贡献指南（Contributing）

## 1. 开发五原则（避免阻塞）

* **本地轻**：本地仅运行 black / ruff(E,F,I,UP,B) / ruff-format / isort（自动修复）
* **CI 严**：安全/隐私/全量规则、覆盖率、类型检查放到 CI
* **分支短**：单一主题，≤300 行，≤48h
* **阈值阶梯**：覆盖率与规则逐步收紧（25% → 40% → 60% → 80%）
* **可回滚**：快照分支/Feature Flag/灰度，必要时可revert

## 2. 工作流（SOP）

1. 新建分支：`feat/<ticket>` 或 `fix/<issue>`
2. 编码前：若涉及行为变更，先加 **Feature Flag**（默认 off）
3. 提交前：

```bash
pre-commit run --all-files
pytest -q -k "not slow"
```

1. 提交 PR（小而快）：

   * 模板项需填写：变更点 / 风险与回滚 / 测试点 / PII 涉及
2. 合并后：

   * 先灰度/小流量，观察指标
   * 无异常再全量开启；删除临时降阈值配置，抬升下一档

## 3. 代码规范与工具

* **Formatting**：black、ruff-format、isort
* **Lint**：ruff（本地仅 E,F,I,UP,B；CI 全量）
* **Testing**：pytest + coverage
* **Coverage**：分支临时阈值起步 25%，逐步提升到 80%
* **Security/Secrets**：bandit/detect-secrets（CI 阶段）
* **PII 误报**：编辑 `.piiignore`，只对白名单上下文放行

## 4. 提交信息规范

* `feat: xxx` / `fix: xxx` / `chore: xxx` / `docs: xxx` / `test: xxx`
* 避免超长标题；正文列“变更动机/影响范围/回滚方式”

## 5. PR 审核要点

* 单一职责、小而清晰
* 有最小可行测试（MST）
* 有回滚策略与灰度开关
* 无明文密钥与敏感信息

---

## 6. 钩子与门控（Hooks & Gating）

* 仓库已统一使用自定义钩子目录：`.githooks`（本地执行：`git config core.hooksPath .githooks`）
* 本地仅运行轻量检查（black / ruff --fix / ruff-format / isort；pre-push 跑快速测试集）
* 文化/AI 规则采用门控变量：`AICULTURE_ENFORCE_BLOCKING=warn|block|off`
  * 默认：feature/chore 等开发分支 `warn`
  * 主线：`main`、`release/*` 在 CI 中注入 `block`
* CI 仍承担严格门禁（全量 Ruff、Bandit、detect-secrets、mypy、pytest --cov 阈值阶梯）
