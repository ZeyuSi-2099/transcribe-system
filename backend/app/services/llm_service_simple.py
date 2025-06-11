"""
简化版 LLM 服务 - 避免SQLModel依赖冲突
集成高级Prompt模板系统
"""

import asyncio
import json
from typing import Optional, Dict, Any, AsyncGenerator
import httpx
from loguru import logger

from app.core.config import settings
from app.services.prompt_templates import prompt_manager, ConversationType


class SimpleLLMService:
    """简化版 LLM 服务类"""
    
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
        简化版转换：直接使用 LLM 转换笔录文本
        
        Args:
            original_text: 原始对话式笔录
            rule_config: 转换规则配置 (暂时忽略)
            
        Returns:
            包含转换结果的字典
        """
        try:
            logger.info(f"开始转换文本，原文长度: {len(original_text)}")
            
            # 直接进行LLM转换
            converted_text = await self._llm_conversion(original_text, rule_config)
            
            # 简化的质量评估
            quality_score = self._simple_quality_assessment(original_text, converted_text)
            
            # 组装结果
            result = {
                "success": True,
                "original_text": original_text,
                "converted_text": converted_text,
                "processing_stages": {
                    "llm_conversion": {
                        "text": converted_text,
                        "model_used": self.deepseek_model
                    }
                },
                "quality_metrics": {
                    "overall_score": quality_score,
                    "word_count_retention": len(converted_text.split()) / len(original_text.split()) if original_text.split() else 0
                },
                "conversion_summary": {
                    "original_length": len(original_text),
                    "final_length": len(converted_text),
                    "compression_ratio": 1 - (len(converted_text) / len(original_text)) if len(original_text) > 0 else 0,
                    "quality_score": quality_score
                }
            }
            
            logger.info(f"转换完成，质量评分: {quality_score:.2f}")
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
    
    async def _llm_conversion(
        self, 
        text: str, 
        rule_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """LLM 转换处理"""
        try:
            # 构建转换提示词
            prompt = self._build_conversion_prompt(text, rule_config)
            
            # 调用 Deepseek API
            converted_text = await self._call_deepseek_api(prompt)
            
            return converted_text
            
        except Exception as e:
            logger.error(f"LLM 转换失败: {e}")
            raise
    
    def _build_conversion_prompt(
        self, 
        text: str, 
        rule_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """构建优化的转换提示词"""
        
        # 使用高级prompt管理器构建prompt
        prompt = prompt_manager.build_prompt(
            text=text, 
            rule_config=rule_config
        )
        
        # 记录检测到的对话类型
        detected_type = prompt_manager.detect_conversation_type(text)
        logger.info(f"检测到对话类型: {detected_type.value}")
        
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
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.deepseek_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                converted_text = result["choices"][0]["message"]["content"].strip()
                
                logger.info(f"Deepseek API 调用成功，返回文本长度: {len(converted_text)}")
                return converted_text
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Deepseek API HTTP 错误: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.TimeoutException:
            logger.error("Deepseek API 调用超时")
            raise
        except Exception as e:
            logger.error(f"Deepseek API 调用异常: {str(e)}")
            raise
    
    def _simple_quality_assessment(self, original: str, converted: str) -> float:
        """简化的质量评估"""
        try:
            # 基础指标计算
            original_words = len(original.split())
            converted_words = len(converted.split())
            
            # 字数保留率 (0.5权重)
            word_retention = min(converted_words / original_words, 1.0) if original_words > 0 else 0
            
            # 长度合理性 (0.3权重)
            length_ratio = len(converted) / len(original) if len(original) > 0 else 0
            length_score = 1.0 if 0.5 <= length_ratio <= 1.5 else 0.5
            
            # 基础内容检查 (0.2权重)
            content_score = 0.8 if len(converted.strip()) > 10 else 0.3
            
            # 综合评分
            overall_score = (
                word_retention * 0.5 + 
                length_score * 0.3 + 
                content_score * 0.2
            )
            
            return min(overall_score, 1.0)
            
        except Exception as e:
            logger.error(f"质量评估失败: {e}")
            return 0.5
    
    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            test_prompt = "你好，请回复'连接正常'。"
            result = await self._call_deepseek_api(test_prompt)
            return "连接正常" in result or len(result) > 0
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False

    async def stream_convert_transcription(
        self, 
        original_text: str, 
        rule_config: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式转换：实时返回转换进度和结果
        
        Args:
            original_text: 原始对话式笔录
            rule_config: 转换规则配置
            
        Yields:
            SSE格式的事件数据
        """
        try:
            logger.info(f"开始流式转换，原文长度: {len(original_text)}")
            
            # 发送开始事件
            detected_type = prompt_manager.detect_conversation_type(original_text)
            yield self._format_sse_event("start", {
                "message": "开始分析对话内容",
                "conversation_type": detected_type.value,
                "original_length": len(original_text)
            })
            
            # 发送分析进度
            yield self._format_sse_event("progress", {
                "percentage": 20,
                "stage": "分析对话类型",
                "message": f"检测到{detected_type.value}类型对话"
            })
            
            # 构建转换提示词
            prompt = self._build_conversion_prompt(original_text, rule_config)
            
            yield self._format_sse_event("progress", {
                "percentage": 40,
                "stage": "构建转换策略",
                "message": "准备开始智能转换"
            })
            
            # 流式调用LLM
            converted_text = ""
            chunk_count = 0
            
            async for chunk_data in self._stream_call_deepseek_api(prompt):
                chunk_count += 1
                converted_text += chunk_data["content"]
                
                # 发送内容块
                yield self._format_sse_event("chunk", {
                    "content": chunk_data["content"],
                    "partial_content": converted_text,
                    "is_partial": True,
                    "chunk_index": chunk_count
                })
                
                # 更新进度
                progress = min(40 + (chunk_count * 8), 85)
                yield self._format_sse_event("progress", {
                    "percentage": progress,
                    "stage": "智能转换中",
                    "message": f"已生成{len(converted_text)}字符"
                })
            
            # 发送质量评估进度
            yield self._format_sse_event("progress", {
                "percentage": 90,
                "stage": "质量分析",
                "message": "评估转换质量"
            })
            
            # 计算质量评分
            quality_score = self._simple_quality_assessment(original_text, converted_text)
            
            yield self._format_sse_event("quality", {
                "score": quality_score,
                "metrics": {
                    "word_count_retention": len(converted_text.split()) / len(original_text.split()) if original_text.split() else 0,
                    "length_ratio": len(converted_text) / len(original_text) if len(original_text) > 0 else 0
                }
            })
            
            # 发送完成事件
            yield self._format_sse_event("complete", {
                "success": True,
                "final_content": converted_text,
                "quality_score": quality_score,
                "original_length": len(original_text),
                "final_length": len(converted_text),
                "processing_time": "已完成",
                "conversion_summary": {
                    "original_length": len(original_text),
                    "final_length": len(converted_text),
                    "compression_ratio": 1 - (len(converted_text) / len(original_text)) if len(original_text) > 0 else 0,
                    "quality_score": quality_score
                }
            })
            
            logger.info(f"流式转换完成，质量评分: {quality_score:.2f}")
            
        except Exception as e:
            logger.error(f"流式转换失败: {str(e)}")
            yield self._format_sse_event("error", {
                "success": False,
                "error": str(e),
                "message": "转换过程出现错误"
            })
    
    def _format_sse_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """格式化SSE事件"""
        import time
        data["timestamp"] = time.time()
        return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    async def _stream_call_deepseek_api(self, prompt: str) -> AsyncGenerator[Dict[str, Any], None]:
        """流式调用Deepseek API"""
        
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
            "max_tokens": 4000,
            "temperature": 0.7,
            "stream": True  # 启用流式响应
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.deepseek_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    
                    # 收集完整响应用于非流式降级
                    full_content = ""
                    chunk_count = 0
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # 移除 "data: " 前缀
                            
                            if data_str.strip() == "[DONE]":
                                break
                                
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        content = delta["content"]
                                        # 确保内容不为空且有效
                                        if content and content.strip():
                                            full_content += content
                                            chunk_count += 1
                                            
                                            yield {
                                                "content": content,
                                                "finish_reason": data["choices"][0].get("finish_reason"),
                                                "chunk_index": chunk_count,
                                                "total_content": full_content
                                            }
                            except json.JSONDecodeError as e:
                                logger.warning(f"跳过无效的SSE数据: {data_str}")
                                continue
                    
                    # 如果没有收到任何有效内容，降级为普通API调用
                    if chunk_count == 0:
                        logger.warning("流式API没有返回有效内容，降级为普通API调用")
                        fallback_content = await self._call_deepseek_api(prompt)
                        if fallback_content and fallback_content.strip():
                            # 将完整内容分成小块进行模拟流式输出
                            words = fallback_content.split()
                            chunk_size = max(1, len(words) // 10)  # 分成10个左右的块
                            
                            for i in range(0, len(words), chunk_size):
                                chunk_words = words[i:i + chunk_size]
                                chunk_content = " ".join(chunk_words)
                                if i > 0:  # 从第二个chunk开始添加空格
                                    chunk_content = " " + chunk_content
                                
                                yield {
                                    "content": chunk_content,
                                    "finish_reason": None if i + chunk_size < len(words) else "stop",
                                    "chunk_index": (i // chunk_size) + 1,
                                    "total_content": " ".join(words[:i + chunk_size])
                                }
                                
                                # 模拟流式延迟
                                await asyncio.sleep(0.3)
                                
        except httpx.HTTPStatusError as e:
            logger.error(f"Deepseek API HTTP 错误: {e.response.status_code} - {e.response.text}")
            # 降级为普通API调用
            try:
                fallback_content = await self._call_deepseek_api(prompt)
                if fallback_content and fallback_content.strip():
                    yield {
                        "content": fallback_content,
                        "finish_reason": "stop",
                        "chunk_index": 1,
                        "total_content": fallback_content
                    }
            except Exception as fallback_error:
                logger.error(f"降级API调用也失败: {fallback_error}")
                raise e
        except httpx.TimeoutException:
            logger.error("Deepseek API 调用超时")
            raise
        except Exception as e:
            logger.error(f"Deepseek API 流式调用异常: {str(e)}")
            raise


# 创建全局实例
simple_llm_service = SimpleLLMService() 