# Git 提交规范

## 分支策略
- `main` → 稳定版本
- `dev` → 开发分支
- `feature/*` → 新功能
- `fix/*` → bug 修复

## 提交信息格式
遵循 [Conventional Commits](https://www.conventionalcommits.org)：
- `feat:` 新功能
- `fix:` 修复 bug
- `chore:` 杂项（脚本、依赖更新）
- `docs:` 文档更新
- `refactor:` 重构
- `test:` 测试相关

示例：
```
feat(data): 新增比赛数据清洗逻辑
fix(model): 修复预测结果概率计算错误
```

## 代码推送
- 所有推送必须走 `make prepush`。
- CI 未通过时禁止推送。 