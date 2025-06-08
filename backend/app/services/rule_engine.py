"""
规则引擎服务 - 处理文本转换规则的应用和执行
"""

import re
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from sqlmodel import Session, select

from app.core.database import engine
from app.models.rule import Rule, RuleSet, RuleType, RuleScope


class RuleEngine:
    """规则引擎核心类"""
    
    def __init__(self):
        self.compiled_patterns = {}  # 缓存编译的正则表达式
        
    async def apply_rules(
        self, 
        text: str, 
        rule_set_id: Optional[int] = None,
        custom_rules: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        应用规则集转换文本
        
        Args:
            text: 待处理的文本
            rule_set_id: 规则集ID
            custom_rules: 自定义规则列表
            
        Returns:
            (转换后的文本, 应用信息)
        """
        try:
            # 获取规则列表
            rules = await self._get_rules(rule_set_id, custom_rules)
            
            if not rules:
                logger.warning("没有可用的规则")
                return text, {"applied_rules": [], "transformations": []}
            
            # 按优先级和类型排序规则
            sorted_rules = self._sort_rules(rules)
            
            # 应用规则
            result_text = text
            applied_rules = []
            transformations = []
            
            for rule in sorted_rules:
                if not rule.get("is_active", True):
                    continue
                    
                original_text = result_text
                result_text, rule_applied = await self._apply_single_rule(
                    result_text, rule
                )
                
                if rule_applied:
                    applied_rules.append({
                        "rule_id": rule.get("id"),
                        "rule_name": rule.get("name"),
                        "rule_type": rule.get("rule_type")
                    })
                    
                    if original_text != result_text:
                        transformations.append({
                            "rule_name": rule.get("name"),
                            "before": original_text[:100] + "..." if len(original_text) > 100 else original_text,
                            "after": result_text[:100] + "..." if len(result_text) > 100 else result_text,
                            "changes": self._calculate_changes(original_text, result_text)
                        })
            
            return result_text, {
                "applied_rules": applied_rules,
                "transformations": transformations,
                "total_rules_applied": len(applied_rules)
            }
            
        except Exception as e:
            logger.error(f"规则应用失败: {str(e)}")
            return text, {"error": str(e), "applied_rules": []}
    
    async def _get_rules(
        self, 
        rule_set_id: Optional[int] = None,
        custom_rules: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """获取规则列表"""
        rules = []
        
        # 添加自定义规则
        if custom_rules:
            rules.extend(custom_rules)
        
        # 从数据库获取规则集
        if rule_set_id:
            with Session(engine) as session:
                rule_set = session.get(RuleSet, rule_set_id)
                if rule_set and rule_set.rules:
                    # 获取规则集中的规则
                    statement = select(Rule).where(Rule.id.in_(rule_set.rules))
                    db_rules = session.exec(statement).all()
                    
                    for rule in db_rules:
                        rules.append({
                            "id": rule.id,
                            "name": rule.name,
                            "description": rule.description,
                            "rule_type": rule.rule_type,
                            "scope": rule.scope,
                            "priority": rule.priority,
                            "is_active": rule.is_active,
                            "pattern": rule.pattern,
                            "replacement": rule.replacement,
                            "conditions": rule.conditions,
                            "parameters": rule.parameters
                        })
        else:
            # 使用默认规则集
            rules.extend(await self._get_default_rules())
        
        return rules
    
    async def _get_default_rules(self) -> List[Dict[str, Any]]:
        """获取默认规则"""
        return [
            {
                "id": "default_1",
                "name": "对话标记清理",
                "rule_type": RuleType.PREPROCESSING,
                "priority": 10,
                "pattern": r"^(问：|答：|访谈者：|被访者：)",
                "replacement": "",
                "description": "移除对话标记"
            },
            {
                "id": "default_2", 
                "name": "多余空格清理",
                "rule_type": RuleType.PREPROCESSING,
                "priority": 9,
                "pattern": r"\s+",
                "replacement": " ",
                "description": "合并多余空格"
            },
            {
                "id": "default_3",
                "name": "句首人称转换",
                "rule_type": RuleType.DIALOGUE_STRUCTURE,
                "priority": 8,
                "pattern": r"我([说道|回答|表示|认为|觉得])？",
                "replacement": r"我\1",
                "description": "统一第一人称表达"
            },
            {
                "id": "default_4",
                "name": "语气词优化",
                "rule_type": RuleType.LANGUAGE_STYLE,
                "priority": 7,
                "pattern": r"(嗯|啊|呃|那个)+",
                "replacement": "",
                "description": "移除语气词"
            },
            {
                "id": "default_5",
                "name": "连接词添加",
                "rule_type": RuleType.POSTPROCESSING,
                "priority": 5,
                "pattern": r"。\s*([然后|接着|后来|之后])",
                "replacement": r"，\1",
                "description": "优化连接词使用"
            }
        ]
    
    def _sort_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按优先级和类型排序规则"""
        # 规则类型优先级映射
        type_priority = {
            RuleType.PREPROCESSING: 1,
            RuleType.DIALOGUE_STRUCTURE: 2,
            RuleType.LANGUAGE_STYLE: 3,
            RuleType.CONTENT_FILTER: 4,
            RuleType.POSTPROCESSING: 5
        }
        
        return sorted(
            rules,
            key=lambda x: (
                type_priority.get(x.get("rule_type"), 99),
                -x.get("priority", 0)  # 优先级高的排前面
            )
        )
    
    async def _apply_single_rule(
        self, 
        text: str, 
        rule: Dict[str, Any]
    ) -> Tuple[str, bool]:
        """应用单个规则"""
        try:
            pattern = rule.get("pattern")
            replacement = rule.get("replacement", "")
            conditions = rule.get("conditions", {})
            
            if not pattern:
                return text, False
            
            # 检查条件
            if not self._check_conditions(text, conditions):
                return text, False
            
            # 编译和缓存正则表达式
            rule_id = rule.get("id", "unknown")
            if rule_id not in self.compiled_patterns:
                try:
                    self.compiled_patterns[rule_id] = re.compile(pattern, re.MULTILINE | re.UNICODE)
                except re.error as e:
                    logger.warning(f"规则 {rule.get('name')} 的正则表达式无效: {e}")
                    return text, False
            
            compiled_pattern = self.compiled_patterns[rule_id]
            
            # 应用替换
            original_text = text
            result_text = compiled_pattern.sub(replacement, text)
            
            # 检查是否有变化
            rule_applied = original_text != result_text
            
            if rule_applied:
                logger.debug(f"规则 '{rule.get('name')}' 已应用")
            
            return result_text, rule_applied
            
        except Exception as e:
            logger.error(f"应用规则 '{rule.get('name')}' 时出错: {e}")
            return text, False
    
    def _check_conditions(self, text: str, conditions: Dict[str, Any]) -> bool:
        """检查规则执行条件"""
        if not conditions:
            return True
        
        try:
            # 检查文本长度条件
            if "min_length" in conditions:
                if len(text) < conditions["min_length"]:
                    return False
            
            if "max_length" in conditions:
                if len(text) > conditions["max_length"]:
                    return False
            
            # 检查包含关键词条件
            if "contains" in conditions:
                keywords = conditions["contains"]
                if isinstance(keywords, str):
                    keywords = [keywords]
                if not any(keyword in text for keyword in keywords):
                    return False
            
            # 检查排除关键词条件
            if "excludes" in conditions:
                keywords = conditions["excludes"]
                if isinstance(keywords, str):
                    keywords = [keywords]
                if any(keyword in text for keyword in keywords):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查条件时出错: {e}")
            return False
    
    def _calculate_changes(self, before: str, after: str) -> Dict[str, Any]:
        """计算文本变化统计"""
        return {
            "length_before": len(before),
            "length_after": len(after),
            "length_change": len(after) - len(before),
            "word_count_before": len(before.split()),
            "word_count_after": len(after.split()),
        }
    
    async def test_rule(
        self, 
        text: str, 
        rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """测试单个规则"""
        try:
            result_text, applied = await self._apply_single_rule(text, rule)
            
            return {
                "success": True,
                "applied": applied,
                "original_text": text,
                "result_text": result_text,
                "changes": self._calculate_changes(text, result_text) if applied else {}
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_text": text
            }
    
    async def validate_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """验证规则有效性"""
        issues = []
        
        # 检查必需字段
        if not rule.get("name"):
            issues.append("规则名称不能为空")
        
        if not rule.get("rule_type"):
            issues.append("规则类型不能为空")
        
        # 检查正则表达式
        pattern = rule.get("pattern")
        if pattern:
            try:
                re.compile(pattern)
            except re.error as e:
                issues.append(f"正则表达式无效: {e}")
        
        # 检查优先级
        priority = rule.get("priority", 5)
        if not isinstance(priority, int) or priority < 1 or priority > 10:
            issues.append("优先级必须是1-10之间的整数")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


# 创建全局规则引擎实例
rule_engine = RuleEngine() 