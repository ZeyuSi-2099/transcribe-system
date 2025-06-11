"""
认证中间件和依赖注入
处理用户身份验证和权限控制
"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import json

from app.core.supabase_client import get_supabase


security = HTTPBearer()


class AuthUser:
    """认证用户信息"""
    
    def __init__(self, user_id: str, email: str, access_token: str):
        self.user_id = user_id
        self.email = email
        self.access_token = access_token


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> AuthUser:
    """获取当前认证用户"""
    
    access_token = credentials.credentials
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # 使用 Supabase 验证 token
        supabase = get_supabase()
        
        # 验证 token 并获取用户信息
        user_response = supabase.auth.get_user(access_token)
        
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_response.user
        
        return AuthUser(
            user_id=user.id,
            email=user.email,
            access_token=access_token
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[AuthUser]:
    """获取可选的认证用户（用于公共接口）"""
    
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    access_token = authorization.replace("Bearer ", "")
    
    try:
        supabase = get_supabase()
        user_response = supabase.auth.get_user(access_token)
        
        if user_response.user:
            return AuthUser(
                user_id=user_response.user.id,
                email=user_response.user.email,
                access_token=access_token
            )
        
    except Exception:
        pass  # 忽略错误，返回 None
    
    return None


# 依赖注入类型
CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
OptionalUser = Annotated[Optional[AuthUser], Depends(get_optional_user)] 