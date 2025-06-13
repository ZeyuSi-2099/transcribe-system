"""
Supabase客户端配置
用于后端服务连接Supabase数据库和认证服务
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class SupabaseClient:
    """Supabase客户端单例类"""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> 'SupabaseClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """初始化Supabase客户端"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # 修复：使用正确的环境变量名
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
        
        self._client = create_client(url, key)
    
    @property
    def client(self) -> Client:
        """获取Supabase客户端实例"""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def get_user_client(self, access_token: str) -> Client:
        """获取用户认证的客户端实例"""
        url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        user_client = create_client(url, anon_key)
        user_client.auth.set_session(access_token, "")
        return user_client

# 全局Supabase客户端实例
supabase_client = SupabaseClient()

def get_supabase() -> Client:
    """获取Supabase客户端实例的便捷函数"""
    return supabase_client.client

def get_user_supabase(access_token: str) -> Client:
    """获取用户认证的Supabase客户端实例的便捷函数"""
    return supabase_client.get_user_client(access_token) 