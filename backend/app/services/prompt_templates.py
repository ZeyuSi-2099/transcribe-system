"""
高级Prompt模板管理系统
支持多种转换场景和动态规则应用
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class ConversationType(Enum):
    """对话类型枚举"""
    GENERAL = "general"  # 通用对话
    INTERVIEW = "interview"  # 访谈记录
    MEETING = "meeting"  # 会议记录
    CONSULTATION = "consultation"  # 咨询对话
    CASUAL = "casual"  # 日常对话
    EMOTIONAL = "emotional"  # 情感访谈


@dataclass
class PromptRule:
    """单个转换规则"""
    name: str
    description: str
    instruction: str
    priority: int = 1  # 优先级 1-5，数字越大优先级越高


class PromptTemplateManager:
    """Prompt模板管理器"""
    
    def __init__(self):
        self.conversation_detectors = self._init_conversation_detectors()
        self.base_templates = self._init_base_templates()
        self.rules_library = self._init_rules_library()
        self.examples = self._init_examples()
    
    def _init_conversation_detectors(self) -> Dict[ConversationType, List[str]]:
        """初始化对话类型检测关键词"""
        return {
            ConversationType.INTERVIEW: [
                "工作经历", "教育背景", "个人经历", "职业", "学习", "成长", 
                "经验", "技能", "项目", "公司", "学校", "专业"
            ],
            ConversationType.MEETING: [
                "会议", "讨论", "决定", "方案", "计划", "进度", "报告", 
                "提案", "议题", "决策", "安排", "项目"
            ],
            ConversationType.CONSULTATION: [
                "咨询", "建议", "帮助", "指导", "解决", "问题", "困惑", 
                "选择", "建议", "推荐", "意见"
            ],
            ConversationType.EMOTIONAL: [
                "感受", "情绪", "心情", "难过", "开心", "压力", "担心", 
                "焦虑", "兴奋", "失望", "感动", "影响", "变化"
            ],
            ConversationType.CASUAL: [
                "昨天", "今天", "明天", "周末", "假期", "朋友", "家人", 
                "电影", "音乐", "旅行", "美食", "天气"
            ]
        }
    
    def _init_base_templates(self) -> Dict[ConversationType, str]:
        """初始化基础模板"""
        return {
            ConversationType.GENERAL: """
你是一位专业的文档转换专家。请将以下对话式笔录精准转换为第一人称叙述形式。

转换要求：
1. 去除所有对话标记（如"问："、"答："、"Q:"、"A:"等）
2. 将受访者的回答转换为自然流畅的第一人称叙述
3. 保持原文的完整信息，不遗漏任何关键细节
4. 维护时间顺序和逻辑关系的连贯性
5. 使用自然、专业的语言表达方式

原始笔录：
{text}

请转换为第一人称叙述：""",

            ConversationType.INTERVIEW: """
你是一位专业的访谈记录整理专家。请将以下访谈对话转换为第一人称自述形式。

专业要求：
1. 将受访者的回答整合为连贯的个人叙述
2. 保持专业术语和具体细节的准确性
3. 按照逻辑顺序重新组织内容（如时间线、重要性等）
4. 体现受访者的专业背景和经验深度
5. 使用正式、专业的表达方式

访谈记录：
{text}

转换为专业自述：""",

            ConversationType.MEETING: """
你是一位专业的会议记录整理专家。请将以下会议对话转换为与会者的第一人称总结。

整理要求：
1. 将发言内容转换为个人视角的会议总结
2. 突出关键决策、行动项和重要观点
3. 保持会议讨论的逻辑结构
4. 体现个人在会议中的参与和贡献
5. 使用清晰、结构化的表达方式

会议记录：
{text}

转换为个人会议总结：""",

            ConversationType.CONSULTATION: """
你是一位专业的咨询记录整理专家。请将以下咨询对话转换为咨询者的第一人称记录。

整理要求：
1. 将咨询过程转换为个人的咨询体验叙述
2. 突出问题、建议和解决方案
3. 保持咨询逻辑的清晰性
4. 体现个人的思考过程和收获
5. 使用易懂、实用的表达方式

