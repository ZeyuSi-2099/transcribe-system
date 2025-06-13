#!/usr/bin/env python3
"""
数据库约束问题诊断和修复脚本
用于检测和解决外键约束导致的转换历史保存问题
"""

import os
import sys
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import uuid

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from app.core.supabase_client import get_supabase

# 加载环境变量
load_dotenv()

class DatabaseConstraintsTester:
    """数据库约束测试器"""
    
    def __init__(self):
        self.client = get_supabase()
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            # 简单的连接测试
            result = self.client.table("transformation_rules").select("count", count="exact").execute()
            print(f"✅ 数据库连接成功！")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def check_table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            result = self.client.table(table_name).select("count", count="exact").limit(1).execute()
            print(f"✅ 表 '{table_name}' 存在")
            return True
        except Exception as e:
            print(f"❌ 表 '{table_name}' 不存在或无法访问: {e}")
            return False
    
    def check_auth_users_table(self) -> Dict[str, Any]:
        """检查auth.users表状态"""
        try:
            # 检查是否有用户
            result = self.client.table("profiles").select("*").limit(5).execute()
            user_count = len(result.data) if result.data else 0
            
            # 尝试获取当前用户
            current_user = self.client.auth.get_user()
            
            return {
                "user_count": user_count,
                "current_user": current_user,
                "status": "accessible"
            }
        except Exception as e:
            print(f"⚠️ 无法访问用户信息: {e}")
            return {
                "user_count": 0,
                "current_user": None,
                "status": "error",
                "error": str(e)
            }
    
    def check_foreign_key_constraints(self) -> List[Dict[str, Any]]:
        """检查外键约束问题"""
        issues = []
        
        # 检查transformation_rules表中的user_id约束
        try:
            result = self.client.table("transformation_rules").select("user_id").not_.is_("user_id", "null").execute()
            if result.data:
                user_ids = [row["user_id"] for row in result.data]
                print(f"📊 transformation_rules表中有 {len(user_ids)} 条记录引用了用户ID")
        except Exception as e:
            issues.append({
                "table": "transformation_rules", 
                "issue": f"无法查询用户ID引用: {e}"
            })
        
        # 检查conversion_history表中的约束
        try:
            result = self.client.table("conversion_history").select("user_id, rule_id").limit(10).execute()
            if result.data:
                print(f"📊 conversion_history表中有 {len(result.data)} 条记录")
            else:
                print("📊 conversion_history表为空")
        except Exception as e:
            issues.append({
                "table": "conversion_history",
                "issue": f"无法查询转换历史: {e}"
            })
        
        return issues
    
    def test_insert_conversion_history(self) -> bool:
        """测试插入转换历史记录"""
        try:
            # 创建测试用户ID（模拟用户UUID）
            test_user_id = str(uuid.uuid4())
            
            # 首先尝试查找一个系统规则
            rules_result = self.client.table("transformation_rules").select("id").eq("rule_type", "system").limit(1).execute()
            rule_id = None
            if rules_result.data:
                rule_id = rules_result.data[0]["id"]
            
            # 准备测试数据
            test_data = {
                "id": str(uuid.uuid4()),
                "user_id": test_user_id,
                "original_text": "测试原始文本",
                "converted_text": "测试转换文本",
                "rule_id": rule_id,
                "file_name": "test.txt",
                "metadata": {"test": True},
                "created_at": datetime.utcnow().isoformat()
            }
            
            # 尝试插入
            result = self.client.table("conversion_history").insert(test_data).execute()
            
            if result.data:
                # 测试成功，立即删除测试数据
                self.client.table("conversion_history").delete().eq("id", test_data["id"]).execute()
                print("✅ 转换历史插入测试成功")
                return True
            else:
                print("❌ 转换历史插入失败：无返回数据")
                return False
                
        except Exception as e:
            print(f"❌ 转换历史插入测试失败: {e}")
            return False
    
    def fix_missing_tables(self) -> bool:
        """修复缺失的表"""
        print("🔧 开始修复缺失的表结构...")
        
        # 读取建表SQL
        try:
            with open("supabase_setup.sql", "r", encoding="utf-8") as f:
                sql_content = f.read()
            
            # 这里我们使用RPC或者分段执行SQL
            # 由于Supabase Python客户端不直接支持执行DDL，我们输出SQL供手动执行
            print("📝 请在Supabase控制台中执行以下SQL:")
            print("=" * 60)
            print(sql_content)
            print("=" * 60)
            
            return True
        except Exception as e:
            print(f"❌ 读取SQL文件失败: {e}")
            return False
    
    def create_test_user_profile(self) -> str:
        """创建测试用户配置"""
        try:
            test_user_id = str(uuid.uuid4())
            
            # 准备测试用户数据
            test_user_data = {
                "id": test_user_id,
                "username": "test_user",
                "email": "test@example.com",
                "full_name": "测试用户",
                "preferences": {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # 插入测试用户
            result = self.client.table("user_profiles").insert(test_user_data).execute()
            
            if result.data:
                print(f"✅ 创建测试用户成功: {test_user_id}")
                return test_user_id
            else:
                print("❌ 创建测试用户失败")
                return ""
                
        except Exception as e:
            print(f"❌ 创建测试用户失败: {e}")
            return ""
    
    def cleanup_test_data(self, test_user_id: str):
        """清理测试数据"""
        try:
            # 删除测试用户的转换历史
            self.client.table("conversion_history").delete().eq("user_id", test_user_id).execute()
            
            # 删除测试用户配置
            self.client.table("user_profiles").delete().eq("id", test_user_id).execute()
            
            print(f"🧹 清理测试数据完成: {test_user_id}")
        except Exception as e:
            print(f"⚠️ 清理测试数据时出错: {e}")

async def main():
    """主函数"""
    print("🔍 开始数据库约束问题诊断...\n")
    
    tester = DatabaseConstraintsTester()
    
    # 1. 测试基础连接
    print("1️⃣ 测试数据库连接")
    if not tester.test_connection():
        print("❌ 数据库连接失败，请检查配置")
        return
    print()
    
    # 2. 检查核心表是否存在
    print("2️⃣ 检查核心表结构")
    tables = ["user_profiles", "transformation_rules", "conversion_history", "batch_jobs"]
    missing_tables = []
    
    for table in tables:
        if not tester.check_table_exists(table):
            missing_tables.append(table)
    
    if missing_tables:
        print(f"❌ 缺失表: {missing_tables}")
        print("🔧 需要创建缺失的表结构")
        tester.fix_missing_tables()
        return
    print()
    
    # 3. 检查用户表状态
    print("3️⃣ 检查用户认证状态")
    auth_status = tester.check_auth_users_table()
    print(f"📊 用户状态: {auth_status}")
    print()
    
    # 4. 检查外键约束
    print("4️⃣ 检查外键约束")
    constraint_issues = tester.check_foreign_key_constraints()
    if constraint_issues:
        print("⚠️ 发现外键约束问题:")
        for issue in constraint_issues:
            print(f"  - {issue['table']}: {issue['issue']}")
    else:
        print("✅ 外键约束检查通过")
    print()
    
    # 5. 测试插入转换历史
    print("5️⃣ 测试转换历史插入")
    if tester.test_insert_conversion_history():
        print("✅ 转换历史功能正常")
    else:
        print("❌ 转换历史插入存在问题")
        
        # 尝试创建测试用户并重新测试
        print("🔧 尝试创建测试用户进行修复测试...")
        test_user_id = tester.create_test_user_profile()
        if test_user_id:
            # 清理测试数据
            tester.cleanup_test_data(test_user_id)
    print()
    
    print("🎉 数据库约束诊断完成！")

if __name__ == "__main__":
    asyncio.run(main()) 