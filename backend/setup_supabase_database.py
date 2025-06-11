#!/usr/bin/env python3
"""
Supabase数据库自动化设置脚本
自动创建表结构、索引和RLS策略
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.supabase_client import get_supabase

# 加载环境变量
load_dotenv()

# SQL脚本片段
CREATE_TABLES_SQL = """
-- 1. 用户配置表
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 转换规则表
CREATE TABLE IF NOT EXISTS transformation_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL DEFAULT 'custom',
    rule_config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 转换历史表
CREATE TABLE IF NOT EXISTS conversion_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    original_text TEXT NOT NULL,
    converted_text TEXT NOT NULL,
    rule_id UUID REFERENCES transformation_rules(id) ON DELETE SET NULL,
    quality_score DECIMAL(5,2),
    processing_time DECIMAL(8,3),
    file_name VARCHAR(255),
    file_size INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 批量处理任务表
CREATE TABLE IF NOT EXISTS batch_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    total_files INTEGER DEFAULT 0,
    processed_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    rule_id UUID REFERENCES transformation_rules(id) ON DELETE SET NULL,
    results JSONB DEFAULT '[]',
    error_log TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

CREATE_INDEXES_SQL = """
-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_transformation_rules_user_id ON transformation_rules(user_id);
CREATE INDEX IF NOT EXISTS idx_transformation_rules_active ON transformation_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_conversion_history_user_id ON conversion_history(user_id);
CREATE INDEX IF NOT EXISTS idx_conversion_history_created_at ON conversion_history(created_at);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_user_id ON batch_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_jobs(status);
"""

ENABLE_RLS_SQL = """
-- 启用行级安全策略 (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE transformation_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversion_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_jobs ENABLE ROW LEVEL SECURITY;
"""

RLS_POLICIES_SQL = """
-- 用户配置表的RLS策略
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- 转换规则表的RLS策略
DROP POLICY IF EXISTS "Users can view own rules" ON transformation_rules;
CREATE POLICY "Users can view own rules" ON transformation_rules
    FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);

DROP POLICY IF EXISTS "Users can create own rules" ON transformation_rules;
CREATE POLICY "Users can create own rules" ON transformation_rules
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own rules" ON transformation_rules;
CREATE POLICY "Users can update own rules" ON transformation_rules
    FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own rules" ON transformation_rules;
CREATE POLICY "Users can delete own rules" ON transformation_rules
    FOR DELETE USING (auth.uid() = user_id);

-- 转换历史表的RLS策略
DROP POLICY IF EXISTS "Users can view own history" ON conversion_history;
CREATE POLICY "Users can view own history" ON conversion_history
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create own history" ON conversion_history;
CREATE POLICY "Users can create own history" ON conversion_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 批量任务表的RLS策略
DROP POLICY IF EXISTS "Users can view own jobs" ON batch_jobs;
CREATE POLICY "Users can view own jobs" ON batch_jobs
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can create own jobs" ON batch_jobs;
CREATE POLICY "Users can create own jobs" ON batch_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own jobs" ON batch_jobs;
CREATE POLICY "Users can update own jobs" ON batch_jobs
    FOR UPDATE USING (auth.uid() = user_id);
"""

TRIGGERS_SQL = """
-- 创建触发器函数用于自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建更新时间触发器
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_transformation_rules_updated_at ON transformation_rules;
CREATE TRIGGER update_transformation_rules_updated_at 
    BEFORE UPDATE ON transformation_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""

DEFAULT_RULES_SQL = """
-- 插入默认转换规则
INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default) VALUES
(NULL, '标准问答转换', '将问答式对话转换为第一人称叙述', 'system', '{"style": "first_person", "format": "narrative"}', true),
(NULL, '正式文档转换', '转换为正式的文档格式', 'system', '{"style": "formal", "format": "document"}', false),
(NULL, '简洁摘要转换', '生成简洁的摘要版本', 'system', '{"style": "summary", "format": "brief"}', false)
ON CONFLICT DO NOTHING;
"""

STORAGE_SETUP_SQL = """
-- 创建存储桶用于文件存储
INSERT INTO storage.buckets (id, name, public) VALUES ('transcripts', 'transcripts', false)
ON CONFLICT DO NOTHING;
"""

STORAGE_POLICIES_SQL = """
-- 存储桶的RLS策略
DROP POLICY IF EXISTS "Users can upload own files" ON storage.objects;
CREATE POLICY "Users can upload own files" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'transcripts' AND auth.uid()::text = (storage.foldername(name))[1]);