咨询记录：
{text}

转换为个人咨询记录：""",

            ConversationType.EMOTIONAL: """
你是一位专业的心理访谈记录整理专家。请将以下对话转换为第一人称的内心叙述。

敏感处理要求：
1. 将情感表达转换为自然的内心独白
2. 保持情感的真实性和细腻度
3. 体现情感变化的过程和层次
4. 使用温暖、理解的语言风格
5. 保护隐私，避免过于具体的敏感信息

情感访谈：
{text}

转换为内心叙述：""",

            ConversationType.CASUAL: """
你是一位专业的日常对话整理专家。请将以下日常对话转换为轻松的第一人称叙述。

轻松处理要求：
1. 保持对话的轻松、自然氛围
2. 将交流内容转换为个人的日常分享
3. 保持生活化的语言风格，但确保信息完整性
4. 体现个人的真实感受和想法
5. 使用亲切、自然的表达方式
6. 保持关键细节和时间信息的准确性
7. 避免过度扩展，保持简洁自然

转换示例：
输入：问：你昨天晚上做了什么？答：我在家看了部电影，然后早点睡了。
输出：昨天晚上我在家看了部电影，之后就早早休息了。

日常对话：
{text}

转换为个人分享："""
        }
    
    def _init_rules_library(self) -> Dict[str, PromptRule]:
        """初始化规则库"""
        return {
            "preserve_details": PromptRule(
                name="细节保持",
                description="确保所有重要细节都被保留",
                instruction="特别注意保留所有数字、日期、名称、地点等具体信息，不要进行概括或省略。",
                priority=5
            ),
            "formal_tone": PromptRule(
                name="正式语调",
                description="使用正式、专业的语言风格",
                instruction="使用正式的书面语表达，避免口语化表达，保持专业性。",
                priority=3
            ),
            "casual_tone": PromptRule(
                name="轻松语调",
                description="使用轻松、自然的语言风格",
                instruction="使用自然、轻松的表达方式，可以保留一些口语化的表达以体现真实性。",
                priority=3
            ),
            "chronological_order": PromptRule(
                name="时间顺序",
                description="按照时间顺序重新组织内容",
                instruction="将内容按照时间先后顺序重新组织，确保叙述的时间逻辑清晰。",
                priority=4
            ),
            "logical_grouping": PromptRule(
                name="逻辑分组",
                description="按照主题和逻辑关系组织内容",
                instruction="将相关主题的内容归类整理，形成逻辑清晰的段落结构。",
                priority=4
            ),
            "emotion_preservation": PromptRule(
                name="情感保持",
                description="保持原文的情感色彩和语调",
                instruction="忠实保留说话者的情感表达和语调特点，体现真实的情感状态。",
                priority=3
            ),
            "concise_expression": PromptRule(
                name="简洁表达",
                description="简化冗余表达，保持内容简洁",
                instruction="去除重复和冗余的表达，保持叙述的简洁性，但不损失重要信息。",
                priority=2
            ),
            "expand_details": PromptRule(
                name="细节扩展",
                description="适当扩展和丰富表达",
                instruction="在保持原意的基础上，适当扩展和丰富表达，使叙述更加完整和生动。",
                priority=2
            )
        }
    
    def _init_examples(self) -> Dict[ConversationType, List[Dict[str, str]]]:
        """初始化示例库"""
        return {
            ConversationType.INTERVIEW: [
                {
                    "input": """问：请介绍一下你的工作经历。
答：我从2020年开始在一家科技公司工作，主要负责产品设计。之前在大学里学的是计算机专业，毕业后就直接进入了这个行业。""",
                    "output": """我从2020年开始在一家科技公司工作，主要负责产品设计工作。在此之前，我在大学攻读计算机专业，毕业后便直接进入了科技行业，开始了我的职业生涯。"""
                }
            ],
            ConversationType.CASUAL: [
                {
                    "input": """问：你昨天晚上做了什么？
