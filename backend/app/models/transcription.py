"""
笔录转换相关数据模型
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON
from enum import Enum


class TranscriptionStatus(str, Enum):
    """转换状态枚举"""
    PENDING = "pending"      # 等待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败


class TranscriptionBase(SQLModel):
    """转换记录基础模型"""
    title: str = Field(description="转换任务标题")
    original_text: str = Field(description="原始文本内容")
    file_name: Optional[str] = Field(default=None, description="原始文件名")
    file_type: Optional[str] = Field(default=None, description="文件类型")


class Transcription(TranscriptionBase, table=True):
    """转换记录表模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 新增字段：是否用户主动保存的任务
    is_saved: bool = Field(default=False, description="是否用户主动保存的任务")
    
    # 转换结果
    converted_text: Optional[str] = Field(default=None, description="转换后的文本")
    
    # 状态和元数据
    status: TranscriptionStatus = Field(default=TranscriptionStatus.PENDING, description="转换状态")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # 质量指标
    quality_metrics: Optional[Dict[str, Any]] = Field(
        default=None, 
        sa_column=Column(JSON),
        description="质量检验指标"
    )
    
    # 配置信息
    rule_config: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON), 
        description="使用的规则配置"
    )
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    
    # 处理时间统计
    processing_time: Optional[float] = Field(default=None, description="处理时间(秒)")


class TranscriptionCreate(TranscriptionBase):
    """创建转换记录的请求模型"""
    rule_config: Optional[Dict[str, Any]] = None
    is_saved: bool = Field(default=False, description="是否用户主动保存的任务")


class TranscriptionUpdate(SQLModel):
    """更新转换记录的请求模型"""
    title: Optional[str] = None
    status: Optional[TranscriptionStatus] = None
    converted_text: Optional[str] = None
    error_message: Optional[str] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    is_saved: Optional[bool] = None # 允许更新is_saved状态


class TranscriptionPublic(TranscriptionBase):
    """公开的转换记录响应模型"""
    id: int
    converted_text: Optional[str]
    status: TranscriptionStatus
    quality_metrics: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    processing_time: Optional[float]


class TranscriptionSummary(SQLModel):
    """转换记录摘要模型"""
    id: int
    title: str
    status: TranscriptionStatus
    created_at: datetime
    processing_time: Optional[float] 