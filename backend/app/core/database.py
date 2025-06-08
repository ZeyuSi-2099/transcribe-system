"""
数据库配置和连接管理
"""

from typing import Annotated
from sqlmodel import SQLModel, Session, create_engine
from fastapi import Depends

from app.core.config import settings


# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)


def create_db_and_tables():
    """创建数据库表"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session


# 数据库会话依赖
SessionDep = Annotated[Session, Depends(get_session)] 