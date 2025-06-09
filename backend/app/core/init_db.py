"""
数据库初始化脚本
"""

import json
from datetime import datetime
from sqlmodel import Session, select
from app.core.database import engine
from app.models.rule import Rule


def init_sample_rules():
    """初始化示例规则数据"""
    sample_rules = [
        {
            "name": "问答式转换",
            "description": "将问答式对话转换为叙述式表达",
            "rule_type": "conversion",
            "scope": "global",
            "priority": 90,
            "is_active": True,
            "pattern": r"问：(.+?)\s*答：(.+?)(?=问：|$)",
            "replacement": "关于{question}，{answer}",
            "conditions": {
                "min_length": 10,
                "has_dialogue_markers": True
            },
            "parameters": {
                "preserve_timeline": True,
                "first_person_conversion": True
            },
            "examples": [
                {
                    "input": "问：你昨天晚上在哪里？答：我在家里看电视。",
                    "output": "昨天晚上我在家里看电视。",
                    "description": "基础问答转换"
                },
                {
                    "input": "问：看的什么节目？答：新闻联播，然后又看了电视剧。",
                    "output": "看了新闻联播，然后又看了电视剧。",
                    "description": "连续内容转换"
                }
            ],
            "created_by": "system",
            "tags": ["问答", "对话", "转换"]
        },
        {
            "name": "时间表达规范化",
            "description": "规范化时间表达，确保时间顺序清晰",
            "rule_type": "preprocessing",
            "scope": "global",
            "priority": 80,
            "is_active": True,
            "pattern": r"(\d{1,2})[点时](\d{1,2}分?)?",
            "replacement": r"\1点\2",
            "conditions": {
                "contains_time": True
            },
            "parameters": {
                "format_24h": False,
                "add_timeline_markers": True
            },
            "examples": [
                {
                    "input": "我8点钟出门的",
                    "output": "我8点出门的",
                    "description": "时间格式标准化"
                },
                {
                    "input": "晚上10点半回家",
                    "output": "晚上10点30分回家",
                    "description": "半点时间转换"
                }
            ],
            "created_by": "system",
            "tags": ["时间", "格式化", "预处理"]
        },
        {
            "name": "第一人称转换",
            "description": "确保叙述式笔录使用第一人称视角",
            "rule_type": "postprocessing",
            "scope": "narrative",
            "priority": 85,
            "is_active": True,
            "pattern": r"他/她说|被访者说",
            "replacement": "我",
            "conditions": {
                "is_narrative": True,
                "has_third_person": True
            },
            "parameters": {
                "preserve_quotes": False,
                "consistency_check": True
            },
            "examples": [
                {
                    "input": "被访者说他当时很紧张",
                    "output": "我当时很紧张",
                    "description": "第三人称转第一人称"
                },
                {
                    "input": "他表示同意这个提案",
                    "output": "我同意这个提案",
                    "description": "简化表达方式"
                }
            ],
            "created_by": "system",
            "tags": ["人称", "视角", "后处理"]
        },
        {
            "name": "冗余词汇清理",
            "description": "清理转换过程中产生的冗余词汇和表达",
            "rule_type": "postprocessing",
            "scope": "global",
            "priority": 70,
            "is_active": True,
            "pattern": r"然后说|接着说|继续说|又说",
            "replacement": "然后",
            "conditions": {
                "has_redundancy": True
            },
            "parameters": {
                "aggressive_cleanup": False,
                "preserve_meaning": True
            },
            "examples": [
                {
                    "input": "我然后说了一些话，接着说了更多内容",
                    "output": "我说了一些话，然后说了更多内容",
                    "description": "清理重复的说话动词"
                },
                {
                    "input": "他又说又说，反复强调",
                    "output": "他反复强调",
                    "description": "简化重复表达"
                }
            ],
            "created_by": "system",
            "tags": ["清理", "冗余", "优化"]
        },
        {
            "name": "连接词优化",
            "description": "优化句子间的连接词，提高叙述流畅性",
            "rule_type": "postprocessing",
            "scope": "global",
            "priority": 75,
            "is_active": True,
            "pattern": r"然后然后|接着接着",
            "replacement": "然后",
            "conditions": {
                "has_repetitive_connectors": True
            },
            "parameters": {
                "add_variety": True,
                "context_aware": True
            },
            "examples": [
                {
                    "input": "我先去了银行，然后然后去了超市",
                    "output": "我先去了银行，然后去了超市",
                    "description": "清理重复连接词"
                },
                {
                    "input": "他吃了饭，接着接着看电视",
                    "output": "他吃了饭，接着看电视",
                    "description": "简化连接表达"
                }
            ],
            "created_by": "system",
            "tags": ["连接词", "流畅性", "优化"]
        }
    ]
    
    with Session(engine) as session:
        # 检查是否已有规则数据
        existing_rules = session.exec(select(Rule)).first()
        if existing_rules:
            print("规则数据已存在，跳过初始化")
            return
        
        print("正在初始化示例规则数据...")
        
        for rule_data in sample_rules:
            # 将examples转换为JSON字符串
            examples_json = json.dumps(rule_data["examples"], ensure_ascii=False)
            conditions_json = json.dumps(rule_data["conditions"], ensure_ascii=False)
            parameters_json = json.dumps(rule_data["parameters"], ensure_ascii=False)
            tags_json = json.dumps(rule_data["tags"], ensure_ascii=False)
            
            rule = Rule(
                name=rule_data["name"],
                description=rule_data["description"],
                rule_type=rule_data["rule_type"],
                scope=rule_data["scope"],
                priority=rule_data["priority"],
                is_active=rule_data["is_active"],
                pattern=rule_data["pattern"],
                replacement=rule_data["replacement"],
                conditions=conditions_json,
                parameters=parameters_json,
                examples=examples_json,
                created_by=rule_data["created_by"],
                tags=tags_json,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                usage_count=0,
                success_rate=0.0
            )
            
            session.add(rule)
        
        session.commit()
        print(f"成功初始化 {len(sample_rules)} 条示例规则")


def init_database():
    """初始化数据库"""
    from app.core.database import create_db_and_tables
    
    print("创建数据库表...")
    create_db_and_tables()
    
    print("初始化示例数据...")
    init_sample_rules()
    
    print("数据库初始化完成！")


if __name__ == "__main__":
    init_database() 