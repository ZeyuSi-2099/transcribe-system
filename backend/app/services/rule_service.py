import re
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.rule import Rule, RuleCreate, RuleUpdate

class RuleService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_rule_from_description(self, description: str) -> Dict[str, Any]:
        """
        根据自然语言描述生成规则
        这里使用简单的规则匹配，实际项目中可以集成LLM
        """
        description_lower = description.lower()
        
        # 分析描述，生成规则
        rule_data = {
            "name": "",
            "description": description,
            "pattern": "",
            "replacement": "",
            "category": "format",
            "enabled": True,
            "example_before": "",
            "example_after": ""
        }
        
        # 简单的规则生成逻辑
        if "替换" in description or "replace" in description_lower:
            # 处理替换类规则
            rule_data.update(self._generate_replacement_rule(description))
        elif "删除" in description or "remove" in description_lower:
            # 处理删除类规则
            rule_data.update(self._generate_removal_rule(description))
        elif "格式" in description or "format" in description_lower:
            # 处理格式化规则
            rule_data.update(self._generate_format_rule(description))
        elif "时间" in description or "日期" in description:
            # 处理时间格式规则
            rule_data.update(self._generate_time_rule(description))
        else:
            # 默认规则
            rule_data.update(self._generate_default_rule(description))
        
        return rule_data

    def _generate_replacement_rule(self, description: str) -> Dict[str, Any]:
        """生成替换类规则"""
        # 尝试从描述中提取替换内容
        # 例如：将"您"替换为"你"
        import re
        
        # 匹配 "将X替换为Y" 的模式
        pattern1 = r'将["""]([^"""]+)["""]替换为["""]([^"""]+)["""]'
        pattern2 = r'把["""]([^"""]+)["""]改为["""]([^"""]+)["""]'
        pattern3 = r'["""]([^"""]+)["""]替换为["""]([^"""]+)["""]'
        
        for pattern in [pattern1, pattern2, pattern3]:
            match = re.search(pattern, description)
            if match:
                old_text = match.group(1)
                new_text = match.group(2)
                return {
                    "name": f"替换规则：{old_text} → {new_text}",
                    "pattern": old_text,
                    "replacement": new_text,
                    "category": "content",
                    "example_before": f"这是一个包含{old_text}的示例文本。",
                    "example_after": f"这是一个包含{new_text}的示例文本。"
                }
        
        # 如果没有匹配到具体的替换内容，生成通用替换规则
        return {
            "name": "文本替换规则",
            "pattern": "待替换文本",
            "replacement": "新文本",
            "category": "content",
            "example_before": "原始文本示例",
            "example_after": "替换后文本示例"
        }

    def _generate_removal_rule(self, description: str) -> Dict[str, Any]:
        """生成删除类规则"""
        if "空格" in description:
            return {
                "name": "删除多余空格",
                "pattern": r"\s+",
                "replacement": " ",
                "category": "format",
                "example_before": "这是   一个    有很多   空格的   文本。",
                "example_after": "这是 一个 有很多 空格的 文本。"
            }
        elif "换行" in description:
            return {
                "name": "删除多余换行",
                "pattern": r"\n+",
                "replacement": "\n",
                "category": "format",
                "example_before": "第一行\n\n\n第二行",
                "example_after": "第一行\n第二行"
            }
        else:
            return {
                "name": "删除指定内容",
                "pattern": "待删除内容",
                "replacement": "",
                "category": "format",
                "example_before": "包含待删除内容的文本",
                "example_after": "删除后的文本"
            }

    def _generate_format_rule(self, description: str) -> Dict[str, Any]:
        """生成格式化规则"""
        if "标点" in description:
            return {
                "name": "标点符号格式化",
                "pattern": r"[,.]",
                "replacement": "，。",
                "category": "format",
                "example_before": "你好,这是一个测试.",
                "example_after": "你好，这是一个测试。"
            }
        else:
            return {
                "name": "文本格式化",
                "pattern": "格式化模式",
                "replacement": "格式化结果",
                "category": "format",
                "example_before": "未格式化的文本",
                "example_after": "格式化后的文本"
            }

    def _generate_time_rule(self, description: str) -> Dict[str, Any]:
        """生成时间格式规则"""
        return {
            "name": "时间格式统一",
            "pattern": r"(\d{4})年(\d{1,2})月(\d{1,2})日",
            "replacement": r"\1-\2-\3",
            "category": "format",
            "example_before": "2024年6月12日",
            "example_after": "2024-6-12"
        }

    def _generate_default_rule(self, description: str) -> Dict[str, Any]:
        """生成默认规则"""
        return {
            "name": "自定义规则",
            "pattern": "匹配模式",
            "replacement": "替换内容",
            "category": "content",
            "example_before": "原始文本示例",
            "example_after": "处理后文本示例"
        }

    def get_all_rules(self) -> List[Rule]:
        """获取所有规则"""
        return self.db.query(Rule).all()

    def get_rule(self, rule_id: int) -> Optional[Rule]:
        """获取指定规则"""
        return self.db.query(Rule).filter(Rule.id == rule_id).first()

    def create_rule(self, rule_data: RuleCreate) -> Rule:
        """创建新规则"""
        rule = Rule(**rule_data.dict())
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_rule(self, rule_id: int, rule_data: RuleUpdate) -> Optional[Rule]:
        """更新规则"""
        rule = self.get_rule(rule_id)
        if not rule:
            return None
        
        for field, value in rule_data.dict(exclude_unset=True).items():
            setattr(rule, field, value)
        
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_rule(self, rule_id: int) -> bool:
        """删除规则"""
        rule = self.get_rule(rule_id)
        if not rule:
            return False
        
        self.db.delete(rule)
        self.db.commit()
        return True 