DROP POLICY IF EXISTS "Users can view own files" ON storage.objects;
CREATE POLICY "Users can view own files" ON storage.objects
    FOR SELECT USING (bucket_id = 'transcripts' AND auth.uid()::text = (storage.foldername(name))[1]);

DROP POLICY IF EXISTS "Users can delete own files" ON storage.objects;
CREATE POLICY "Users can delete own files" ON storage.objects
    FOR DELETE USING (bucket_id = 'transcripts' AND auth.uid()::text = (storage.foldername(name))[1]);
"""

async def execute_sql(supabase, sql, description):
    """执行SQL并处理错误"""
    print(f"🔧 {description}...")
    
    try:
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print(f"✅ {description} - 成功")
        return True
    except Exception as e:
        # 如果没有exec_sql函数，尝试直接使用数据库查询
        try:
            # 分割SQL语句并逐个执行
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            for stmt in statements:
                if stmt:
                    supabase.query(stmt).execute()
            print(f"✅ {description} - 成功")
            return True
        except Exception as e2:
            print(f"❌ {description} - 失败: {e2}")
            return False

async def setup_database():
    """设置数据库"""
    print("🚀 开始自动化设置Supabase数据库...\n")
    
    # 检查环境变量
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请确保 .env 文件包含所需的Supabase配置")
        return False
    
    try:
        supabase = get_supabase()
        print("✅ Supabase连接成功\n")
        
        # 执行设置步骤
        steps = [
            (CREATE_TABLES_SQL, "创建数据表"),
            (CREATE_INDEXES_SQL, "创建索引"),
            (ENABLE_RLS_SQL, "启用行级安全策略"),
            (RLS_POLICIES_SQL, "设置安全策略"),
            (TRIGGERS_SQL, "创建触发器"),
            (DEFAULT_RULES_SQL, "插入默认规则"),
            (STORAGE_SETUP_SQL, "设置文件存储"),
            (STORAGE_POLICIES_SQL, "设置存储策略"),
        ]
        
        success_count = 0
        for sql, description in steps:
            if await execute_sql(supabase, sql, description):
                success_count += 1
            print()  # 空行分隔
        
        print(f"📊 设置结果: {success_count}/{len(steps)} 步骤成功")
        
        if success_count == len(steps):
            print("🎉 数据库设置完成！所有表结构和策略已就绪")
            
            # 验证设置
            print("\n🔍 验证数据库设置...")
            await verify_setup(supabase)
            
            return True
        else:
            print("⚠️ 部分设置失败，请检查错误信息")
            return False
            
    except Exception as e:
        print(f"❌ 数据库设置失败: {e}")
        return False

async def verify_setup(supabase):
    """验证数据库设置"""
    tables = ["user_profiles", "transformation_rules", "conversion_history", "batch_jobs"]
    
    for table in tables:
        try:
            result = supabase.table(table).select("count", count="exact").limit(1).execute()
            print(f"✅ 表 {table} - 验证成功 (记录数: {result.count})")
        except Exception as e:
            print(f"❌ 表 {table} - 验证失败: {e}")

async def main():
    """主函数"""
    success = await setup_database()
    
    if success:
        print("\n🎯 下一步:")
        print("1. 运行测试脚本: python3 test_supabase_integration.py")
        print("2. 启动后端服务: uvicorn app.main:app --reload")
        print("3. 启动前端服务: cd ../frontend && npm run dev")
        print("4. 访问应用: http://localhost:3000")
    else:
        print("\n❌ 设置失败，请检查错误信息并重试")

if __name__ == "__main__":
    asyncio.run(main()) 