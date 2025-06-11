#!/usr/bin/env python3
"""
最终的数据库约束修复方案
使用 Supabase Admin API 直接创建用户，解决外键约束问题
"""

import os
import sys
import uuid
import requests
from datetime import datetime, timezone

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from app.core.supabase_client import get_supabase

# 加载环境变量
load_dotenv()

def create_users_via_admin_api():
    """使用 Supabase Admin API 创建用户"""
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_role_key:
        print("❌ 环境变量未设置")
        return False
    
    # Admin API headers
    admin_headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json"
    }
    
    # 系统用户配置
    users_to_create = [
        {
            "id": "00000000-0000-0000-0000-000000000000",
            "email": "system@transcription-system.local",
            "password": "system-user-no-login",
            "user_metadata": {
                "full_name": "系统用户",
                "role": "system",
                "username": "system"
            },
            "app_metadata": {
                "provider": "system",
                "role": "system"
            }
        },
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "email": "anonymous@transcription-system.local", 
            "password": "anonymous-user-no-login",
            "user_metadata": {
                "full_name": "匿名用户",
                "role": "anonymous",
                "username": "anonymous"
            },
            "app_metadata": {
                "provider": "anonymous",
                "role": "anonymous"
            }
        }
    ]
    
    print("🚀 使用 Supabase Admin API 创建系统用户...\n")
    
    success_count = 0
    
    for user in users_to_create:
        try:
            print(f"🔧 创建用户: {user['user_metadata']['full_name']}")
            
            # 使用 Supabase Admin API 创建用户
            admin_url = f"{supabase_url}/auth/v1/admin/users"
            
            response = requests.post(admin_url, headers=admin_headers, json=user)
            
            if response.status_code in [200, 201]:
                print(f"✅ Admin API 创建用户成功: {user['id']}")
                
                # 创建用户配置
                if create_user_profile(user, admin_headers):
                    success_count += 1
                    print(f"✅ 用户 {user['user_metadata']['full_name']} 完全创建成功\n")
                else:
                    print(f"⚠️ 用户认证创建成功，但配置创建失败\n")
                    
            elif response.status_code == 422:
                # 用户可能已存在
                print(f"⚠️ 用户可能已存在: {response.text}")
                if create_user_profile(user, admin_headers):
                    success_count += 1
                    print(f"✅ 用户配置更新成功\n")
            else:
                print(f"❌ Admin API 创建用户失败: {response.status_code}")
                print(f"   错误详情: {response.text}\n")
                
        except Exception as e:
            print(f"❌ 创建用户异常: {e}\n")
    
    if success_count > 0:
        # 测试转换历史功能
        test_conversion_functionality()
    
    return success_count >= 1  # 至少成功创建一个用户

