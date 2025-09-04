# CI/CD 校验规则

## 校验内容
1. **环境**  
   - 使用 Python 3.11
   - 依赖由 `requirements.txt` 管理

2. **代码质量**  
   - `ruff check` 必须通过
   - `ruff format` 必须无格式差异

3. **测试**  
   - `pytest` 必须全绿
   - 覆盖率 ≥ 80%

4. **安全**  
   - 禁止提交明文密码/密钥
   - 配置文件需支持 `.env`

## 流程
- 本地：开发者通过 `make prepush` 模拟 CI
- 远程：推送后触发 GitHub Actions / Gitee CI
- 如果 CI 红灯 → 必须修复，禁止跳过

## 提示
CI 环境和本地环境必须保持一致（使用 Docker + Makefile）。 