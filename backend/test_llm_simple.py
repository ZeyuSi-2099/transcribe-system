#!/usr/bin/env python3
"""
简化版LLM服务测试脚本
验证Deepseek API连接和转换功能
"""

import asyncio
import os
import sys

# 设置路径
sys.path.append('/Users/13426090042139.com/Documents/3.Cursor/1.Record Transfer/Test15 需求整理/backend')

from app.services.llm_service_simple import simple_llm_service


async def test_llm_connection():
    """测试LLM连接"""
    print("🔧 测试LLM连接...")
    
    try:
        is_connected = await simple_llm_service.test_connection()
        if is_connected:
            print("✅ LLM连接测试成功")
            return True
        else:
            print("❌ LLM连接测试失败")
            return False
    except Exception as e:
        print(f"❌ LLM连接异常: {e}")
        return False


async def test_transcription_conversion():
    """测试转换功能"""
    print("\n🔄 测试转换功能...")
    
    test_text = """
问：你昨天晚上在哪里？
答：我在家里看电视。
问：看的什么节目？
答：看的是新闻联播，然后又看了一个电视剧。
问：几点睡的？
答：大概11点左右就睡了。
"""
    
    try:
        print(f"原文长度: {len(test_text)} 字符")
        print("开始转换...")
        
        result = await simple_llm_service.convert_transcription(test_text)
        
        if result["success"]:
            print("✅ 转换成功!")
            print(f"转换后长度: {len(result['converted_text'])} 字符")
            print(f"质量评分: {result['quality_metrics']['overall_score']:.2f}")
            print(f"使用模型: {result['processing_stages']['llm_conversion']['model_used']}")
            
            print("\n📝 转换结果预览:")
            print("-" * 50)
            print(result['converted_text'][:200] + "..." if len(result['converted_text']) > 200 else result['converted_text'])
            print("-" * 50)
            
            return True
        else:
            print(f"❌ 转换失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 转换异常: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始LLM服务测试")
    print("=" * 60)
    
    # 检查配置
    if not simple_llm_service.deepseek_api_key:
        print("⚠️  警告: DEEPSEEK_API_KEY 未配置，将跳过实际API测试")
        print("请在环境变量或.env文件中配置API密钥")
        return
    
    # 测试连接
    connection_ok = await test_llm_connection()
    
    if connection_ok:
        # 测试转换功能
        conversion_ok = await test_transcription_conversion()
        
        if conversion_ok:
            print("\n🎉 所有测试通过！LLM服务工作正常")
        else:
            print("\n❌ 转换功能测试失败")
    else:
        print("\n❌ 连接测试失败，请检查API密钥和网络")
    
    print("=" * 60)
    print("测试完成")


if __name__ == "__main__":
    asyncio.run(main()) 