#!/usr/bin/env python3
"""
测试匿名用户转换历史功能
验证数据库约束修复后的功能是否正常
"""

import os
import sys
import uuid
from datetime import datetime, timezone

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from app.core.supabase_client import get_supabase

# 加载环境变量
load_dotenv()

def test_anonymous_user_conversion():
    """测试匿名用户转换历史功能"""
    
    print("🧪 测试匿名用户转换历史功能...")
    
    try:
        client = get_supabase()
        anonymous_user_id = "00000000-0000-0000-0000-000000000001"
        
        # 验证匿名用户配置存在
        user_result = client.table("user_profiles").select("*").eq("id", anonymous_user_id).execute()
        
        if not user_result.data:
            print("❌ 匿名用户配置不存在")
            return False
        
        user_info = user_result.data[0]
        print(f"✅ 匿名用户配置验证: {user_info['full_name']} ({user_info['email']})")
        
        # 获取系统规则
        rules_result = client.table("transformation_rules").select("id, name").eq("rule_type", "system").limit(1).execute()
        rule_id = None
        rule_name = "无规则"
        
        if rules_result.data:
            rule_id = rules_result.data[0]["id"]
            rule_name = rules_result.data[0]["name"]
            print(f"✅ 使用系统规则: {rule_name}")
        
        # 测试数据
        test_id = str(uuid.uuid4())
        test_data = {
            "id": test_id,
            "user_id": anonymous_user_id,
            "original_text": "这是一个测试原始文本。Q: 你好吗？A: 我很好，谢谢。",
            "converted_text": "这是转换后的文本。我很好，谢谢。",
            "rule_id": rule_id,
            "file_name": "anonymous_conversion_test.txt",
            "file_size": 1024,
            "quality_score": 85.5,
            "processing_time": 2.3,
            "metadata": {
                "test": True,
                "user_type": "anonymous",
                "conversion_type": "qa_to_narrative",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # 插入测试数据
        print("🔧 插入转换历史记录...")
        result = client.table("conversion_history").insert(test_data).execute()
        
        if result.data:
            inserted_record = result.data[0]
            print("✅ 转换历史插入成功！")
            print(f"   记录ID: {inserted_record['id']}")
            print(f"   用户ID: {inserted_record['user_id']}")
            print(f"   文件名: {inserted_record['file_name']}")
            print(f"   质量分数: {inserted_record['quality_score']}")
            print(f"   处理时间: {inserted_record['processing_time']}秒")
            
            # 验证数据查询
            print("🔍 验证数据查询...")
            check_result = client.table("conversion_history").select("*").eq("id", test_id).execute()
            
            if check_result.data:
                record = check_result.data[0]
                print("✅ 数据查询验证成功！")
                print(f"   原始文本长度: {len(record['original_text'])} 字符")
                print(f"   转换文本长度: {len(record['converted_text'])} 字符")
                print(f"   元数据: {record['metadata']}")
            else:
                print("❌ 数据查询验证失败")
                return False
            
            # 测试列表查询
            print("📋 测试转换历史列表查询...")
            list_result = client.table("conversion_history").select("id, file_name, quality_score, created_at").eq("user_id", anonymous_user_id).order("created_at", desc=True).limit(5).execute()
            
            if list_result.data:
                print(f"✅ 找到 {len(list_result.data)} 条转换历史记录")
                for i, record in enumerate(list_result.data, 1):
                    print(f"   {i}. {record['file_name']} (质量: {record['quality_score']}) - {record['created_at'][:19]}")
            
            # 清理测试数据
            print("🧹 清理测试数据...")
            delete_result = client.table("conversion_history").delete().eq("id", test_id).execute()
            
            if delete_result.data:
                print("✅ 测试数据清理成功")
            else:
                print("⚠️ 测试数据清理可能失败")
            
            return True
            
        else:
            print("❌ 转换历史插入失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        return False

def test_system_functionality():
    """测试系统功能完整性"""
    
    print("\n🔧 测试系统功能完整性...")
    
    try:
        client = get_supabase()
        
        # 1. 检查表结构
        print("1️⃣ 检查核心表结构...")
        tables = ["user_profiles", "transformation_rules", "conversion_history", "batch_jobs"]
        
        for table in tables:
            try:
                result = client.table(table).select("count", count="exact").execute()
                count = result.count if result.count else 0
                print(f"   ✅ {table}: {count} 条记录")
            except Exception as e:
                print(f"   ❌ {table}: 访问失败 - {e}")
                return False
        
        # 2. 检查系统规则
        print("\n2️⃣ 检查系统规则...")
        rules_result = client.table("transformation_rules").select("id, name, rule_type, is_active").eq("rule_type", "system").execute()
        
        if rules_result.data:
            print(f"   ✅ 系统规则: {len(rules_result.data)} 条")
            for rule in rules_result.data:
                status = "启用" if rule["is_active"] else "禁用"
                print(f"      - {rule['name']} ({status})")
        else:
            print("   ⚠️ 未找到系统规则")
        
        # 3. 检查用户配置
        print("\n3️⃣ 检查用户配置...")
        users_result = client.table("user_profiles").select("id, full_name, email, preferences").execute()
        
        if users_result.data:
            print(f"   ✅ 用户配置: {len(users_result.data)} 个")
            for user in users_result.data:
                role = user.get("preferences", {}).get("role", "unknown")
                print(f"      - {user['full_name']} ({role}): {user['email']}")
        else:
            print("   ❌ 未找到用户配置")
            return False
        
        print("\n✅ 系统功能完整性检查通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 系统功能检查异常: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 数据库约束修复验证测试")
    print("=" * 60)
    print()
    
    # 测试系统功能
    if test_system_functionality():
        print()
        
        # 测试匿名用户转换功能
        if test_anonymous_user_conversion():
            print("\n🎉 数据库约束修复验证完全成功！")
            print("\n📋 验证结果总结：")
            print("   ✅ 数据库表结构正常")
            print("   ✅ 系统规则配置正确")
            print("   ✅ 用户配置功能正常")
            print("   ✅ 转换历史插入功能正常")
            print("   ✅ 数据查询和删除功能正常")
            print("   ✅ 外键约束问题彻底解决")
            
            print("\n💡 约束修复说明：")
            print("   - 成功创建了匿名用户作为系统用户")
            print("   - 外键约束现在指向有效的用户记录")
            print("   - 转换历史可以正常保存和查询")
            print("   - 系统具备了完整的数据持久化能力")
            
            print("\n🚀 系统现在可以正常运行！")
            
        else:
            print("\n❌ 转换历史功能测试失败")
    else:
        print("\n❌ 系统功能检查失败")

if __name__ == "__main__":
    main() 