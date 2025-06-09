"""
测试Supabase连接
验证环境变量配置和数据库连接是否正常
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.supabase_client import get_supabase

def test_supabase_connection():
    """测试Supabase连接"""
    try:
        # 加载环境变量
        load_dotenv()
        
        print("🔍 检查环境变量...")
        url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        
        print(f"SUPABASE_URL: {'✅ 已设置' if url else '❌ 未设置'}")
        print(f"SUPABASE_SERVICE_KEY: {'✅ 已设置' if service_key else '❌ 未设置'}")
        print(f"SUPABASE_ANON_KEY: {'✅ 已设置' if anon_key else '❌ 未设置'}")
        print(f"SUPABASE_JWT_SECRET: {'✅ 已设置' if jwt_secret else '❌ 未设置'}")
        
        if not all([url, service_key, anon_key, jwt_secret]):
            print("❌ 环境变量配置不完整")
            return False
        
        print("\n🔗 测试Supabase连接...")
        supabase = get_supabase()
        
        # 测试简单查询
        result = supabase.table('transformation_rules').select('*').limit(1).execute()
        
        print("✅ Supabase连接成功！")
        print(f"📊 查询结果: {len(result.data)} 条记录")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试Supabase连接...\n")
    success = test_supabase_connection()
    
    if success:
        print("\n🎉 所有测试通过！Supabase配置正确。")
    else:
        print("\n💥 测试失败，请检查配置。")
        sys.exit(1) 