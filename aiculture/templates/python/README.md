# {{project_name}}

{{project_description}}

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Git

### 安装

1. **克隆项目**
```bash
git clone https://github.com/{{github_username}}/{{project_name}}.git
cd {{project_name}}
```

2. **创建虚拟环境** (必须)
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -e ".[dev]"
```

4. **验证安装**
```bash
{{project_name}} --help
```

## 🛠️ 开发指南

### 开发环境设置

```bash
# 安装开发依赖
pip install -e ".[dev,test,docs]"

# 安装pre-commit钩子
pre-commit install

# 运行测试
pytest

# 检查代码质量
black . --check
isort . --check-only
flake8 .
mypy {{package_name}}
```

### 项目结构

```
{{project_name}}/
├── {{package_name}}/          # 主要源代码
│   ├── __init__.py
│   ├── cli.py                 # 命令行接口
│   ├── core.py                # 核心功能
│   └── utils.py               # 工具函数
├── tests/                     # 测试代码
│   ├── __init__.py
│   ├── test_core.py
│   └── test_cli.py
├── docs/                      # 文档
├── .github/                   # GitHub工作流
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── pyproject.toml             # 项目配置
├── requirements.txt           # 生产依赖
├── requirements-dev.txt       # 开发依赖
├── .gitignore
├── .env.example               # 环境变量示例
└── README.md
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_core.py

# 生成覆盖率报告
pytest --cov={{package_name}} --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

## 📦 构建和发布

```bash
# 构建包
python -m build

# 发布到PyPI (需要配置token)
python -m twine upload dist/*
```

## 🔧 代码质量工具

本项目使用以下工具确保代码质量：

- **Black**: 代码格式化
- **isort**: import排序
- **flake8**: 代码风格检查
- **mypy**: 类型检查
- **pytest**: 单元测试
- **bandit**: 安全扫描
- **pre-commit**: Git钩子

### 运行所有检查

```bash
# 格式化代码
black .
isort .

# 检查代码质量
flake8 .
mypy {{package_name}}
bandit -r {{package_name}}

# 运行测试
pytest --cov={{package_name}}
```

## 🚀 部署

### 使用Docker

```bash
# 构建镜像
docker build -t {{project_name}} .

# 运行容器
docker run -p 8000:8000 {{project_name}}
```

### 环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

主要环境变量：
- `ENVIRONMENT`: 运行环境 (development/production)
- `LOG_LEVEL`: 日志级别 (DEBUG/INFO/WARNING/ERROR)
- `DATABASE_URL`: 数据库连接字符串 (如适用)

## 📚 API文档

API文档自动生成并部署到: https://{{github_username}}.github.io/{{project_name}}

本地查看文档：
```bash
mkdocs serve
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 贡献要求

- 所有测试必须通过
- 代码覆盖率不低于80%
- 遵循项目代码风格
- 添加适当的文档和注释

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 感谢所有贡献者
- 基于 [AICultureKit](https://github.com/your-org/AICultureKit) 最佳实践 