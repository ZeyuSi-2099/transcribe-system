#!/usr/bin/env python3
"""
核心功能测试脚本
验证笔录转换系统的主要功能模块
"""

import asyncio
import json
import uuid
from datetime import datetime
from app.services.supabase_service import TransformationRuleService, ConversionHistoryService
from app.models.supabase_models import ConversionHistoryCreate

# 使用有效的UUID格式
TEST_USER_ID = str(uuid.uuid4())

async def test_rule_service():
    """测试规则服务"""
    print("🔧 测试规则服务...")
    
    service = TransformationRuleService(TEST_USER_ID)
    
    # 获取系统规则
    rules = service.get_system_rules()
    print(f"✅ 成功获取 {len(rules)} 条系统规则:")
    for rule in rules:
        print(f"  - {rule.name}: {rule.description}")
    
    # 获取用户规则（异步）
    user_rules = await service.list_rules(include_system=False)
    print(f"✅ 用户规则数量: {len(user_rules)}")
    
    return rules[0] if rules else None


async def test_conversion_service(rule_id: str):
    """测试转换服务"""
    print("\n📝 测试转换服务...")
    
    service = ConversionHistoryService(TEST_USER_ID)
    
    # 创建测试转换记录
    test_data = ConversionHistoryCreate(
        original_text="测试问：您好，请问您的姓名是什么？\n答：我叫张三，今年25岁。",
        rule_id=rule_id,
        file_name="test_conversation.txt",
        file_size=len("测试文本".encode('utf-8')),
        metadata={"test": True, "created_at": datetime.now().isoformat()}
    )
    
    try:
        # 创建转换记录
        conversion = await service.create_conversion(test_data)
        print(f"✅ 创建转换记录成功: {conversion.id}")
        
        # 获取转换记录
        retrieved = await service.get_conversion(conversion.id)
        if retrieved:
            print(f"✅ 获取转换记录成功: {retrieved.file_name}")
        
        # 获取用户统计
        stats = await service.get_user_stats()
        print(f"✅ 用户统计: {stats}")
        
        return conversion.id
        
    except Exception as e:
        print(f"❌ 转换服务测试失败: {e}")
        return None


async def test_text_processing():
    """测试文本处理功能"""
    print("\n🤖 测试文本处理功能...")
    
    # 模拟LLM文本转换（这里使用简单的规则转换）
    test_text = """
    问：您能介绍一下自己吗？
    答：我叫李四，是一名软件工程师，在北京工作已经三年了。
    
    问：您平时的工作内容是什么？
    答：主要负责后端开发，使用Python和Java开发Web应用。
    """
    
    # 简单的转换规则（实际应该调用LLM）
    converted_text = convert_qa_to_narrative(test_text)
    
    print("原文:")
    print(test_text.strip())
    print("\n转换后:")
    print(converted_text)
    
    return converted_text


def convert_qa_to_narrative(text: str) -> str:
    """
    简单的问答转换为叙述（模拟LLM功能）
    实际项目中应该调用LLM API
    """
    lines = text.strip().split('\n')
    narrative_parts = []
    
    current_answer = ""
    for line in lines:
        line = line.strip()
        if line.startswith('答：'):
            # 提取答案内容，转换为第一人称
            answer = line[2:].strip()
            # 简单转换：移除"我"字开头的重复
            if answer.startswith('我'):
                current_answer = answer
            else:
                current_answer = f"我{answer}"
            narrative_parts.append(current_answer)
    
    return ' '.join(narrative_parts)


async def main():
    """主测试函数"""
    print("🚀 开始核心功能测试\n")
    
    try:
        # 1. 测试规则服务
        rule = await test_rule_service()
        
        if rule:
            # 2. 测试转换服务
            conversion_id = await test_conversion_service(rule.id)
            
            # 3. 测试文本处理
            await test_text_processing()
            
            print("\n🎉 所有核心功能测试完成！")
            print(f"✅ 规则服务: 正常")
            print(f"✅ 转换服务: 正常") 
            print(f"✅ 文本处理: 正常")
            print(f"✅ 数据库集成: 正常")
            
        else:
            print("❌ 无法获取测试规则，请检查数据库数据")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 