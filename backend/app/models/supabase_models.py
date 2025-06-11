"""
Supabase 数据模型
与 Supabase PostgreSQL 数据库表结构对应的数据模型
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class TranscriptionStatus(str, Enum):
    """转换状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"


class BatchJobStatus(str, Enum):
    """批量任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ==================== 用户配置相关模型 ====================

class UserProfile(BaseModel):
    """用户配置模型"""
    id: str = Field(description="用户UUID")
    username: Optional[str] = Field(default=None, description="用户名")
    email: str = Field(description="邮箱")
    full_name: Optional[str] = Field(default=None, description="全名")
    avatar_url: Optional[str] = Field(default=None, description="头像URL")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="用户偏好设置")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class UserProfileCreate(BaseModel):
    """创建用户配置请求模型"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserProfileUpdate(BaseModel):
    """更新用户配置请求模型"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


# ==================== 转换规则相关模型 ====================

class TransformationRule(BaseModel):
    """转换规则模型"""
    id: str = Field(description="规则UUID")
    user_id: Optional[str] = Field(default=None, description="用户ID，NULL表示系统规则")
    name: str = Field(description="规则名称")
    description: Optional[str] = Field(default=None, description="规则描述")
    rule_type: str = Field(default="custom", description="规则类型")
    rule_config: Dict[str, Any] = Field(default_factory=dict, description="规则配置")
    is_active: bool = Field(default=True, description="是否激活")
    is_default: bool = Field(default=False, description="是否为默认规则")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class TransformationRuleCreate(BaseModel):
    """创建转换规则请求模型"""
    name: str
    description: Optional[str] = None
    rule_type: str = "custom"
    rule_config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    is_default: bool = False


class TransformationRuleUpdate(BaseModel):
    """更新转换规则请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    rule_type: Optional[str] = None
    rule_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


# ==================== 转换历史相关模型 ====================

class ConversionHistory(BaseModel):
    """转换历史模型"""
    id: str = Field(description="转换UUID")
    user_id: str = Field(description="用户ID")
    original_text: str = Field(description="原始文本")
    converted_text: str = Field(description="转换后文本")
    rule_id: Optional[str] = Field(default=None, description="使用的规则ID")
    quality_score: Optional[float] = Field(default=None, description="质量评分")
    processing_time: Optional[float] = Field(default=None, description="处理时间(秒)")
    file_name: Optional[str] = Field(default=None, description="原始文件名")
    file_size: Optional[int] = Field(default=None, description="文件大小")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(description="创建时间")


class ConversionHistoryCreate(BaseModel):
    """创建转换历史请求模型"""
    original_text: str
    rule_id: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversionHistoryUpdate(BaseModel):
    """更新转换历史请求模型"""
    converted_text: Optional[str] = None
    quality_score: Optional[float] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversionHistorySummary(BaseModel):
    """转换历史摘要模型"""
    id: str
    user_id: str
    file_name: Optional[str]
    quality_score: Optional[float]
    processing_time: Optional[float]
    created_at: datetime
    rule_name: Optional[str] = None  # 从关联的规则表获取


# ==================== 批量处理相关模型 ====================

class BatchJob(BaseModel):
    """批量处理任务模型"""
    id: str = Field(description="任务UUID")
    user_id: str = Field(description="用户ID")
    job_name: str = Field(description="任务名称")
    status: BatchJobStatus = Field(default=BatchJobStatus.PENDING, description="任务状态")
    total_files: int = Field(default=0, description="总文件数")
    processed_files: int = Field(default=0, description="已处理文件数")
    failed_files: int = Field(default=0, description="失败文件数")
    rule_id: Optional[str] = Field(default=None, description="使用的规则ID")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="处理结果")
    error_log: Optional[str] = Field(default=None, description="错误日志")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    created_at: datetime = Field(description="创建时间")


class BatchJobCreate(BaseModel):
    """创建批量任务请求模型"""
    job_name: str
    rule_id: Optional[str] = None
    files: List[Dict[str, Any]] = Field(default_factory=list, description="待处理文件列表")


class BatchJobUpdate(BaseModel):
    """更新批量任务请求模型"""
    status: Optional[BatchJobStatus] = None
    processed_files: Optional[int] = None
    failed_files: Optional[int] = None
    results: Optional[List[Dict[str, Any]]] = None
    error_log: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None 