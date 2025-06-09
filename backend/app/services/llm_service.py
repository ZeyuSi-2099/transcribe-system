"""
LLM 服务 - 集成 Deepseek API 进行文本转换
"""

import asyncio
from typing import Optional, Dict, Any, Tuple
import httpx
from loguru import logger

from app.core.config import settings
from app.services.rule_engine import rule_engine
from app.services.quality_service import quality_service


class LLMService:
    """LLM 服务类"""
    
    def __init__(self):
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY
        self.deepseek_base_url = settings.DEEPSEEK_BASE_URL
        self.deepseek_model = settings.DEEPSEEK_MODEL
        
    async def convert_transcription(
        self, 
        original_text: str, 
        rule_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        混合处理：规则引擎 + LLM 转换笔录文本
        
        Args:
            original_text: 原始对话式笔录
            rule_config: 转换规则配置
            
        Returns:
            包含转换结果和质量指标的字典
        """
        try:
            logger.info(f"开始转换文本，原文长度: {len(original_text)}")
            
            # 阶段1: 规则引擎预处理
            rule_processed_text, rule_info = await self._apply_rule_preprocessing(
                original_text, rule_config
            )
            
            # 阶段2: LLM 转换
            llm_result = await self._llm_conversion(
                rule_processed_text, rule_config
            )
            
            # 阶段3: 规则引擎后处理
            final_text, post_rule_info = await self._apply_rule_postprocessing(
                llm_result, rule_config
            )
            
            # 阶段4: 质量检验
            quality_metrics = await quality_service.calculate_quality_metrics(
                original_text, 
                final_text,
                {
                    "preprocessing_rules": rule_info,
                    "postprocessing_rules": post_rule_info
                }
            )
            
            # 组装最终结果
            result = {
                "success": True,
                "original_text": original_text,
                "converted_text": final_text,
                "processing_stages": {
                    "rule_preprocessing": {
                        "text": rule_processed_text,
                        "applied_rules": rule_info.get("applied_rules", [])
                    },
                    "llm_conversion": {
                        "text": llm_result,
                        "model_used": self.deepseek_model
                    },
                    "rule_postprocessing": {
                        "text": final_text,
                        "applied_rules": post_rule_info.get("applied_rules", [])
                    }
                },
                "quality_metrics": quality_metrics,
                "conversion_summary": {
                    "original_length": len(original_text),
                    "final_length": len(final_text),
                    "compression_ratio": 1 - (len(final_text) / len(original_text)) if len(original_text) > 0 else 0,
                    "quality_score": quality_metrics.get("overall_score", 0)
                }
            }
            
            logger.info(f"转换完成，质量评分: {quality_metrics.get('overall_score', 0):.2f}")
            return result
            
        except Exception as e:
            logger.error(f"转换过程失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_text": original_text,
                "converted_text": original_text,  # 失败时返回原文
                "quality_metrics": {"overall_score": 0.0}
            }
    
    async def _apply_rule_preprocessing(
        self, 
        text: str, 
        rule_config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """应用预处理规则"""
        try:
            # 提取预处理规则配置
            rule_set_id = None
            custom_rules = []
            
            if rule_config:
                rule_set_id = rule_config.get("rule_set_id")
                custom_rules = rule_config.get("preprocessing_rules", [])
            
            # 应用规则
            processed_text, rule_info = await rule_engine.apply_rules(
                text, rule_set_id, custom_rules
            )
            
            logger.debug(f"预处理完成，应用了 {len(rule_info.get('applied_rules', []))} 个规则")
            return processed_text, rule_info
            
        except Exception as e:
            logger.error(f"预处理失败: {e}")
            return text, {"error": str(e), "applied_rules": []}
    
    async def _apply_rule_postprocessing(
        self, 
        text: str, 
        rule_config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """应用后处理规则"""
        try:
            # 后处理规则（主要用于格式化和优化）
            post_rules = []
            
            if rule_config:
                post_rules = rule_config.get("postprocessing_rules", [])
            
            # 默认后处理规则
            default_post_rules = [
                {
                    "id": "post_1",
                    "name": "去除多余换行",
                    "rule_type": "postprocessing",
                    "priority": 10,
                    "pattern": r"\n\s*\n",
                    "replacement": "\n\n"
                },
                {
                    "id": "post_2",
                    "name": "标点符号优化",
                    "rule_type": "postprocessing", 
                    "priority": 9,
                    "pattern": r"([，。！？])\s+",
                    "replacement": r"\1"
                }
            ]
            
            all_post_rules = default_post_rules + post_rules
            
            # 应用后处理规则
            processed_text, rule_info = await rule_engine.apply_rules(
                text, None, all_post_rules
            )
            
            logger.debug(f"后处理完成，应用了 {len(rule_info.get('applied_rules', []))} 个规则")
            return processed_text, rule_info
            
        except Exception as e:
            logger.error(f"后处理失败: {e}")
            return text, {"error": str(e), "applied_rules": []}
    
    async def _llm_conversion(
        self, 
        text: str, 
        rule_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """LLM 转换处理"""
        try:
            # 构建增强的转换提示词
            prompt = self._build_enhanced_conversion_prompt(text, rule_config)
            
            # 调用 Deepseek API
            converted_text = await self._call_deepseek_api(prompt)
            
            return converted_text
            
        except Exception as e:
            logger.error(f"LLM 转换失败: {e}")
            raise
    
    def _build_enhanced_conversion_prompt(
        self, 
        text: str, 
        rule_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建增强的转换提示词"""
        
        # 基础转换指令
        base_instruction = """
你是一个专业的笔录转换专家。请将以下对话式访谈笔录转换为流畅的第一人称叙述文档。

转换要求：
1. **视角转换**: 将对话形式转换为被访者的第一人称叙述
2. **信息保全**: 保持所有重要事实、时间、地点、人物等关键信息
3. **语言优化**: 使用自然、流畅的书面语言表达
4. **逻辑重构**: 按时间顺序或逻辑顺序重新组织内容
5. **冗余处理**: 去除重复和无意义的语气词、口语化表达
6. **连贯性**: 使用适当的连接词确保文本连贯

转换原则：
- 严格使用第一人称（"我"）
- 保持事实的准确性和完整性
- 语言正式但不失自然
- 结构清晰，逻辑连贯
- 适当压缩冗余内容但不丢失重要信息
"""
        
        # 根据规则配置调整转换策略
        if rule_config:
            style_preference = rule_config.get("style_preference", "formal")
            if style_preference == "casual":
                base_instruction += "\n- 语言风格相对轻松自然，但仍保持书面语规范"
            elif style_preference == "formal":
                base_instruction += "\n- 使用正式的书面语言，表达准确严谨"
            
            focus_areas = rule_config.get("focus_areas", [])
            if "time_sequence" in focus_areas:
                base_instruction += "\n- 特别注意时间顺序的准确性和连贯性"
            if "emotional_tone" in focus_areas:
                base_instruction += "\n- 适当保留情感色彩和语气"
            if "factual_accuracy" in focus_areas:
                base_instruction += "\n- 优先确保事实描述的准确性"
        
        # 添加转换示例
        examples = """
转换示例：

原文：
问：你昨天晚上在哪里？
答：我在家里看电视。
问：看的什么节目？
答：看的是新闻联播，然后又看了一个电视剧。
问：几点睡的？
答：大概11点左右就睡了。

转换后：
昨天晚上我在家里看电视。先看了新闻联播，然后又看了一个电视剧，大概11点左右就睡了。

原文：
问：当时发生了什么？
答：就是，呃，我正在公司加班，然后突然接到一个电话。
问：什么电话？
答：是我妈妈打来的，说家里出了点事情，让我赶紧回去。
问：然后呢？
答：然后我就立马放下手头的工作，开车回家了。

转换后：
当时我正在公司加班，突然接到妈妈的电话，说家里出了点事情，让我赶紧回去。我立马放下手头的工作，开车回家了。
"""
        
        # 构建完整提示词
        prompt = f"""{base_instruction}

{examples}

现在请转换以下笔录：

{text}

转换后的文本："""
        
        return prompt
    
    async def _call_deepseek_api(self, prompt: str) -> str:
        """调用 Deepseek API"""
        
        if not self.deepseek_api_key:
            raise ValueError("Deepseek API 密钥未配置")
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.deepseek_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,  # 降低温度确保输出稳定
            "max_tokens": 4000,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=settings.DEFAULT_TIMEOUT) as client:
            try:
                response = await client.post(
                    f"{self.deepseek_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    raise ValueError("API 响应格式异常")
                    
            except httpx.HTTPStatusError as e:
                logger.error(f"Deepseek API HTTP 错误: {e.response.status_code} - {e.response.text}")
                raise ValueError(f"API 调用失败: {e.response.status_code}")
            except httpx.TimeoutException:
                logger.error("Deepseek API 调用超时")
                raise ValueError("API 调用超时")
            except Exception as e:
                logger.error(f"Deepseek API 调用异常: {str(e)}")
                raise
    
    async def test_connection(self) -> bool:
        """测试 LLM 服务连接"""
        try:
            test_text = "问：你好吗？答：我很好，谢谢。"
            result = await self.convert_transcription(test_text)
            return result.get("success", False)
        except Exception as e:
            logger.error(f"LLM 服务连接测试失败: {str(e)}")
            return False
    
    async def validate_conversion_quality(
        self, 
        original_text: str, 
        converted_text: str
    ) -> Dict[str, Any]:
        """验证转换质量"""
        try:
            # 基本验证
            if not converted_text or len(converted_text.strip()) == 0:
                return {"valid": False, "reason": "转换结果为空"}
            
            # 长度检查
            if len(converted_text) < len(original_text) * 0.3:
                return {"valid": False, "reason": "转换结果过短，可能丢失重要信息"}
            
            if len(converted_text) > len(original_text) * 1.5:
                return {"valid": False, "reason": "转换结果过长，可能存在冗余"}
            
            # 第一人称检查
            first_person_count = len([word for word in converted_text.split() if '我' in word])
            total_words = len(converted_text.split())
            if total_words > 20 and first_person_count == 0:
                return {"valid": False, "reason": "转换结果缺乏第一人称表述"}
            
            # 对话标记检查（转换后不应该还有对话标记）
            dialogue_markers = ['问：', '答：', '访谈者：', '被访者：']
            for marker in dialogue_markers:
                if marker in converted_text:
                    return {"valid": False, "reason": f"转换结果仍包含对话标记: {marker}"}
            
            return {"valid": True, "reason": "转换质量验证通过"}
            
        except Exception as e:
            logger.error(f"质量验证失败: {e}")
            return {"valid": False, "reason": f"验证过程出错: {str(e)}"}


# 创建全局 LLM 服务实例
llm_service = LLMService() 