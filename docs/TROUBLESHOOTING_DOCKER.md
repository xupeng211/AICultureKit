# 🐳 Docker CI/CD 故障排除指南

本文档提供了在自动集成部署过程中遇到 Docker 容器构建失败时的诊断和解决方案。

## 🚨 常见构建失败原因

### 1. Python 版本不匹配

**症状：**

```
ERROR: Package 'aiculture-kit' requires a different Python: 3.10.18 not in '>=3.11'
```

**原因：** Dockerfile 中的 Python 版本与 pyproject.toml 要求不匹配

**解决方案：**

```dockerfile
# 确保使用正确的 Python 版本
FROM python:3.11-slim  # 匹配 pyproject.toml 中的 requires-python = ">=3.11"
```

### 2. 依赖文件缺失

**症状：**

```
ERROR: failed to calculate checksum of ref: "/requirements.txt": not found
```

**原因：** .dockerignore 文件排除了必要的依赖文件

**解决方案：**

```dockerignore
# 确保不排除必要文件
*.txt
# 但保留依赖文件
!requirements.txt
!requirements-dev.txt
```

### 3. 构建上下文过大

**症状：**

```
transferring context: large-context-size MB
```

**原因：** .dockerignore 配置不当，包含了不必要的文件

**解决方案：**
优化 .dockerignore 文件，排除：

- .git 目录
- 虚拟环境目录 (venv/, .venv/)
- 缓存文件 (**pycache**/, *.pyc)
- 开发工具配置 (.vscode/, .idea/)
- 测试和构建输出 (htmlcov/, dist/, build/)

### 4. 多平台构建失败

**症状：**

```
ERROR: multiple platforms not supported
```

**解决方案：**

```yaml
- name: 🐳 Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
```

### 5. 权限问题

**症状：**

```
permission denied while trying to connect to the Docker daemon socket
```

**解决方案：**
在 GitHub Actions 中确保使用正确的权限：

```yaml
permissions:
  contents: read
  packages: write
```

## 🔍 诊断步骤

### 第一步：本地测试

```bash
# 1. 清理 Docker 缓存
docker system prune -f

# 2. 本地构建测试
docker build -t aiculture-kit:debug . --no-cache

# 3. 检查镜像
docker images | grep aiculture-kit

# 4. 测试运行
docker run --rm aiculture-kit:debug aiculture --version
```

### 第二步：检查配置文件

```bash
# 检查 Dockerfile
cat Dockerfile | grep FROM

# 检查 Python 版本要求
grep "requires-python" pyproject.toml

# 验证依赖文件存在
ls -la requirements*.txt

# 检查 .dockerignore
cat .dockerignore | grep -E "(requirements|txt)"
```

### 第三步：验证 docker-compose

```bash
# 验证配置语法
docker-compose config

# 测试服务构建
docker-compose build aiculture-kit

# 测试服务运行
docker-compose run --rm aiculture-kit aiculture --help
```

## 🛠️ CI/CD 特定问题

### GitHub Actions 工作流问题

**检查工作流文件：**

```bash
ls -la .github/workflows/
cat .github/workflows/docker-build.yml
```

**常见 GitHub Actions 错误：**

1. **Token 权限不足**

   ```yaml
   # 解决方案：确保正确的权限设置
   permissions:
     contents: read
     packages: write
   ```

2. **构建超时**

   ```yaml
   # 解决方案：增加超时时间
   timeout-minutes: 30
   ```

3. **缓存问题**

   ```yaml
   # 解决方案：使用 GitHub Actions 缓存
   cache-from: type=gha
   cache-to: type=gha,mode=max
   ```

### 容器注册表问题

**登录失败：**

```yaml
- name: 🔑 Log in to Container Registry
  uses: docker/login-action@v3
  with:
    registry: ${{ env.REGISTRY }}
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

**推送失败：**

```yaml
# 确保只在非 PR 事件时推送
push: ${{ github.event_name != 'pull_request' }}
```

## 📋 快速检查清单

在提交代码前，确认以下项目：

- [ ] `Dockerfile` 中的 Python 版本与 `pyproject.toml` 一致
- [ ] `requirements.txt` 和 `requirements-dev.txt` 文件存在
- [ ] `.dockerignore` 没有排除必要文件
- [ ] 本地 `docker build` 成功
- [ ] 本地 `docker run` 测试通过
- [ ] `docker-compose config` 验证通过
- [ ] 主要 CLI 命令在容器中正常工作

## 🚀 自动化修复脚本

创建快速诊断脚本：

```bash
#!/bin/bash
# docker-health-check.sh

echo "🔍 Docker 健康检查开始..."

# 检查 Docker 是否运行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker 未运行或无权限访问"
    exit 1
fi

# 检查 Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile 不存在"
    exit 1
fi

# 检查 Python 版本一致性
DOCKERFILE_PYTHON=$(grep "FROM python:" Dockerfile | cut -d: -f2 | cut -d- -f1)
PYPROJECT_PYTHON=$(grep "requires-python" pyproject.toml | grep -o ">=[0-9.]*" | cut -d= -f2)

echo "📋 Python 版本检查:"
echo "  Dockerfile: $DOCKERFILE_PYTHON"
echo "  pyproject.toml: >=$PYPROJECT_PYTHON"

# 检查依赖文件
for file in requirements.txt requirements-dev.txt; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 缺失"
    fi
done

# 测试构建
echo "🏗️ 测试 Docker 构建..."
if docker build -t aiculture-kit:health-check . >/dev/null 2>&1; then
    echo "✅ Docker 构建成功"
    
    # 测试运行
    if docker run --rm aiculture-kit:health-check aiculture --version >/dev/null 2>&1; then
        echo "✅ 容器运行测试成功"
    else
        echo "❌ 容器运行测试失败"
    fi
    
    # 清理测试镜像
    docker rmi aiculture-kit:health-check >/dev/null 2>&1
else
    echo "❌ Docker 构建失败"
fi

echo "🎉 健康检查完成"
```

## 📞 获取帮助

如果问题仍然存在：

1. **检查日志：** 查看完整的构建日志
2. **GitHub Issues：** 在项目仓库创建 issue
3. **社区支持：** 查看 Docker 和 GitHub Actions 官方文档

## 🔗 相关资源

- [Docker 官方文档](https://docs.docker.com/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Docker Buildx 文档](https://docs.docker.com/buildx/)
- [项目 Docker 指南](../DOCKER.md)
