-- Supabase Database Setup Script
-- 笔录转换系统数据库表结构

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

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_transformation_rules_user_id ON transformation_rules(user_id);
CREATE INDEX IF NOT EXISTS idx_transformation_rules_active ON transformation_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_conversion_history_user_id ON conversion_history(user_id);
CREATE INDEX IF NOT EXISTS idx_conversion_history_created_at ON conversion_history(created_at);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_user_id ON batch_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_jobs(status);

-- 启用行级安全策略 (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE transformation_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversion_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_jobs ENABLE ROW LEVEL SECURITY;

-- 用户配置表的RLS策略
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- 转换规则表的RLS策略
CREATE POLICY "Users can view own rules" ON transformation_rules
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own rules" ON transformation_rules
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own rules" ON transformation_rules
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own rules" ON transformation_rules
    FOR DELETE USING (auth.uid() = user_id);

-- 转换历史表的RLS策略
CREATE POLICY "Users can view own history" ON conversion_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own history" ON conversion_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 批量任务表的RLS策略
CREATE POLICY "Users can view own jobs" ON batch_jobs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own jobs" ON batch_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own jobs" ON batch_jobs
    FOR UPDATE USING (auth.uid() = user_id);

-- 创建触发器函数用于自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建更新时间触发器
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transformation_rules_updated_at 
    BEFORE UPDATE ON transformation_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入默认转换规则
INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default) VALUES
(NULL, '标准问答转换', '将问答式对话转换为第一人称叙述', 'system', '{"style": "first_person", "format": "narrative"}', true),
(NULL, '正式文档转换', '转换为正式的文档格式', 'system', '{"style": "formal", "format": "document"}', false),
(NULL, '简洁摘要转换', '生成简洁的摘要版本', 'system', '{"style": "summary", "format": "brief"}', false)
ON CONFLICT DO NOTHING;

-- 创建存储桶用于文件存储
INSERT INTO storage.buckets (id, name, public) VALUES ('transcripts', 'transcripts', false);

-- 存储桶的RLS策略
CREATE POLICY "Users can upload own files" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'transcripts' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view own files" ON storage.objects
    FOR SELECT USING (bucket_id = 'transcripts' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete own files" ON storage.objects
    FOR DELETE USING (bucket_id = 'transcripts' AND auth.uid()::text = (storage.foldername(name))[1]); 