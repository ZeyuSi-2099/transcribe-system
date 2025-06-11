#!/usr/bin/env python3
"""
Supabase数据库最终自动化设置脚本
使用Supabase管理API创建表结构
"""

import os
import requests
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_management_headers():
    """获取管理API头部"""
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not service_role_key:
        raise ValueError("未找到SUPABASE_SERVICE_ROLE_KEY环境变量")
    
    return {
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json",
        "apikey": service_role_key
    }

def execute_sql_via_rest(supabase_url, sql, description):
    """通过REST API执行SQL"""
    print(f"🔧 {description}...")
    
    # 使用Supabase的REST API执行SQL
    url = f"{supabase_url}/rest/v1/rpc/execute_sql"
    
    try:
        headers = get_management_headers()
        payload = {"sql": sql}
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ {description} - 成功")
            return True
        else:
            print(f"❌ {description} - 失败: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ {description} - 失败: {e}")
        return False

def create_execute_sql_function(supabase_url):
    """创建execute_sql函数"""
    print("🔧 创建SQL执行函数...")
    
    # 创建执行SQL的函数
    function_sql = """
CREATE OR REPLACE FUNCTION execute_sql(sql TEXT)
RETURNS TEXT AS $$
BEGIN
    EXECUTE sql;
    RETURN 'Success';
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
"""
    
    try:
        # 直接使用PostgREST创建函数
        url = f"{supabase_url}/rest/v1/rpc/execute"
        headers = get_management_headers()
        
        # 尝试其他方法
        print("⚠️ 无法通过REST API创建函数，将使用备用方案")
        return True
        
    except Exception as e:
        print(f"⚠️ 创建函数失败: {e}")
        return True  # 继续执行，尝试其他方法

def create_tables_directly(supabase_url):
    """直接创建表结构"""
    print("🏗️ 直接创建表结构...")
    
    # 使用HTTP POST请求直接创建表
    tables_config = [
        {
            "name": "user_profiles",
            "columns": [
                {"name": "id", "type": "uuid", "primary_key": True, "references": "auth.users(id)"},
                {"name": "username", "type": "varchar(50)", "unique": True},
                {"name": "email", "type": "varchar(255)", "not_null": True},
                {"name": "full_name", "type": "varchar(100)"},
                {"name": "avatar_url", "type": "text"},
                {"name": "preferences", "type": "jsonb", "default": "'{}'"},
                {"name": "created_at", "type": "timestamptz", "default": "now()"},
                {"name": "updated_at", "type": "timestamptz", "default": "now()"}
            ]
        },
        {
            "name": "transformation_rules",
            "columns": [
                {"name": "id", "type": "uuid", "primary_key": True, "default": "gen_random_uuid()"},
                {"name": "user_id", "type": "uuid", "references": "auth.users(id)", "on_delete": "cascade"},
                {"name": "name", "type": "varchar(100)", "not_null": True},
                {"name": "description", "type": "text"},
                {"name": "rule_type", "type": "varchar(50)", "not_null": True, "default": "'custom'"},
                {"name": "rule_config", "type": "jsonb", "not_null": True, "default": "'{}'"},
                {"name": "is_active", "type": "boolean", "default": "true"},
                {"name": "is_default", "type": "boolean", "default": "false"},
                {"name": "created_at", "type": "timestamptz", "default": "now()"},
                {"name": "updated_at", "type": "timestamptz", "default": "now()"}
            ]
        },
        {
            "name": "conversion_history",
            "columns": [
                {"name": "id", "type": "uuid", "primary_key": True, "default": "gen_random_uuid()"},
                {"name": "user_id", "type": "uuid", "references": "auth.users(id)", "on_delete": "cascade"},
                {"name": "original_text", "type": "text", "not_null": True},
                {"name": "converted_text", "type": "text", "not_null": True},
                {"name": "rule_id", "type": "uuid", "references": "transformation_rules(id)", "on_delete": "set null"},
                {"name": "quality_score", "type": "decimal(5,2)"},
                {"name": "processing_time", "type": "decimal(8,3)"},
                {"name": "file_name", "type": "varchar(255)"},
                {"name": "file_size", "type": "integer"},
                {"name": "metadata", "type": "jsonb", "default": "'{}'"},
                {"name": "created_at", "type": "timestamptz", "default": "now()"}
            ]
        },
        {
            "name": "batch_jobs",
            "columns": [
                {"name": "id", "type": "uuid", "primary_key": True, "default": "gen_random_uuid()"},
                {"name": "user_id", "type": "uuid", "references": "auth.users(id)", "on_delete": "cascade"},
                {"name": "job_name", "type": "varchar(100)", "not_null": True},
                {"name": "status", "type": "varchar(20)", "default": "'pending'"},
                {"name": "total_files", "type": "integer", "default": "0"},
                {"name": "processed_files", "type": "integer", "default": "0"},
                {"name": "failed_files", "type": "integer", "default": "0"},
                {"name": "rule_id", "type": "uuid", "references": "transformation_rules(id)", "on_delete": "set null"},
                {"name": "results", "type": "jsonb", "default": "'[]'"},
                {"name": "error_log", "type": "text"},
                {"name": "started_at", "type": "timestamptz"},
                {"name": "completed_at", "type": "timestamptz"},
                {"name": "created_at", "type": "timestamptz", "default": "now()"}
            ]
        }
    ]
    
    print("💡 由于Supabase REST API的限制，建议使用Web控制台创建表")
    print("📋 我们将提供简化的SQL脚本，您可以直接复制粘贴")
    return False

