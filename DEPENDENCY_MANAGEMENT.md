# 📦 AICultureKit 依赖管理指南

## 🎯 依赖管理策略

AICultureKit 使用现代化的依赖管理方式，优先使用 `pyproject.toml` 作为依赖定义的单一来源。

## 📁 文件说明

### 主要文件

- **`pyproject.toml`** - 主要的项目配置文件，包含所有依赖定义
- **`requirements.txt`** - 生产依赖（向后兼容）
- **`requirements-dev.txt`** - 开发依赖（向后兼容）
- **`requirements.lock`** - 锁定的完整环境快照

### 文件关系

```
pyproject.toml (主要)
├── [project.dependencies] → requirements.txt
└── [project.optional-dependencies.dev] → requirements-dev.txt
```

## 🚀 推荐的安装方式

### 生产环境

```bash
# 推荐方式（使用 pyproject.toml）
pip install -e .

# 或者使用传统方式
pip install -r requirements.txt
```

### 开发环境

```bash
# 推荐方式（安装开发依赖）
pip install -e ".[dev]"

# 或者使用传统方式
pip install -r requirements-dev.txt
```

### 完整开发环境设置

```bash
# 1. 创建虚拟环境
python -m venv aiculture-env
source aiculture-env/bin/activate  # Linux/Mac
# 或 aiculture-env\Scripts\activate  # Windows

# 2. 升级pip
pip install --upgrade pip

# 3. 安装开发依赖
pip install -e ".[dev]"

# 4. 安装pre-commit钩子
pre-commit install

# 5. 验证安装
aiculture --version
pytest --version
```

## 🔒 依赖锁定

### 生成锁定文件

```bash
# 生成当前环境的完整依赖快照
pip freeze > requirements.lock
```

### 使用锁定文件

```bash
# 在CI/CD或生产环境中使用精确版本
pip install -r requirements.lock
```

## 📋 依赖分类

### 生产依赖 (pyproject.toml)

```toml
dependencies = [
    "click>=8.0.0",        # CLI框架
    "jinja2>=3.0.0",       # 模板引擎
    "pyyaml>=6.0.0",       # YAML处理
    "gitpython>=3.1.0",    # Git操作
    "cookiecutter>=2.1.0", # 项目模板
]
```

### 开发依赖 (pyproject.toml)

```toml
[project.optional-dependencies]
dev = [
    "black>=22.0.0",       # 代码格式化
    "isort>=5.0.0",        # 导入排序
    "flake8>=4.0.0",       # 代码检查
    "mypy>=0.991",         # 类型检查
    "pytest>=7.0.0",       # 测试框架
    "pytest-cov>=4.0.0",   # 测试覆盖率
    "pre-commit>=2.20.0",   # Git钩子
]
```

### 额外开发工具 (requirements-dev.txt)

```
bandit>=1.7.0      # 安全检查
safety>=2.3.0      # 依赖安全扫描
pip-audit>=2.6.0   # 依赖漏洞检查
```

## 🔄 依赖更新流程

### 1. 更新依赖版本

```bash
# 检查过时的依赖
pip list --outdated

# 更新特定依赖
pip install --upgrade package_name

# 更新所有依赖（谨慎使用）
pip install --upgrade -r requirements-dev.txt
```

### 2. 测试兼容性

```bash
# 运行测试确保兼容性
pytest

# 运行代码质量检查
black --check .
flake8 .
mypy .
```

### 3. 更新配置文件

1. 更新 `pyproject.toml` 中的版本要求
2. 同步更新 `requirements.txt` 和 `requirements-dev.txt`
3. 重新生成 `requirements.lock`

### 4. 提交更改

```bash
git add pyproject.toml requirements*.txt requirements.lock
git commit -m "deps: update dependencies to latest versions"
```

## 🛡️ 安全最佳实践

### 定期安全检查

```bash
# 检查已知漏洞
safety check

# 审计依赖
pip-audit

# 安全代码扫描
bandit -r aiculture/
```

### 依赖固定策略

- **生产依赖**: 使用 `>=` 允许补丁更新
- **开发依赖**: 使用 `>=` 保持工具最新
- **CI/CD**: 使用 `requirements.lock` 确保一致性

## 🚨 故障排除

### 常见问题

1. **依赖冲突**
   ```bash
   pip install --force-reinstall -r requirements-dev.txt
   ```

2. **版本不兼容**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

3. **缓存问题**
   ```bash
   pip cache purge
   pip install --no-cache-dir -r requirements-dev.txt
   ```

### 清理环境

```bash
# 完全重建环境
deactivate
rm -rf aiculture-env
python -m venv aiculture-env
source aiculture-env/bin/activate
pip install -e ".[dev]"
```

## 📊 依赖监控

### CI/CD 检查

- 自动化依赖安全扫描
- 定期依赖更新检查
- 兼容性测试矩阵

### 工具推荐

- **Dependabot**: 自动依赖更新PR
- **Safety**: 安全漏洞检查
- **pip-audit**: 依赖审计
- **pip-tools**: 依赖管理工具

---

**维护者**: AICultureKit 团队  
**最后更新**: 2024年8月  
**版本**: 1.0
