"""
应用核心配置
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    PROJECT_NAME: str = "笔录转换系统"
    VERSION: str = "0.1.0-alpha"
    API_V1_STR: str = "/api/v1"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS 配置
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",  # Next.js 开发服务器
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Next.js 开发服务器 (备用端口)
        "http://127.0.0.1:3001",
        "http://localhost:8000",  # FastAPI 开发服务器
        "http://127.0.0.1:8000",
        "https://transcribe.solutions",  # 生产环境域名
        "https://www.transcribe.solutions",  # 生产环境域名(www)
    ]
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./transcribe_system.db"
    DATABASE_ECHO: bool = True  # 开发环境显示SQL日志
    
    # LLM 配置
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, description="Deepseek API密钥")
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # OpenAI 兼容配置 (备用)
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API密钥")
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 本地 Ollama 配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b-instruct"
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".txt", ".docx"]
    UPLOAD_DIR: str = "./uploads"
    
    # 转换配置
    MAX_TEXT_LENGTH: int = 50000  # 最大文本长度
    DEFAULT_TIMEOUT: int = 300  # 默认超时时间(秒)
    
    # 安全配置
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT密钥，生产环境必须修改"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis 配置 (可选)
    REDIS_URL: Optional[str] = Field(default=None, description="Redis连接URL")
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Supabase 配置 (用于前端认证)
    SUPABASE_URL: Optional[str] = Field(default=None, description="Supabase项目URL")
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None, description="Supabase匿名密钥")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None, description="Supabase服务角色密钥")
    
    # 环境配置
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: Optional[str] = Field(default=None, description="允许的CORS源")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # 忽略额外的环境变量
    )


# 创建全局配置实例
settings = Settings() 