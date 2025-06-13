#!/usr/bin/env python3
"""
通过HTTP API创建系统用户
使用Supabase的HTTP API直接操作auth.users表
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class SystemUserCreator:
    """系统用户创建器"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not self.supabase_url or not self.service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    
    def create_auth_user_via_rpc(self, user_id: str, email: str, role: str) -> bool:
        """通过RPC创建auth.users记录"""
        try:
            # 使用自定义的RPC函数来插入auth.users
            rpc_url = f"{self.supabase_url}/rest/v1/rpc/create_system_user"
            
            headers = {
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            payload = {
                "user_id": user_id,
                "user_email": email,
                "user_role": role
            }
            
            response = requests.post(rpc_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                print(f"✅ 通过RPC创建用户成功: {user_id}")
                return True
            else:
                print(f"❌ RPC创建用户失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ RPC创建用户异常: {e}")
            return False
    
    def create_user_profile_via_http(self, user_id: str, username: str, email: str, full_name: str, role: str) -> bool:
        """通过HTTP API创建用户配置"""
        try:
            # 直接使用HTTP API插入user_profiles
            url = f"{self.supabase_url}/rest/v1/user_profiles"
            
            headers = {
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            data = {
                "id": user_id,
                "username": username,
                "email": email,
                "full_name": full_name,
                "preferences": {"role": role},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                print(f"✅ 用户配置创建成功: {user_id}")
                return True
            else:
                print(f"❌ 用户配置创建失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 用户配置创建异常: {e}")
            return False
    
    def test_conversion_via_http(self, user_id: str) -> bool:
        """通过HTTP API测试转换历史插入"""
        try:
            # 首先获取一个系统规则ID
            rules_url = f"{self.supabase_url}/rest/v1/transformation_rules?rule_type=eq.system&limit=1"
            headers = {
                "apikey": self.service_role_key,
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/json"
            }
            
            rules_response = requests.get(rules_url, headers=headers)
            rule_id = None
            
            if rules_response.status_code == 200:
                rules_data = rules_response.json()
                if rules_data:
                    rule_id = rules_data[0]["id"]
            
            # 测试插入转换历史
            test_id = "test-" + user_id
            conversion_url = f"{self.supabase_url}/rest/v1/conversion_history"
            
            test_data = {
                "id": test_id,
                "user_id": user_id,
                "original_text": f"测试原始文本 - {user_id}",
                "converted_text": f"测试转换文本 - {user_id}",
                "rule_id": rule_id,
                "file_name": f"test_{user_id}.txt",
                "metadata": {"test": True, "user_type": "system"},
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(conversion_url, headers=headers, json=test_data)
            
            if response.status_code in [200, 201]:
                print(f"✅ 转换历史测试成功: {user_id}")
                
                # 清理测试数据
                delete_url = f"{conversion_url}?id=eq.{test_id}"
                requests.delete(delete_url, headers=headers)
                
                return True
            else:
                print(f"❌ 转换历史测试失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 转换历史测试异常: {e}")
            return False

def create_rpc_function_sql():
    """生成创建RPC函数的SQL"""
    sql = """
-- 创建系统用户的RPC函数
CREATE OR REPLACE FUNCTION create_system_user(
    user_id UUID,
    user_email TEXT,
    user_role TEXT
) RETURNS VOID AS $$
BEGIN
    -- 插入到auth.users表
    INSERT INTO auth.users (
        id,
        instance_id,
        aud,
        role,
        email,
        encrypted_password,
        email_confirmed_at,
        raw_app_meta_data,
        raw_user_meta_data,
        created_at,
        updated_at
    ) VALUES (
        user_id,
        '00000000-0000-0000-0000-000000000000',
        'authenticated',
        'authenticated', 
        user_email,
        '',
        NOW(),
        jsonb_build_object('provider', user_role, 'providers', ARRAY[user_role], 'role', user_role),
        jsonb_build_object('full_name', user_role || '用户', 'role', user_role),
        NOW(),
        NOW()
    ) ON CONFLICT (id) DO NOTHING;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
"""
    return sql

def main():
    """主函数"""
    print("🚀 开始创建系统用户...\n")
    
    creator = SystemUserCreator()
    
    # 系统用户和匿名用户的配置
    users_to_create = [
        {
            "id": "00000000-0000-0000-0000-000000000000",
            "username": "system",
            "email": "system@transcription-system.local",
            "full_name": "系统用户",
            "role": "system"
        },
        {
            "id": "00000000-0000-0000-0000-000000000001",
            "username": "anonymous",
            "email": "anonymous@transcription-system.local",
            "full_name": "匿名用户",
            "role": "anonymous"
        }
    ]
    
    print("📝 请先在Supabase控制台执行以下SQL创建RPC函数:")
    print("=" * 60)
    print(create_rpc_function_sql())
    print("=" * 60)
    print()
    
    input("按回车键继续（确认已创建RPC函数）...")
    print()
    
    # 创建用户
    success_count = 0
    for user in users_to_create:
        print(f"🔧 创建用户: {user['full_name']} ({user['id']})")
        
        # 1. 通过RPC创建auth.users记录
        if creator.create_auth_user_via_rpc(user["id"], user["email"], user["role"]):
            # 2. 创建用户配置
            if creator.create_user_profile_via_http(
                user["id"], 
                user["username"], 
                user["email"], 
                user["full_name"], 
                user["role"]
            ):
                # 3. 测试转换历史功能
                if creator.test_conversion_via_http(user["id"]):
                    success_count += 1
                    print(f"✅ 用户 {user['full_name']} 创建并测试成功\n")
                else:
                    print(f"⚠️ 用户 {user['full_name']} 创建成功但测试失败\n")
            else:
                print(f"❌ 用户 {user['full_name']} 配置创建失败\n")
        else:
            print(f"❌ 用户 {user['full_name']} auth记录创建失败\n")
    
    if success_count == len(users_to_create):
        print("🎉 所有系统用户创建成功！")
        print("\n📋 创建总结：")
        print("   ✅ 系统用户 (00000000-0000-0000-0000-000000000000)")
        print("   ✅ 匿名用户 (00000000-0000-0000-0000-000000000001)")
        print("\n💡 现在可以使用这些用户ID进行数据库操作，外键约束问题已解决！")
    else:
        print(f"⚠️ 部分用户创建失败，成功: {success_count}/{len(users_to_create)}")

if __name__ == "__main__":
    main() 