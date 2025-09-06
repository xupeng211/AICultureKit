"""
AICultureKit FastAPI 应用入口点
"""

import asyncio
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .__version__ import __version__
from .core import config, logger
from .services import service_manager

# 创建FastAPI应用
app = FastAPI(
    title="AICultureKit",
    description="AI辅助文化产业工具包",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加CORS中间件 - 安全配置：限制允许的域名
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # 使用环境变量控制允许的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("🚀 AICultureKit 应用启动中...")

    try:
        # 初始化所有服务
        success = await service_manager.initialize_all()
        if success:
            logger.info("✅ 所有服务初始化成功")
        else:
            logger.error("❌ 服务初始化失败")
    except Exception as e:
        logger.error(f"❌ 启动过程中发生错误: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("🛑 AICultureKit 应用关闭中...")

    try:
        await service_manager.shutdown_all()
        logger.info("✅ 所有服务已关闭")
    except Exception as e:
        logger.error(f"❌ 关闭过程中发生错误: {e}")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to AICultureKit",
        "version": __version__,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": str(asyncio.get_event_loop().time()),
        "services": {
            service_name: "active" for service_name in service_manager.services.keys()
        },
    }


@app.get("/api/status")
async def api_status():
    """API状态检查"""
    try:
        # 检查服务状态
        service_status = {}
        for name, service in service_manager.services.items():
            service_status[name] = {"name": service.name, "status": "active"}

        return {
            "api_version": "v1",
            "status": "operational",
            "services": service_status,
            "config": {
                "debug": config.get("debug", False),
                "environment": config.get("environment", "development"),
            },
        }
    except Exception as e:
        logger.error(f"状态检查失败: {e}")
        raise HTTPException(status_code=500, detail="服务状态检查失败")


# 错误处理 - 安全配置：生产环境隐藏敏感信息
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"全局异常: {exc}")
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    if debug_mode:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    return JSONResponse(status_code=500, content={"error": "服务暂时不可用"})


if __name__ == "__main__":
    import uvicorn

    # 安全配置：使用环境变量控制网络绑定和模式
    host = os.getenv("API_HOST", "127.0.0.1")  # 默认只监听本地
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("DEBUG", "false").lower() == "true"  # 只在DEBUG模式启用reload

    uvicorn.run("src.main:app", host=host, port=port, reload=reload, log_level="info")
