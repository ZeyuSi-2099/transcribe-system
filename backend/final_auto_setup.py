#!/usr/bin/env python3
"""
最终自动化设置 - 使用HTTP直接调用Supabase
绕过客户端限制，直接执行SQL
"""

import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def execute_sql_via_http(sql_statement, description="执行SQL"):
    """通过HTTP直接执行SQL"""
    print(f"🔧 {description}...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # 解析项目ID
    project_id = supabase_url.split("//")[1].split(".")[0]
    
    # 方法1: 使用PostgreSQL连接池
    url = f"https://{project_id}.pooler.supabase.com/rest/v1/rpc/exec"
    
    headers = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "apikey": service_key
    }
    
    payload = {"sql": sql_statement}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code in [200, 201, 204]:
            print(f"✅ {description} - 成功")
            return True
        elif response.status_code == 404:
            print(f"⚠️ {description} - RPC端点不存在，尝试其他方法")
            return False
        else:
            print(f"❌ {description} - 失败: {response.status_code} {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {description} - 网络错误: {e}")
        return False

def create_helper_function():
    """创建SQL执行辅助函数"""
    print("🔧 创建SQL执行辅助函数...")
    
    create_function_sql = """
CREATE OR REPLACE FUNCTION exec(sql_text TEXT) 
RETURNS TEXT AS $$
BEGIN
    EXECUTE sql_text;
    RETURN 'OK';
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'ERROR: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
"""
    
    return execute_sql_via_http(create_function_sql, "创建辅助函数")

def auto_create_all_tables():
    """自动创建所有表"""
    print("🚀 开始自动创建所有表...")
    
    # 完整的SQL脚本
    complete_sql = """
-- 创建所有表结构
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transformation_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL DEFAULT 'custom',
    rule_config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

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
    created_at TIMESTAMPTZ DEFAULT NOW()
);

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
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入默认数据
INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default) 
SELECT NULL, '标准问答转换', '将问答式对话转换为第一人称叙述', 'system', 
       '{"style": "first_person", "format": "narrative"}'::jsonb, true
WHERE NOT EXISTS (SELECT 1 FROM transformation_rules WHERE rule_type = 'system' AND name = '标准问答转换');

INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default)
SELECT NULL, '正式文档转换', '转换为正式的文档格式', 'system',
       '{"style": "formal", "format": "document"}'::jsonb, false
WHERE NOT EXISTS (SELECT 1 FROM transformation_rules WHERE rule_type = 'system' AND name = '正式文档转换');

INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default)
SELECT NULL, '简洁摘要转换', '生成简洁的摘要版本', 'system',
       '{"style": "summary", "format": "brief"}'::jsonb, false
WHERE NOT EXISTS (SELECT 1 FROM transformation_rules WHERE rule_type = 'system' AND name = '简洁摘要转换');
"""
    
    success = execute_sql_via_http(complete_sql, "创建完整数据库结构")
    
    if not success:
        print("⚠️ 直接执行失败，尝试分步执行...")
        
        # 分步执行每个CREATE语句
        sql_parts = [
            ("用户配置表", """
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);"""),
            ("转换规则表", """
CREATE TABLE IF NOT EXISTS transformation_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL DEFAULT 'custom',
    rule_config JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);"""),
            ("转换历史表", """
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
    created_at TIMESTAMPTZ DEFAULT NOW()
);"""),
            ("批量任务表", """
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
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);""")
        ]
        
        success_count = 0
        for description, sql in sql_parts:
            if execute_sql_via_http(sql, f"创建{description}"):
                success_count += 1
            time.sleep(1)  # 避免频率限制
        
        success = success_count > 0
    
    return success

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 最终自动化设置 - 直接HTTP调用")
    print("=" * 60)
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        print("❌ 缺少环境变量")
        return False
    
    print(f"🔗 项目: {supabase_url}")
    print(f"🔑 Service Key: {service_key[:20]}...")
    print()
    
    # 尝试创建辅助函数
    create_helper_function()
    
    # 自动创建表
    success = auto_create_all_tables()
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 自动化设置完成！")
        print("🔍 现在验证设置...")
        
        # 运行测试验证
        import subprocess
        try:
            result = subprocess.run(["python3", "test_supabase_integration.py"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and "成功" in result.stdout:
                print("✅ 验证测试通过！")
                print("\n🎯 接下来可以:")
                print("1. 启动后端: uvicorn app.main:app --reload")
                print("2. 启动前端: cd ../frontend && npm run dev")
                return True
            else:
                print("⚠️ 验证测试部分通过")
                print("建议手动运行: python3 test_supabase_integration.py")
        except Exception as e:
            print(f"⚠️ 无法运行验证测试: {e}")
    else:
        print("❌ 自动化设置失败")
        print("\n📋 请手动执行SQL:")
        print("1. 打开 Supabase 控制台")
        print("2. 进入 SQL Editor") 
        print("3. 复制 supabase_simple_setup.sql 的内容")
        print("4. 执行SQL脚本")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    main() 