#!/usr/bin/env python3
"""
Supabase数据库简化设置脚本
使用PostgreSQL直连，自动创建表结构、索引和RLS策略
"""

import os
import psycopg2
from dotenv import load_dotenv
import urllib.parse

# 加载环境变量
load_dotenv()

def get_postgres_connection():
    """获取PostgreSQL连接"""
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise ValueError("未找到SUPABASE_URL环境变量")
    
    # 解析Supabase URL获取数据库连接信息
    # Supabase URL格式: https://xxx.supabase.co
    parsed = urllib.parse.urlparse(supabase_url)
    host = parsed.hostname
    
    # Supabase的PostgreSQL连接信息
    db_host = host.replace('.supabase.co', '.pooler.supabase.com')
    db_name = 'postgres'
    db_user = 'postgres'
    db_password = os.getenv("SUPABASE_DB_PASSWORD") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    db_port = 6543  # Supabase pooler port
    
    print(f"🔗 连接到数据库: {db_host}:{db_port}")
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"❌ 连接失败，尝试备用方法...")
        
        # 备用方法：使用标准端口
        try:
            alt_host = host.replace('.supabase.co', '.db.supabase.co')
            conn = psycopg2.connect(
                host=alt_host,
                port=5432,
                database='postgres',
                user='postgres',
                password=db_password,
                sslmode='require'
            )
            print(f"✅ 使用备用连接成功: {alt_host}:5432")
            return conn
        except Exception as e2:
            print(f"❌ 备用连接也失败: {e2}")
            raise e

def execute_sql_file(conn, sql_content, description):
    """执行SQL内容"""
    print(f"🔧 {description}...")
    
    try:
        cursor = conn.cursor()
        
        # 分割SQL语句
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for stmt in statements:
            if stmt:
                cursor.execute(stmt)
        
        conn.commit()
        cursor.close()
        print(f"✅ {description} - 成功")
        return True
    except Exception as e:
        print(f"❌ {description} - 失败: {e}")
        conn.rollback()
        return False

def main():
    """主函数"""
    print("🚀 开始自动化设置Supabase数据库...")
    print("📝 这将创建表结构、索引、安全策略和默认数据\n")
    
    # 检查必要的环境变量
    required_vars = ["SUPABASE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("\n请在.env文件中设置以下变量:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_SERVICE_ROLE_KEY=your-service-role-key")
        print("或")
        print("SUPABASE_DB_PASSWORD=your-database-password")
        return False
    
    # 检查密码
    password = os.getenv("SUPABASE_DB_PASSWORD") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not password:
        print("❌ 需要数据库密码")
        print("请设置 SUPABASE_DB_PASSWORD 或 SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    try:
        # 连接数据库
        conn = get_postgres_connection()
        print("✅ 数据库连接成功\n")
        
        # SQL脚本内容
        setup_steps = [
            # 1. 创建表结构
            ("""
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
)""", "创建数据表"),

            # 2. 创建索引
            ("""
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_transformation_rules_user_id ON transformation_rules(user_id);
CREATE INDEX IF NOT EXISTS idx_transformation_rules_active ON transformation_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_conversion_history_user_id ON conversion_history(user_id);
CREATE INDEX IF NOT EXISTS idx_conversion_history_created_at ON conversion_history(created_at);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_user_id ON batch_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_jobs(status)""", "创建索引"),

            # 3. 启用RLS
            ("""
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE transformation_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversion_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_jobs ENABLE ROW LEVEL SECURITY""", "启用行级安全策略"),

            # 4. 创建触发器
            ("""
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_transformation_rules_updated_at ON transformation_rules;
CREATE TRIGGER update_transformation_rules_updated_at 
    BEFORE UPDATE ON transformation_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()""", "创建触发器"),

            # 5. 插入默认数据
            ("""
INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default) VALUES
(NULL, '标准问答转换', '将问答式对话转换为第一人称叙述', 'system', '{"style": "first_person", "format": "narrative"}', true),
(NULL, '正式文档转换', '转换为正式的文档格式', 'system', '{"style": "formal", "format": "document"}', false),
(NULL, '简洁摘要转换', '生成简洁的摘要版本', 'system', '{"style": "summary", "format": "brief"}', false)
ON CONFLICT DO NOTHING""", "插入默认规则"),
        ]
        
        # 执行所有设置步骤
        success_count = 0
        for sql, description in setup_steps:
            if execute_sql_file(conn, sql, description):
                success_count += 1
            print()
        
        # 验证设置
        print("🔍 验证数据库设置...")
        tables = ["user_profiles", "transformation_rules", "conversion_history", "batch_jobs"]
        
        cursor = conn.cursor()
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ 表 {table} - 验证成功 (记录数: {count})")
            except Exception as e:
                print(f"❌ 表 {table} - 验证失败: {e}")
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 设置结果: {success_count}/{len(setup_steps)} 步骤成功")
        
        if success_count == len(setup_steps):
            print("🎉 数据库设置完成！")
            print("\n🎯 下一步:")
            print("1. 运行测试: python3 test_supabase_integration.py")
            print("2. 启动后端: uvicorn app.main:app --reload")
            print("3. 启动前端: cd ../frontend && npm run dev")
            return True
        else:
            print("⚠️ 部分设置失败，请检查错误信息")
            return False
            
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        print("\n💡 提示:")
        print("1. 确保Supabase项目已创建")
        print("2. 确保环境变量配置正确")
        print("3. 确保网络连接正常")
        print("4. 可以尝试手动创建表结构")
        return False

if __name__ == "__main__":
    main() 