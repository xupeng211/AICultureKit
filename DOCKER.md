# 🐳 Docker 容器化部署指南

AICultureKit 支持完整的 Docker 容器化部署，提供多种服务配置以满足不同使用场景。

## 🚀 快速开始

### 构建镜像

```bash
# 构建基础镜像
docker build -t aiculture-kit .

# 或使用 docker-compose 构建
docker-compose build
```

### 运行容器

```bash
# 基础运行（显示帮助信息）
docker run --rm aiculture-kit

# 交互式运行
docker run -it --rm aiculture-kit /bin/bash

# 挂载项目目录运行
docker run -it --rm -v $(pwd):/workspace aiculture-kit
```

## 🔧 Docker Compose 服务

项目提供了多个预配置的服务：

### 主要服务

```bash
# 启动主服务
docker-compose up aiculture-kit

# 开发环境
docker-compose up dev

# 运行测试
docker-compose up test

# 启动文档服务
docker-compose up docs
```

### 服务说明

| 服务名 | 端口 | 用途 | 命令 |
|--------|------|------|------|
| `aiculture-kit` | 8000 | 主应用服务 | `aiculture --help` |
| `dev` | - | 开发环境 | `tail -f /dev/null` |
| `test` | - | 测试运行 | `pytest --cov=aiculture --cov-report=html` |
| `docs` | 8080 | 文档服务 | `python -m http.server 8080` |

## 🛠️ 技术规格

### 基础镜像

- **Python 版本**: 3.11-slim
- **基础系统**: Debian Linux
- **包管理**: pip

### 系统依赖

- `git` - 版本控制支持
- `build-essential` - 编译工具链

### Python 依赖

- 生产依赖: `requirements.txt`
- 开发依赖: `requirements-dev.txt`

### 容器特性

- ✅ 非 root 用户运行（用户: `aiculture`）
- ✅ 健康检查支持
- ✅ 环境变量配置
- ✅ 数据卷挂载支持
- ✅ 网络隔离

## 🔍 使用示例

### 1. 项目质量检查

```bash
# 在容器中检查当前项目
docker run --rm -v $(pwd):/workspace -w /workspace aiculture-kit \
  aiculture quality check

# 使用 docker-compose
docker-compose run --rm aiculture-kit aiculture quality check
```

### 2. 创建新项目

```bash
# 创建新项目模板
docker run --rm -v $(pwd):/workspace -w /workspace aiculture-kit \
  aiculture project create my-project

# 交互式创建
docker run -it --rm -v $(pwd):/workspace -w /workspace aiculture-kit \
  aiculture template create
```

### 3. 开发环境

```bash
# 启动开发容器
docker-compose up -d dev

# 进入开发容器
docker-compose exec dev /bin/bash

# 在容器中开发
aiculture culture check
aiculture quality analyze
```

### 4. 持续集成

```bash
# CI/CD 中的测试运行
docker-compose run --rm test

# 生成覆盖率报告
docker-compose run --rm -v $(pwd)/htmlcov:/app/htmlcov test
```

## 🌐 网络和存储

### 网络配置

项目使用自定义网络 `aiculture-network`，所有服务可以相互通信：

```yaml
networks:
  aiculture-network:
    driver: bridge
```

### 数据卷

- **代码挂载**: `.:/app` - 开发时代码同步
- **Docker socket**: `/var/run/docker.sock` - Docker-in-Docker 支持
- **输出目录**: 覆盖率报告、日志等可挂载到主机

## 🚨 故障排除

### 常见问题

**Q: Docker 构建失败 "Python version mismatch"**

```
A: 确保 Dockerfile 使用 Python 3.11-slim，与 pyproject.toml 要求一致
```

**Q: 权限问题**

```
A: 容器以非 root 用户运行，确保挂载目录有正确权限
```

**Q: 依赖安装失败**

```
A: 检查网络连接，或使用 --no-cache 重新构建
```

### 调试命令

```bash
# 查看构建过程
docker build --no-cache --progress=plain -t aiculture-kit .

# 检查容器状态
docker-compose ps

# 查看服务日志
docker-compose logs aiculture-kit

# 进入运行中的容器
docker-compose exec aiculture-kit /bin/bash
```

## 🔄 CI/CD 集成

Docker 镜像可以集成到各种 CI/CD 流水线中：

```yaml
# GitHub Actions 示例
- name: Build and test with Docker
  run: |
    docker build -t aiculture-kit .
    docker run --rm aiculture-kit aiculture --version
    docker-compose run --rm test
```

## 📚 更多资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [项目主文档](README.md)
- [开发者指南](docs/DEVELOPER_GUIDE.md)