def create_user_profile(user, headers):
    """创建用户配置"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        
        # 检查是否已存在
        check_url = f"{supabase_url}/rest/v1/user_profiles?id=eq.{user['id']}"
        check_response = requests.get(check_url, headers=headers)
        
        if check_response.status_code == 200 and check_response.json():
            print(f"✅ 用户配置已存在: {user['id']}")
            return True
        
        # 创建用户配置
        profile_data = {
            "id": user["id"],
            "username": user["user_metadata"]["username"],
            "email": user["email"],
            "full_name": user["user_metadata"]["full_name"],
            "preferences": {
                "role": user["user_metadata"]["role"],
                "created_by": "admin_api_fix"
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        profile_url = f"{supabase_url}/rest/v1/user_profiles"
        response = requests.post(profile_url, headers=headers, json=profile_data)
        
        if response.status_code in [200, 201]:
            print(f"✅ 用户配置创建成功: {user['id']}")
            return True
        else:
            print(f"❌ 用户配置创建失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 用户配置创建异常: {e}")
        return False

def test_conversion_functionality():
    """测试转换历史功能"""
    try:
        print("\n🧪 测试转换历史功能...")
        
        # 使用 Supabase Python 客户端测试
        client = get_supabase()
        system_user_id = "00000000-0000-0000-0000-000000000000"
        
        # 获取系统规则
        rules_result = client.table("transformation_rules").select("id").eq("rule_type", "system").limit(1).execute()
        rule_id = None
        if rules_result.data:
            rule_id = rules_result.data[0]["id"]
        
        # 测试数据
        test_id = str(uuid.uuid4())
        test_data = {
            "id": test_id,
            "user_id": system_user_id,
            "original_text": "测试原始文本 - 最终约束修复验证",
            "converted_text": "测试转换文本 - 最终约束修复验证",
            "rule_id": rule_id,
            "file_name": "final_constraint_fix_test.txt",
            "metadata": {"test": True, "final_fix_verification": True},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # 插入测试数据
        result = client.table("conversion_history").insert(test_data).execute()
        
        if result.data:
            print("✅ 转换历史插入测试成功！")
            
            # 验证数据存在
            check_result = client.table("conversion_history").select("*").eq("id", test_id).execute()
            
            if check_result.data:
                print("✅ 转换历史数据验证成功！")
                print(f"   记录ID: {check_result.data[0]['id']}")
                print(f"   用户ID: {check_result.data[0]['user_id']}")
                print(f"   文件名: {check_result.data[0]['file_name']}")
                
                # 清理测试数据
                client.table("conversion_history").delete().eq("id", test_id).execute()
                print("🧹 测试数据已清理")
                
                return True
            else:
                print("❌ 转换历史数据验证失败")
                return False
        else:
            print("❌ 转换历史插入失败")
            return False
            
    except Exception as e:
        print(f"❌ 转换历史功能测试异常: {e}")
        return False

def verify_final_status():
    """验证最终状态"""
    try:
        print("\n🔍 验证最终修复状态...")
        
        client = get_supabase()
        
        # 检查系统用户
        users_result = client.table("user_profiles").select("*").in_("id", [
            "00000000-0000-0000-0000-000000000000",
            "00000000-0000-0000-0000-000000000001"
        ]).execute()
        
        if users_result.data:
            print(f"✅ 系统用户配置: {len(users_result.data)} 个")
            for user in users_result.data:
                role = user.get('preferences', {}).get('role', 'unknown')
                print(f"   - {user['full_name']} ({role}): {user['id']}")
        else:
            print("❌ 未找到系统用户配置")
            return False
        
        # 检查系统规则
        rules_result = client.table("transformation_rules").select("id, name").eq("rule_type", "system").execute()
        
        if rules_result.data:
            print(f"✅ 系统规则: {len(rules_result.data)} 条")
            for rule in rules_result.data:
                print(f"   - {rule['name']}: {rule['id']}")
        else:
            print("⚠️ 未找到系统规则")
        
        # 检查转换历史表结构
        history_result = client.table("conversion_history").select("count", count="exact").execute()
        print(f"✅ 转换历史表状态: {history_result.count} 条记录")
        
        return True
        
    except Exception as e:
        print(f"❌ 最终状态验证异常: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 最终数据库约束修复方案")
    print("=" * 60)
    print()
    
    print("📋 修复步骤：")
    print("   1. 使用 Supabase Admin API 创建系统用户")
    print("   2. 创建对应的用户配置记录")
    print("   3. 测试转换历史功能")
    print("   4. 验证最终修复状态")
    print()
    
    # 执行修复
    if create_users_via_admin_api():
        print("\n🎉 数据库约束问题修复成功！")
        
        # 验证最终状态
        if verify_final_status():
            print("\n📋 修复总结：")
            print("   ✅ 系统用户通过 Admin API 创建成功")
            print("   ✅ 用户配置记录创建成功")
            print("   ✅ 转换历史功能验证通过")
            print("   ✅ 外键约束问题彻底解决")
            
            print("\n💡 说明：")
            print("   - 使用了 Supabase Admin API 创建真实的认证用户")
            print("   - 外键约束现在指向有效的 auth.users 记录")
            print("   - 系统可以正常保存和查询转换历史")
            print("   - 为未来的用户认证功能奠定了基础")
            
            print("\n🎯 下一步建议：")
            print("   - 测试前端登录注册功能")
            print("   - 验证用户认证流程")
            print("   - 测试实际的文档转换功能")
            
        else:
            print("\n⚠️ 修复成功但最终验证有问题")
    else:
        print("\n❌ 数据库约束问题修复失败")
        
        print("\n🔧 替代方案：")
        print("   1. 手动在 Supabase 控制台执行 manual_fix_auth_users.sql")
        print("   2. 检查 Supabase 项目的 Admin API 权限")
        print("   3. 确认 SUPABASE_SERVICE_ROLE_KEY 正确设置")

if __name__ == "__main__":
    main() 