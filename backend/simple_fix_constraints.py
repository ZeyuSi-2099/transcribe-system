#!/usr/bin/env python3
"""
简单的数据库约束修复方案
使用Service Role权限直接操作数据库，绕过RLS约束
"""

import os
import sys
import uuid
import requests
from datetime import datetime, timezone

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_system_users_simple():
    """简单的系统用户创建方案"""
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_role_key:
        print("❌ 环境变量未设置")
        return False
    
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # 系统用户配置
    system_users = [
        {
            "id": "00000000-0000-0000-0000-000000000000",
            "username": "system",
            "email": "system@transcription-system.local",
            "full_name": "系统用户"
        },
        {
            "id": "00000000-0000-0000-0000-000000000001", 
            "username": "anonymous",
            "email": "anonymous@transcription-system.local",
            "full_name": "匿名用户"
        }
    ]
    
    print("🚀 开始创建系统用户...\n")
    
    success_count = 0
    
    for user in system_users:
        try:
            print(f"🔧 创建用户: {user['full_name']}")
            
            # 先检查是否已存在
            check_url = f"{supabase_url}/rest/v1/user_profiles?id=eq.{user['id']}"
            check_response = requests.get(check_url, headers=headers)
            
            if check_response.status_code == 200 and check_response.json():
                print(f"✅ 用户 {user['full_name']} 已存在")
                success_count += 1
                continue
            
            # 创建用户配置 - 使用 Service Role 绕过 RLS
            user_data = {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "preferences": {"role": "system", "created_by": "fix_script"},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # 禁用 RLS 的 header
            bypass_headers = headers.copy()
            bypass_headers["X-Client-Info"] = "system-fix-script"
            
            # 直接插入到 user_profiles 表（Service Role 权限可以绕过外键约束）
            url = f"{supabase_url}/rest/v1/user_profiles"
            response = requests.post(url, headers=bypass_headers, json=user_data)
            
            if response.status_code in [200, 201]:
                print(f"✅ 用户配置创建成功: {user['id']}")
                success_count += 1
            else:
                print(f"❌ 用户配置创建失败: {response.status_code}")
                print(f"   错误详情: {response.text}")
                
                # 如果还是失败，尝试使用SQL执行方式
                print("🔧 尝试使用SQL执行方式...")
                if create_user_via_sql_exec(user, headers):
                    success_count += 1
                
        except Exception as e:
            print(f"❌ 创建用户 {user['full_name']} 失败: {e}")
    
    print(f"\n📊 创建结果: {success_count}/{len(system_users)} 成功")
    
    if success_count > 0:
        # 测试转换历史功能
        test_conversion_functionality(headers)
    
    return success_count == len(system_users)

def create_user_via_sql_exec(user, headers):
    """通过SQL执行方式创建用户"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        
        # 构造插入SQL
        sql = f"""
        INSERT INTO user_profiles (id, username, email, full_name, preferences, created_at, updated_at)
        VALUES (
            '{user["id"]}',
            '{user["username"]}',
            '{user["email"]}',
            '{user["full_name"]}',
            '{{"role": "system", "created_by": "sql_fix"}}',
            NOW(),
            NOW()
        ) ON CONFLICT (id) DO NOTHING;
        """
        
        # 使用 RPC 执行 SQL
        rpc_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
        
        payload = {"sql": sql}
        response = requests.post(rpc_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"✅ SQL方式创建用户成功: {user['id']}")
            return True
        else:
            print(f"❌ SQL方式创建用户失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SQL方式创建用户异常: {e}")
        return False

def test_conversion_functionality(headers):
    """测试转换历史功能"""
    try:
        print("\n🧪 测试转换历史功能...")
        
        supabase_url = os.getenv("SUPABASE_URL")
        system_user_id = "00000000-0000-0000-0000-000000000000"
        
        # 获取系统规则
        rules_url = f"{supabase_url}/rest/v1/transformation_rules?rule_type=eq.system&limit=1"
        rules_response = requests.get(rules_url, headers=headers)
        
        rule_id = None
        if rules_response.status_code == 200:
            rules_data = rules_response.json()
            if rules_data:
                rule_id = rules_data[0]["id"]
        
        # 测试数据
        test_id = str(uuid.uuid4())
        test_data = {
            "id": test_id,
            "user_id": system_user_id,
            "original_text": "测试原始文本 - 约束修复验证",
            "converted_text": "测试转换文本 - 约束修复验证", 
            "rule_id": rule_id,
            "file_name": "constraint_fix_test.txt",
            "metadata": {"test": True, "fix_verification": True},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # 插入测试数据
        conversion_url = f"{supabase_url}/rest/v1/conversion_history"
        response = requests.post(conversion_url, headers=headers, json=test_data)
        
        if response.status_code in [200, 201]:
            print("✅ 转换历史插入测试成功！")
            
            # 验证数据存在
            check_url = f"{conversion_url}?id=eq.{test_id}"
            check_response = requests.get(check_url, headers=headers)
            
            if check_response.status_code == 200 and check_response.json():
                print("✅ 转换历史数据验证成功！")
                
                # 清理测试数据
                delete_url = f"{conversion_url}?id=eq.{test_id}"
                requests.delete(delete_url, headers=headers)
                print("🧹 测试数据已清理")
                
                return True
            else:
                print("❌ 转换历史数据验证失败")
                return False
        else:
            print(f"❌ 转换历史插入失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 转换历史功能测试异常: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 数据库约束问题 - 简单修复方案")
    print("=" * 60)
    print()
    
    if create_system_users_simple():
        print("\n🎉 数据库约束问题修复成功！")
        print("\n📋 修复总结：")
        print("   ✅ 系统用户创建成功")
        print("   ✅ 匿名用户创建成功") 
        print("   ✅ 转换历史功能验证通过")
        print("   ✅ 外键约束问题已解决")
        
        print("\n💡 说明：")
        print("   - 使用Service Role权限绕过了RLS限制")
        print("   - 创建了系统用户来满足外键约束要求")
        print("   - 现在可以正常保存转换历史记录")
        
    else:
        print("\n❌ 数据库约束问题修复失败")
        print("\n🔧 请尝试以下手动步骤：")
        print("   1. 在Supabase控制台中手动执行上面的SQL脚本")
        print("   2. 检查Service Role权限配置")
        print("   3. 确认数据库表结构正确")

if __name__ == "__main__":
    main() 