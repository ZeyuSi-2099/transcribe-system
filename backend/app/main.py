"""
笔录转换系统 - FastAPI 主应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 启动笔录转换系统...")
    create_db_and_tables()
    print("✅ 数据库初始化完成")
    
    yield
    
    # 关闭时执行
    print("🔄 正在关闭笔录转换系统...")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="基于LLM和规则引擎的智能笔录转换工具",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "笔录转换系统",
            "version": settings.VERSION
        }
    )


# 根路径
@app.get("/")
async def root():
    """根路径欢迎信息"""
    return {
        "message": "欢迎使用笔录转换系统 API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# 注册 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 