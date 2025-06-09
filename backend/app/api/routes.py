"""
API 路由配置
"""

from fastapi import APIRouter
from app.api.endpoints import transcription, rules, advanced_quality

# 创建主路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(
    transcription.router, 
    prefix="/transcription", 
    tags=["transcription"]
)

api_router.include_router(
    rules.router,
    prefix="/rules",
    tags=["rules"]
)

# 阶段三：深度质量分析路由
api_router.include_router(
    advanced_quality.router,
    prefix="/quality",
    tags=["advanced-quality"]
) 