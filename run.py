#!/usr/bin/env python3
"""
AICultureKit 启动脚本
使用方法: python run.py
"""

import os

# 确保可以导入项目模块
if __name__ == "__main__":
    # 运行FastAPI应用
    import uvicorn
    
    # 安全配置：使用环境变量控制网络绑定和模式
    host = os.getenv("API_HOST", "127.0.0.1")  # 默认只监听本地
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("DEBUG", "false").lower() == "true"  # 只在DEBUG模式启用reload
    
    print("🚀 启动 AICultureKit 服务...")
    print(f"📡 地址: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    
    uvicorn.run("src.main:app", host=host, port=port, reload=reload, log_level="info") 