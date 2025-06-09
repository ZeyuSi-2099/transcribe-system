"""
规则管理相关数据模型
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Column, JSON
from enum import Enum


class RuleType(str, Enum):
    """规则类型枚举"""
    PREPROCESSING = "preprocessing"    # 预处理规则
    DIALOGUE_STRUCTURE = "dialogue_structure"  # 对话结构规则
    LANGUAGE_STYLE = "language_style"  # 语言风格规则
    CONTENT_FILTER = "content_filter"  # 内容过滤规则
    POSTPROCESSING = "postprocessing"  # 后处理规则


class RuleScope(str, Enum):
    """规则应用范围枚举"""
    GLOBAL = "global"      # 全局规则
    DOMAIN = "domain"      # 领域特定规则
    USER = "user"          # 用户自定义规则


class RulePriority(int, Enum):
    """规则优先级枚举"""
    LOW = 1
    MEDIUM = 5
    HIGH = 10


class RuleBase(SQLModel):
    """规则基础模型"""
    name: str = Field(description="规则名称")
    description: str = Field(description="规则描述")
    rule_type: RuleType = Field(description="规则类型")
    scope: RuleScope = Field(default=RuleScope.GLOBAL, description="规则范围")
    priority: int = Field(default=RulePriority.MEDIUM, description="规则优先级")
    is_active: bool = Field(default=True, description="是否启用")


class Rule(RuleBase, table=True):
    """规则表模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 规则内容
    pattern: Optional[str] = Field(default=None, description="匹配模式(正则表达式或关键词)")
    replacement: Optional[str] = Field(default=None, description="替换模板")
    conditions: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="规则执行条件"
    )
    
    # 规则参数
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="规则参数配置"
    )
    
    # 规则示例
    examples: Optional[List[Dict[str, str]]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="规则应用示例"
    )
    
    # 元数据
    created_by: Optional[str] = Field(default=None, description="创建者")
    tags: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="规则标签"
    )
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    # 使用统计
    usage_count: int = Field(default=0, description="使用次数")
    success_rate: Optional[float] = Field(default=None, description="成功率")


class RuleSetBase(SQLModel):
    """规则集基础模型"""
    name: str = Field(description="规则集名称")
    description: str = Field(description="规则集描述")
    version: str = Field(default="1.0.0", description="版本号")
    is_default: bool = Field(default=False, description="是否为默认规则集")


class RuleSet(RuleSetBase, table=True):
    """规则集表模型"""
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 规则集配置
    rules: List[int] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="包含的规则ID列表"
    )
    
    rule_weights: Optional[Dict[str, float]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="规则权重配置"
    )
    
    execution_order: Optional[List[int]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="规则执行顺序"
    )
    
    # 适用场景
    applicable_scenarios: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="适用场景列表"
    )
    
    # 元数据
    created_by: Optional[str] = Field(default=None, description="创建者")
    is_public: bool = Field(default=True, description="是否公开")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    # 使用统计
    usage_count: int = Field(default=0, description="使用次数")
    average_score: Optional[float] = Field(default=None, description="平均评分")


# API 请求/响应模型

class RuleCreate(RuleBase):
    """创建规则的请求模型"""
    pattern: Optional[str] = None
    replacement: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, str]]] = None
    tags: Optional[List[str]] = None


class RuleUpdate(SQLModel):
    """更新规则的请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    pattern: Optional[str] = None
    replacement: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, str]]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    tags: Optional[List[str]] = None


class RulePublic(RuleBase):
    """公开的规则响应模型"""
    id: int
    pattern: Optional[str]
    replacement: Optional[str]
    conditions: Optional[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]
    examples: Optional[List[Dict[str, str]]]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]
    usage_count: int
    success_rate: Optional[float]


class RuleSetCreate(RuleSetBase):
    """创建规则集的请求模型"""
    rules: List[int] = []
    rule_weights: Optional[Dict[str, float]] = None
    execution_order: Optional[List[int]] = None
    applicable_scenarios: Optional[List[str]] = None


class RuleSetUpdate(SQLModel):
    """更新规则集的请求模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    rules: Optional[List[int]] = None
    rule_weights: Optional[Dict[str, float]] = None
    execution_order: Optional[List[int]] = None
    applicable_scenarios: Optional[List[str]] = None
    is_default: Optional[bool] = None
    is_public: Optional[bool] = None


class RuleSetPublic(RuleSetBase):
    """公开的规则集响应模型"""
    id: int
    rules: List[int]
    rule_weights: Optional[Dict[str, float]]
    execution_order: Optional[List[int]]
    applicable_scenarios: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]
    usage_count: int
    average_score: Optional[float]


class RuleSetWithRules(RuleSetPublic):
    """包含规则详情的规则集模型"""
    rule_details: List[RulePublic] = [] 