答：我在家看了部电影，然后早点睡了。""",
                    "output": """昨天晚上我在家看了部电影，之后就早早休息了。"""
                }
            ]
        }
    
    def detect_conversation_type(self, text: str) -> ConversationType:
        """检测对话类型"""
        text_lower = text.lower()
        type_scores = {}
        
        # 加权计算分数
        for conv_type, keywords in self.conversation_detectors.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # 给高优先级关键词更高权重
                    if conv_type == ConversationType.EMOTIONAL and keyword in ['感受', '情绪', '心情', '影响', '变化']:
                        score += 2  # 情感关键词加权
                    elif conv_type == ConversationType.CONSULTATION and keyword in ['建议', '帮助', '指导', '解决']:
                        score += 2  # 咨询关键词加权
                    elif conv_type == ConversationType.CASUAL and keyword in ['昨天', '今天', '电影', '朋友']:
                        score += 2  # 日常关键词加权
                    else:
                        score += 1
            
            if score > 0:
                type_scores[conv_type] = score
        
        if not type_scores:
            return ConversationType.GENERAL
        
        # 返回得分最高的类型
        return max(type_scores.items(), key=lambda x: x[1])[0]
    
    def get_recommended_rules(self, conversation_type: ConversationType) -> List[str]:
        """根据对话类型推荐最佳规则组合"""
        # 基于测试结果的最佳配置
        recommendations = {
            ConversationType.INTERVIEW: ["preserve_details", "formal_tone"],
            ConversationType.CONSULTATION: ["logical_grouping", "preserve_details"],
            ConversationType.EMOTIONAL: ["emotion_preservation", "expand_details"],
            ConversationType.CASUAL: ["concise_expression", "casual_tone"],
            ConversationType.MEETING: ["logical_grouping", "formal_tone", "preserve_details"],
            ConversationType.GENERAL: []  # 默认配置表现最佳
        }
        
        return recommendations.get(conversation_type, [])
    
    def build_prompt(
        self, 
        text: str, 
        conversation_type: Optional[ConversationType] = None,
        rule_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建优化的prompt"""
        
        # 自动检测对话类型
        if conversation_type is None:
            conversation_type = self.detect_conversation_type(text)
        
        # 获取基础模板
        base_template = self.base_templates.get(
            conversation_type, 
            self.base_templates[ConversationType.GENERAL]
        )
        
        # 应用规则配置
        if rule_config:
            additional_rules = self._apply_rule_config(rule_config)
            if additional_rules:
                base_template = base_template.replace(
                    "请转换为第一人称叙述：",
                    f"""
                    
附加要求：
{additional_rules}

请转换为第一人称叙述："""
                )
        
        # 添加示例（如果有）
        examples = self.examples.get(conversation_type, [])
        if examples:
            example_text = "\n\n转换示例：\n"
            for i, example in enumerate(examples[:2], 1):  # 最多使用2个示例
                example_text += f"\n示例{i}：\n原文：{example['input']}\n转换：{example['output']}\n"
            
            base_template = base_template.replace(
                f"原始笔录：\n{text}",
                f"{example_text}\n现在请转换以下内容：\n原始笔录：\n{text}"
            )
        
        return base_template.format(text=text)
    
    def _apply_rule_config(self, rule_config: Dict[str, Any]) -> str:
        """应用规则配置"""
        if not rule_config:
            return ""
        
        active_rules = []
        
        # 处理预定义规则
        for rule_name in rule_config.get("rules", []):
            if rule_name in self.rules_library:
                rule = self.rules_library[rule_name]
                active_rules.append((rule.priority, rule.instruction))
        
        # 处理自定义规则
        custom_instructions = rule_config.get("custom_instructions", [])
        for instruction in custom_instructions:
            active_rules.append((3, instruction))  # 默认优先级为3
        
        # 按优先级排序并组合
        active_rules.sort(key=lambda x: x[0], reverse=True)
        return "\n".join([f"- {instruction}" for _, instruction in active_rules])


# 创建全局实例
prompt_manager = PromptTemplateManager() 