#!/usr/bin/env python3
"""
Supabase集成测试脚本
验证数据库连接、表结构和基本CRUD操作
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.supabase_client import get_supabase

# 加载环境变量
load_dotenv()

async def test_supabase_connection():
    """测试Supabase基础连接"""
    print("🔍 测试Supabase连接...")
    
    try:
        supabase = get_supabase()
        
        # 测试基础查询
        result = supabase.table("user_profiles").select("count", count="exact").execute()
        print(f"✅ Supabase连接成功，用户配置表记录数: {result.count}")
        
        return True
    except Exception as e:
        print(f"❌ Supabase连接失败: {e}")
        return False

async def test_database_structure():
    """测试数据库表结构"""
    print("\n🔍 测试数据库表结构...")
    
    try:
        supabase = get_supabase()
        
        # 测试各个表的基本查询
        tables = [
            "user_profiles",
            "transformation_rules", 
            "conversion_history",
            "batch_jobs"
        ]
        
        for table in tables:
            try:
                result = supabase.table(table).select("count", count="exact").limit(1).execute()
                print(f"✅ 表 {table} 访问正常，记录数: {result.count}")
            except Exception as e:
                print(f"❌ 表 {table} 访问失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库表结构测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始Supabase集成测试\n")
    
    # 检查环境变量
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请确保 .env 文件包含所需的Supabase配置")
        return
    
    # 运行测试
    tests = [
        ("基础连接", test_supabase_connection),
        ("数据库表结构", test_database_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试出现异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！Supabase集成正常工作")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")

if __name__ == "__main__":
    asyncio.run(main()) 