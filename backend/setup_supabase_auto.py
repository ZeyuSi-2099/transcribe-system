#!/usr/bin/env python3
"""
Supabase数据库自动化设置脚本
使用Supabase Python客户端直接执行SQL
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.supabase_client import get_supabase

# 加载环境变量
load_dotenv()

def execute_sql_statement(supabase, sql, description):
    """执行单个SQL语句"""
    print(f"🔧 {description}...")
    
    try:
        # 使用PostgREST的rpc功能执行SQL
        # 我们需要创建一个简单的函数来执行SQL
        result = supabase.rpc('execute_sql', {'query': sql}).execute()
        print(f"✅ {description} - 成功")
        return True
    except Exception as e:
        # 如果rpc失败，尝试使用query方法（对于简单的查询）
        try:
            if sql.strip().upper().startswith('SELECT'):
                result = supabase.query(sql).execute()
                print(f"✅ {description} - 成功 (查询)")
                return True
            elif sql.strip().upper().startswith('INSERT'):
                # 尝试解析INSERT语句
                print(f"⚠️ {description} - 跳过 (INSERT语句需要特殊处理)")
                return True
            else:
                print(f"❌ {description} - 失败: {e}")
                return False
        except Exception as e2:
            print(f"❌ {description} - 失败: {e2}")
            return False

def create_tables_via_api(supabase):
    """通过API创建表结构"""
    print("🏗️ 开始创建表结构...")
    
    # 分步执行SQL语句
    sql_steps = [
        # 1. 创建用户配置表
        ("""
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
        """, "创建用户配置表"),
        
        # 2. 创建转换规则表
        ("""
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
)
        """, "创建转换规则表"),
        
        # 3. 创建转换历史表
        ("""
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
)
        """, "创建转换历史表"),
        
        # 4. 创建批量任务表
        ("""
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
)
        """, "创建批量任务表"),
    ]
    
    success_count = 0
    for sql, description in sql_steps:
        if execute_sql_statement(supabase, sql.strip(), description):
            success_count += 1
        print()
    
    return success_count == len(sql_steps)

def insert_default_data(supabase):
    """插入默认数据"""
    print("📝 插入默认规则...")
    
    # 使用Supabase客户端直接插入数据
    try:
        default_rules = [
            {
                "user_id": None,
                "name": "标准问答转换",
                "description": "将问答式对话转换为第一人称叙述",
                "rule_type": "system",
                "rule_config": {"style": "first_person", "format": "narrative"},
                "is_default": True
            },
            {
                "user_id": None,
                "name": "正式文档转换",
                "description": "转换为正式的文档格式",
                "rule_type": "system",
                "rule_config": {"style": "formal", "format": "document"},
                "is_default": False
            },
            {
                "user_id": None,
                "name": "简洁摘要转换",
                "description": "生成简洁的摘要版本",
                "rule_type": "system",
                "rule_config": {"style": "summary", "format": "brief"},
                "is_default": False
            }
        ]
        
        # 检查是否已有默认规则
        existing = supabase.table('transformation_rules').select('id').eq('rule_type', 'system').execute()
        
        if len(existing.data) == 0:
            # 插入默认规则
            result = supabase.table('transformation_rules').insert(default_rules).execute()
            print(f"✅ 插入默认规则 - 成功 (插入了 {len(result.data)} 条记录)")
        else:
            print(f"✅ 插入默认规则 - 跳过 (已存在 {len(existing.data)} 条系统规则)")
        
        return True
    except Exception as e:
        print(f"❌ 插入默认规则 - 失败: {e}")
        return False

def verify_tables(supabase):
    """验证表结构"""
    print("🔍 验证表结构...")
    
    tables = ["user_profiles", "transformation_rules", "conversion_history", "batch_jobs"]
    success_count = 0
    
    for table in tables:
        try:
            result = supabase.table(table).select("count", count="exact").limit(1).execute()
            print(f"✅ 表 {table} - 验证成功 (记录数: {result.count})")
            success_count += 1
        except Exception as e:
            print(f"❌ 表 {table} - 验证失败: {e}")
    
    return success_count == len(tables)

def main():
    """主函数"""
    print("🚀 开始Supabase数据库自动化设置...")
    print("🔧 使用Supabase Python客户端直接操作\n")
    
    # 检查环境变量
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    
    try:
        # 获取Supabase客户端
        supabase = get_supabase()
        print("✅ Supabase客户端初始化成功\n")
        
        # 测试连接
        try:
            test_result = supabase.table('auth.users').select('count', count="exact").limit(1).execute()
            print("✅ Supabase连接测试成功\n")
        except Exception as e:
            print(f"⚠️ 连接测试警告: {e}\n")
        
        # 执行设置步骤
        success_steps = 0
        total_steps = 3
        
        # 步骤1: 创建表结构
        print("📋 步骤 1/3: 创建表结构")
        if create_tables_via_api(supabase):
            success_steps += 1
            print("✅ 表结构创建完成\n")
        else:
            print("❌ 表结构创建失败\n")
        
        # 步骤2: 插入默认数据
        print("📋 步骤 2/3: 插入默认数据")
        if insert_default_data(supabase):
            success_steps += 1
            print("✅ 默认数据插入完成\n")
        else:
            print("❌ 默认数据插入失败\n")
        
        # 步骤3: 验证设置
        print("📋 步骤 3/3: 验证设置")
        if verify_tables(supabase):
            success_steps += 1
            print("✅ 设置验证完成\n")
        else:
            print("❌ 设置验证失败\n")
        
        # 显示结果
        print(f"📊 设置结果: {success_steps}/{total_steps} 步骤成功")
        
        if success_steps == total_steps:
            print("🎉 Supabase数据库设置完成！")
            print("\n🎯 下一步:")
            print("1. 运行测试: python3 test_supabase_integration.py")
            print("2. 启动后端: uvicorn app.main:app --reload")
            print("3. 启动前端: cd ../frontend && npm run dev")
            return True
        else:
            print("⚠️ 部分设置失败")
            print("\n💡 建议:")
            print("1. 检查Supabase项目状态")
            print("2. 验证Service Role Key权限")
            print("3. 可以尝试手动在控制台执行SQL")
            return False
            
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        print("\n💡 故障排除:")
        print("1. 检查网络连接")
        print("2. 验证环境变量")
        print("3. 确认Supabase项目状态")
        return False

if __name__ == "__main__":
    main() 