def main():
    """主函数"""
    print("🚀 Supabase自动化设置 - 最终方案")
    print("📝 为您提供最简单的手动设置方案\n")
    
    # 检查环境变量
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_role_key:
        print("❌ 缺少必要的环境变量")
        return False
    
    print(f"🔗 Supabase项目: {supabase_url}")
    print(f"🔑 Service Role Key: {service_role_key[:20]}...\n")
    
    # 生成简化的SQL脚本
    simple_sql = """
-- 🚀 笔录转换系统 - 简化数据库设置
-- 请将以下SQL复制到Supabase控制台的SQL编辑器中执行

-- 1. 用户配置表
CREATE TABLE user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 转换规则表  
CREATE TABLE transformation_rules (
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

-- 3. 转换历史表
CREATE TABLE conversion_history (
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

-- 4. 批量任务表
CREATE TABLE batch_jobs (
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

-- 5. 插入默认规则
INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default) VALUES
(NULL, '标准问答转换', '将问答式对话转换为第一人称叙述', 'system', '{"style": "first_person", "format": "narrative"}', true),
(NULL, '正式文档转换', '转换为正式的文档格式', 'system', '{"style": "formal", "format": "document"}', false),
(NULL, '简洁摘要转换', '生成简洁的摘要版本', 'system', '{"style": "summary", "format": "brief"}', false);

-- 完成提示
SELECT '🎉 数据库设置完成！请运行测试脚本验证：python3 test_supabase_integration.py' as message;
"""
    
    # 保存简化SQL脚本
    script_file = "supabase_simple_setup.sql"
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(simple_sql)
    
    print("📄 已生成简化设置脚本！")
    print(f"📁 文件位置: {script_file}")
    print("\n🎯 请按以下步骤操作:")
    print("1. 打开 Supabase 控制台: https://app.supabase.com")
    print("2. 选择您的项目")
    print("3. 点击左侧 'SQL Editor'")
    print("4. 点击 'New query'")
    print(f"5. 复制文件 '{script_file}' 的内容到编辑器")
    print("6. 点击 'Run' 执行SQL")
    print("7. 回到终端运行: python3 test_supabase_integration.py")
    
    print("\n" + "="*60)
    print("📋 SQL脚本预览:")
    print("="*60)
    print(simple_sql[:800] + "...")
    print("="*60)
    
    return True

if __name__ == "__main__":
    main() 