#!/usr/bin/env python3
"""
真正的Supabase自动化设置脚本
直接使用HTTP请求创建表结构
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def create_table_via_api(supabase_url, service_key, table_name, sql):
    """通过API创建表"""
    print(f"🔧 创建表 {table_name}...")
    
    # 使用Supabase的SQL执行端点
    url = f"{supabase_url}/rest/v1/rpc/exec"
    
    headers = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "apikey": service_key
    }
    
    payload = {"sql": sql}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            print(f"✅ 表 {table_name} 创建成功")
            return True
        else:
            print(f"❌ 表 {table_name} 创建失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 表 {table_name} 创建失败: {e}")
        return False

def execute_raw_sql(supabase_url, service_key, sql, description):
    """执行原始SQL"""
    print(f"🔧 {description}...")
    
    # 直接使用PostgreSQL REST接口
    url = f"{supabase_url}/rest/v1/"
    
    headers = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "text/plain",
        "apikey": service_key,
        "Prefer": "return=minimal"
    }
    
    try:
        # 尝试多种方法
        methods = [
            # 方法1: 使用rpc端点
            (f"{supabase_url}/rest/v1/rpc/exec", {"sql": sql}),
            # 方法2: 使用query端点  
            (f"{supabase_url}/rest/v1/query", {"q": sql}),
        ]
        
        for url, payload in methods:
            try:
                if isinstance(payload, dict):
                    response = requests.post(url, json=payload, headers=headers)
                else:
                    response = requests.post(url, data=sql, headers=headers)
                
                if response.status_code in [200, 201, 204]:
                    print(f"✅ {description} - 成功")
                    return True
            except:
                continue
        
        print(f"❌ {description} - 所有方法都失败了")
        return False
        
    except Exception as e:
        print(f"❌ {description} - 失败: {e}")
        return False

def auto_setup_database():
    """自动化设置数据库"""
    print("🚀 开始真正的自动化数据库设置...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        print("❌ 缺少环境变量")
        return False
    
    print(f"🔗 项目URL: {supabase_url}")
    print(f"🔑 Service Key: {service_key[:20]}...\n")
    
    # 尝试直接创建表的SQL命令
    sql_commands = [
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
);
"""),
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
);
"""),
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
);
"""),
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
);
""")
    ]
    
    success_count = 0
    
    # 执行SQL命令
    for description, sql in sql_commands:
        if execute_raw_sql(supabase_url, service_key, sql.strip(), f"创建{description}"):
            success_count += 1
    
    # 插入默认数据
    default_data_sql = """
INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default) VALUES
(NULL, '标准问答转换', '将问答式对话转换为第一人称叙述', 'system', '{"style": "first_person", "format": "narrative"}', true),
(NULL, '正式文档转换', '转换为正式的文档格式', 'system', '{"style": "formal", "format": "document"}', false),
(NULL, '简洁摘要转换', '生成简洁的摘要版本', 'system', '{"style": "summary", "format": "brief"}', false)
ON CONFLICT DO NOTHING;
"""
    
    if execute_raw_sql(supabase_url, service_key, default_data_sql, "插入默认规则"):
        success_count += 1
    
    print(f"\n📊 设置结果: {success_count}/{len(sql_commands)+1} 操作成功")
    
    if success_count > 0:
        print("🎉 部分或全部设置成功！")
        return True
    else:
        print("❌ 所有自动化操作都失败了")
        print("\n💡 建议：使用手动方式")
        print("📋 请复制 supabase_simple_setup.sql 的内容到Supabase控制台执行")
        return False

def test_connection():
    """测试连接"""
    print("🔍 测试Supabase连接...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    url = f"{supabase_url}/rest/v1/"
    headers = {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Supabase连接成功")
            return True
        else:
            print(f"❌ 连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 Supabase 真正自动化设置")
    print("=" * 60)
    
    # 测试连接
    if not test_connection():
        print("❌ 连接测试失败，无法继续")
        return False
    
    print()
    
    # 自动化设置
    success = auto_setup_database()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 设置完成！接下来运行测试验证：")
        print("   python3 test_supabase_integration.py")
        print("\n如果测试失败，请手动执行SQL脚本：")
        print("   复制 supabase_simple_setup.sql 到Supabase控制台")
    else:
        print("❌ 自动化设置失败")
        print("📋 请手动执行以下操作：")
        print("1. 打开 Supabase 控制台: https://app.supabase.com")
        print("2. 进入 SQL Editor")
        print("3. 复制 supabase_simple_setup.sql 的内容")
        print("4. 执行SQL脚本")
        print("5. 运行测试: python3 test_supabase_integration.py")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    main() 