#!/usr/bin/env python3
"""
立即创建Supabase表结构
使用现有的Supabase客户端
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.supabase_client import get_supabase

# 加载环境变量
load_dotenv()

def create_tables_directly():
    """直接创建表结构"""
    print("🚀 开始创建表结构...")
    
    try:
        supabase = get_supabase()
        print("✅ Supabase客户端连接成功")
        
        # 直接插入默认规则到不存在的表，这会自动显示错误
        # 我们可以通过错误信息了解表的状态
        
        print("\n🔧 尝试插入默认数据以测试表结构...")
        
        # 先尝试查询表，如果表不存在会报错
        try:
            result = supabase.table('transformation_rules').select('id').limit(1).execute()
            print("✅ transformation_rules 表已存在")
            tables_exist = True
        except Exception as e:
            print(f"❌ transformation_rules 表不存在: {e}")
            tables_exist = False
        
        if not tables_exist:
            print("\n💡 表不存在，需要手动创建")
            print("📋 请按以下步骤操作：")
            print("1. 打开 Supabase 控制台: https://app.supabase.com")
            print("2. 进入 SQL Editor")
            print("3. 复制并执行以下 SQL:")
            
            sql = """
-- 创建表结构
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

-- 插入默认规则
INSERT INTO transformation_rules (user_id, name, description, rule_type, rule_config, is_default) VALUES
(NULL, '标准问答转换', '将问答式对话转换为第一人称叙述', 'system', '{"style": "first_person", "format": "narrative"}', true),
(NULL, '正式文档转换', '转换为正式的文档格式', 'system', '{"style": "formal", "format": "document"}', false),
(NULL, '简洁摘要转换', '生成简洁的摘要版本', 'system', '{"style": "summary", "format": "brief"}', false);
"""
            print("\n" + "="*60)
            print(sql)
            print("="*60)
            
            return False
        else:
            print("✅ 表结构已存在，尝试插入默认数据...")
            
            # 检查是否已有默认规则
            existing_rules = supabase.table('transformation_rules').select('id').eq('rule_type', 'system').execute()
            
            if len(existing_rules.data) == 0:
                # 插入默认规则
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
                
                result = supabase.table('transformation_rules').insert(default_rules).execute()
                print(f"✅ 插入了 {len(result.data)} 条默认规则")
            else:
                print(f"✅ 已存在 {len(existing_rules.data)} 条系统规则，跳过插入")
            
            return True
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 立即创建Supabase表结构")
    print("="*50)
    
    if create_tables_directly():
        print("\n🎉 成功！现在运行测试验证：")
        print("python3 test_supabase_integration.py")
    else:
        print("\n⚠️ 需要手动创建表结构")
        print("请复制上面的SQL到Supabase控制台执行")
    
    print("="*50)

if __name__ == "__main__":
    main() 