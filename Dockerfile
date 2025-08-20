# 使用官方Python运行时作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt requirements-dev.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-dev.txt

# 复制源代码
COPY . .

# 安装包（可编辑模式）
RUN pip install -e .

# 创建非root用户
RUN groupadd -r aiculture && useradd -r -g aiculture aiculture
RUN chown -R aiculture:aiculture /app
USER aiculture

# 暴露端口（如果需要的话）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import aiculture; print('OK')" || exit 1

# 默认命令
CMD ["aiculture", "--help"] 