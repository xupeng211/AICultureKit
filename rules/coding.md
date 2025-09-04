# 代码风格与架构规范

## 命名规范
- Python 使用 `snake_case`，类名用 `PascalCase`。
- 常量用 `UPPER_CASE`。
- 文件/目录名用小写字母 + `_`。

## 目录结构
- `src/` → 核心代码
- `tests/` → 测试
- `scripts/` → 脚本工具
- `configs/` → 配置文件

## 开发规范
- 修改优先：在已有文件内修改，而不是随意新建文件。
- 模块化：每个文件功能单一，不要写"巨石文件"。
- 注释：
  - 复杂逻辑必须有注释。
  - 公共方法必须有 docstring。

## 依赖管理
- 所有依赖必须写入 `requirements.txt`。
- 不允许在本地随意 pip install 未记录的库。 