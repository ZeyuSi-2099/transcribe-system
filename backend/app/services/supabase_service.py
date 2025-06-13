"""
Supabase 数据服务层
封装所有与 Supabase 数据库交互的操作
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from supabase import Client

from app.core.supabase_client import get_supabase, get_user_supabase
from app.models.supabase_models import (
    ConversionHistory,
    ConversionHistoryCreate,
    ConversionHistoryUpdate,
    ConversionHistorySummary,
    TransformationRule,
    TransformationRuleCreate,
    TransformationRuleUpdate,
    UserProfile,
    UserProfileCreate,
    UserProfileUpdate,
    BatchJob,
    BatchJobCreate,
    BatchJobUpdate
)


class ConversionHistoryService:
    """转换历史服务"""
    
    def __init__(self, user_id: str, access_token: Optional[str] = None):
        self.user_id = user_id
        if access_token:
            self.client = get_user_supabase(access_token)
        else:
            self.client = get_supabase()
    
    async def create_conversion(self, conversion_data: ConversionHistoryCreate) -> ConversionHistory:
        """创建新的转换记录"""
        data = {
            "id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "original_text": conversion_data.original_text,
            "converted_text": "",  # 初始化为空，转换完成后更新
            "rule_id": conversion_data.rule_id,
            "file_name": conversion_data.file_name,
            "file_size": conversion_data.file_size,
            "metadata": conversion_data.metadata,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = self.client.table("conversion_history").insert(data).execute()
        
        if result.data:
            return ConversionHistory(**result.data[0])
        else:
            raise Exception("Failed to create conversion record")
    
    async def update_conversion(self, conversion_id: str, update_data: ConversionHistoryUpdate) -> ConversionHistory:
        """更新转换记录"""
        data = {}
        if update_data.converted_text is not None:
            data["converted_text"] = update_data.converted_text
        if update_data.quality_score is not None:
            data["quality_score"] = update_data.quality_score
        if update_data.processing_time is not None:
            data["processing_time"] = update_data.processing_time
        if update_data.metadata is not None:
            data["metadata"] = update_data.metadata
        
        result = self.client.table("conversion_history").update(data).eq("id", conversion_id).eq("user_id", self.user_id).execute()
        
        if result.data:
            return ConversionHistory(**result.data[0])
        else:
            raise Exception("Failed to update conversion record")
    
    async def get_conversion(self, conversion_id: str) -> Optional[ConversionHistory]:
        """获取单个转换记录"""
        result = self.client.table("conversion_history").select("*").eq("id", conversion_id).eq("user_id", self.user_id).execute()
        
        if result.data:
            return ConversionHistory(**result.data[0])
        return None
    
    async def list_conversions(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        rule_id: Optional[str] = None
    ) -> List[ConversionHistorySummary]:
        """获取转换历史列表"""
        query = self.client.table("conversion_history").select(
            "id, user_id, file_name, quality_score, processing_time, created_at, transformation_rules(name)"
        ).eq("user_id", self.user_id)
        
        # 搜索过滤
        if search:
            query = query.ilike("file_name", f"%{search}%")
        
        # 规则过滤
        if rule_id:
            query = query.eq("rule_id", rule_id)
        
        # 排序和分页
        result = query.order("created_at", desc=True).range(skip, skip + limit - 1).execute()
        
        conversions = []
        if result.data:
            for item in result.data:
                rule_name = None
                if item.get("transformation_rules"):
                    rule_name = item["transformation_rules"]["name"]
                
                conversions.append(ConversionHistorySummary(
                    id=item["id"],
                    user_id=item["user_id"],
                    file_name=item.get("file_name"),
                    quality_score=item.get("quality_score"),
                    processing_time=item.get("processing_time"),
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                    rule_name=rule_name
                ))
        
        return conversions
    
    async def delete_conversion(self, conversion_id: str) -> bool:
        """删除转换记录"""
        result = self.client.table("conversion_history").delete().eq("id", conversion_id).eq("user_id", self.user_id).execute()
        return len(result.data) > 0
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """获取用户转换统计信息"""
        # 总转换次数
        total_result = self.client.table("conversion_history").select("id", count="exact").eq("user_id", self.user_id).execute()
        total_conversions = total_result.count if total_result.count else 0
        
        # 平均质量分数
        quality_result = self.client.table("conversion_history").select("quality_score").eq("user_id", self.user_id).not_.is_("quality_score", "null").execute()
        
        avg_quality = 0
        if quality_result.data:
            scores = [item["quality_score"] for item in quality_result.data]
            avg_quality = sum(scores) / len(scores) if scores else 0
        
        # 总处理时间
        time_result = self.client.table("conversion_history").select("processing_time").eq("user_id", self.user_id).not_.is_("processing_time", "null").execute()
        
        total_time = 0
        if time_result.data:
            times = [item["processing_time"] for item in time_result.data]
            total_time = sum(times) if times else 0
        
        return {
            "total_conversions": total_conversions,
            "average_quality_score": round(avg_quality, 2),
            "total_processing_time": round(total_time, 2)
        }


class TransformationRuleService:
    """转换规则服务"""
    
    def __init__(self, user_id: str, access_token: Optional[str] = None):
        self.user_id = user_id
        if access_token:
            self.client = get_user_supabase(access_token)
        else:
            self.client = get_supabase()
    
    async def create_rule(self, rule_data: TransformationRuleCreate) -> TransformationRule:
        """创建新的转换规则"""
        data = {
            "id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "name": rule_data.name,
            "description": rule_data.description,
            "rule_type": rule_data.rule_type,
            "rule_config": rule_data.rule_config,
            "is_active": rule_data.is_active,
            "is_default": rule_data.is_default,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = self.client.table("transformation_rules").insert(data).execute()
        
        if result.data:
            return TransformationRule(**result.data[0])
        else:
            raise Exception("Failed to create transformation rule")
    
    async def list_rules(self, include_system: bool = True) -> List[TransformationRule]:
        """获取转换规则列表"""
        query = self.client.table("transformation_rules").select("*")
        
        if include_system:
            # 包含系统规则和用户规则
            query = query.or_(f"user_id.eq.{self.user_id},user_id.is.null")
        else:
            # 只包含用户规则
            query = query.eq("user_id", self.user_id)
        
        result = query.eq("is_active", True).order("created_at", desc=True).execute()
        
        rules = []
        if result.data:
            for item in result.data:
                rules.append(TransformationRule(
                    id=item["id"],
                    user_id=item.get("user_id"),
                    name=item["name"],
                    description=item.get("description"),
                    rule_type=item["rule_type"],
                    rule_config=item["rule_config"],
                    is_active=item["is_active"],
                    is_default=item["is_default"],
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                ))
        
        return rules
    
    async def get_rule(self, rule_id: str) -> Optional[TransformationRule]:
        """获取单个转换规则"""
        result = self.client.table("transformation_rules").select("*").eq("id", rule_id).or_(f"user_id.eq.{self.user_id},user_id.is.null").execute()
        
        if result.data:
            item = result.data[0]
            return TransformationRule(
                id=item["id"],
                user_id=item.get("user_id"),
                name=item["name"],
                description=item.get("description"),
                rule_type=item["rule_type"],
                rule_config=item["rule_config"],
                is_active=item["is_active"],
                is_default=item["is_default"],
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
            )
        return None
    
    def get_system_rules(self) -> List[TransformationRule]:
        """获取系统规则（同步版本，用于快速测试）"""
        result = self.client.table("transformation_rules").select("*").is_("user_id", "null").eq("is_active", True).execute()
        
        rules = []
        if result.data:
            for item in result.data:
                rules.append(TransformationRule(
                    id=item["id"],
                    user_id=item.get("user_id"),
                    name=item["name"],
                    description=item.get("description"),
                    rule_type=item["rule_type"],
                    rule_config=item["rule_config"],
                    is_active=item["is_active"],
                    is_default=item["is_default"],
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                ))
        
        return rules


class UserProfileService:
    """用户配置服务"""
    
    def __init__(self, user_id: str, access_token: Optional[str] = None):
        self.user_id = user_id
        if access_token:
            self.client = get_user_supabase(access_token)
        else:
            self.client = get_supabase()
    
    async def get_or_create_profile(self, email: str, profile_data: Optional[UserProfileCreate] = None) -> UserProfile:
        """获取或创建用户配置"""
        # 先尝试获取现有配置
        result = self.client.table("user_profiles").select("*").eq("id", self.user_id).execute()
        
        if result.data:
            item = result.data[0]
            return UserProfile(
                id=item["id"],
                username=item.get("username"),
                email=item["email"],
                full_name=item.get("full_name"),
                avatar_url=item.get("avatar_url"),
                preferences=item.get("preferences", {}),
                created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
            )
        else:
            # 创建新的用户配置
            data = {
                "id": self.user_id,
                "email": email,
                "username": profile_data.username if profile_data else None,
                "full_name": profile_data.full_name if profile_data else None,
                "avatar_url": profile_data.avatar_url if profile_data else None,
                "preferences": profile_data.preferences if profile_data else {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("user_profiles").insert(data).execute()
            
            if result.data:
                item = result.data[0]
                return UserProfile(
                    id=item["id"],
                    username=item.get("username"),
                    email=item["email"],
                    full_name=item.get("full_name"),
                    avatar_url=item.get("avatar_url"),
                    preferences=item.get("preferences", {}),
                    created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
                )
            else:
                raise Exception("Failed to create user profile") 