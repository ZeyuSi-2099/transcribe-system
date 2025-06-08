"""
质量检验服务 - 计算和评估文本转换质量
"""

import re
import difflib
from typing import Dict, Any, List, Tuple
from loguru import logger


class QualityService:
    """质量检验服务类"""
    
    def __init__(self):
        self.quality_weights = {
            "word_retention_rate": 0.25,      # 字数保留率
            "content_preservation": 0.30,     # 内容保持率
            "coherence_score": 0.20,          # 连贯性评分
            "first_person_consistency": 0.15, # 第一人称一致性
            "redundancy_reduction": 0.10       # 冗余减少率
        }
    
    async def calculate_quality_metrics(
        self, 
        original_text: str, 
        converted_text: str,
        rule_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        计算转换质量指标
        
        Args:
            original_text: 原始文本
            converted_text: 转换后文本
            rule_info: 规则应用信息
            
        Returns:
            质量指标字典
        """
        try:
            metrics = {}
            
            # 基础统计指标
            metrics.update(self._calculate_basic_metrics(original_text, converted_text))
            
            # 内容保持指标
            metrics.update(self._calculate_content_preservation(original_text, converted_text))
            
            # 语言质量指标
            metrics.update(self._calculate_language_quality(converted_text))
            
            # 结构化指标
            metrics.update(self._calculate_structure_metrics(original_text, converted_text))
            
            # 计算综合评分
            metrics["overall_score"] = self._calculate_overall_score(metrics)
            
            # 添加规则应用信息
            if rule_info:
                metrics["rule_application"] = rule_info
            
            # 生成质量报告
            metrics["quality_report"] = self._generate_quality_report(metrics)
            
            logger.info(f"质量评估完成，综合评分: {metrics['overall_score']:.2f}")
            return metrics
            
        except Exception as e:
            logger.error(f"质量评估失败: {str(e)}")
            return {"error": str(e), "overall_score": 0.0}
    
    def _calculate_basic_metrics(self, original: str, converted: str) -> Dict[str, Any]:
        """计算基础统计指标"""
        # 类型检查和安全处理
        if not isinstance(original, str):
            original = str(original) if original is not None else ""
        if not isinstance(converted, str):
            converted = str(converted) if converted is not None else ""
            
        original_chars = len(original)
        converted_chars = len(converted)
        original_words = len(original.split()) if original.strip() else 0
        converted_words = len(converted.split()) if converted.strip() else 0
        
        return {
            "character_count": {
                "original": original_chars,
                "converted": converted_chars,
                "retention_rate": converted_chars / original_chars if original_chars > 0 else 0
            },
            "word_count": {
                "original": original_words,
                "converted": converted_words,
                "retention_rate": converted_words / original_words if original_words > 0 else 0
            },
            "compression_ratio": {
                "character_level": (original_chars - converted_chars) / original_chars if original_chars > 0 else 0,
                "word_level": (original_words - converted_words) / original_words if original_words > 0 else 0
            }
        }
    
    def _calculate_content_preservation(self, original: str, converted: str) -> Dict[str, Any]:
        """计算内容保持指标"""
        # 提取关键信息
        original_entities = self._extract_entities(original)
        converted_entities = self._extract_entities(converted)
        
        # 计算实体保留率
        entity_preservation = 0.0
        if original_entities:
            preserved_entities = len(set(original_entities) & set(converted_entities))
            entity_preservation = preserved_entities / len(original_entities)
        
        # 计算语义相似度 (简化版本)
        semantic_similarity = self._calculate_semantic_similarity(original, converted)
        
        # 关键词保留率
        original_keywords = self._extract_keywords(original)
        converted_keywords = self._extract_keywords(converted)
        keyword_preservation = 0.0
        if original_keywords:
            preserved_keywords = len(set(original_keywords) & set(converted_keywords))
            keyword_preservation = preserved_keywords / len(original_keywords)
        
        return {
            "content_preservation": {
                "entity_preservation_rate": entity_preservation,
                "keyword_preservation_rate": keyword_preservation,
                "semantic_similarity": semantic_similarity,
                "overall_preservation": (entity_preservation + keyword_preservation + semantic_similarity) / 3
            }
        }
    
    def _calculate_language_quality(self, text: str) -> Dict[str, Any]:
        """计算语言质量指标"""
        # 第一人称一致性
        first_person_consistency = self._check_first_person_consistency(text)
        
        # 连贯性评分
        coherence_score = self._calculate_coherence(text)
        
        # 流畅度评分
        fluency_score = self._calculate_fluency(text)
        
        # 冗余度检查
        redundancy_score = self._check_redundancy(text)
        
        return {
            "language_quality": {
                "first_person_consistency": first_person_consistency,
                "coherence_score": coherence_score,
                "fluency_score": fluency_score,
                "redundancy_score": redundancy_score,
                "overall_language_quality": (first_person_consistency + coherence_score + fluency_score + redundancy_score) / 4
            }
        }
    
    def _calculate_structure_metrics(self, original: str, converted: str) -> Dict[str, Any]:
        """计算结构化指标"""
        # 对话轮次分析
        original_turns = self._count_dialogue_turns(original)
        converted_turns = self._count_dialogue_turns(converted)
        
        # 句子数量分析
        original_sentences = self._count_sentences(original)
        converted_sentences = self._count_sentences(converted)
        
        # 段落结构分析
        original_paragraphs = len([p for p in original.split('\n\n') if p.strip()])
        converted_paragraphs = len([p for p in converted.split('\n\n') if p.strip()])
        
        return {
            "structure_metrics": {
                "dialogue_turns": {
                    "original": original_turns,
                    "converted": converted_turns,
                    "reduction_rate": (original_turns - converted_turns) / original_turns if original_turns > 0 else 0
                },
                "sentences": {
                    "original": original_sentences,
                    "converted": converted_sentences,
                    "change_rate": (converted_sentences - original_sentences) / original_sentences if original_sentences > 0 else 0
                },
                "paragraphs": {
                    "original": original_paragraphs,
                    "converted": converted_paragraphs,
                    "change_rate": (converted_paragraphs - original_paragraphs) / original_paragraphs if original_paragraphs > 0 else 0
                }
            }
        }
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取实体(人名、地名、时间等)"""
        entities = []
        
        # 简单的实体识别(可以后续扩展为更复杂的NER)
        # 时间表达式
        time_patterns = [
            r'\d{1,2}[点时](\d{1,2}分?)?',
            r'(昨天|今天|明天|前天|后天)',
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'(上午|下午|晚上|深夜|凌晨)',
        ]
        
        for pattern in time_patterns:
            entities.extend(re.findall(pattern, text))
        
        # 地点表达式
        location_patterns = [
            r'在([^，。！？\s]{2,8})(里|内|中|上|下|旁|边)',
            r'(公司|学校|医院|银行|商店|餐厅|酒店)([^，。！？\s]{0,5})',
        ]
        
        for pattern in location_patterns:
            entities.extend([match[0] if isinstance(match, tuple) else match for match in re.findall(pattern, text)])
        
        return list(set(entities))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 类型检查和安全处理
        if not isinstance(text, str):
            if isinstance(text, list):
                # 如果传入的是列表，将其连接为字符串
                text = ' '.join(str(item) for item in text)
            else:
                # 其他类型转换为字符串
                text = str(text)
        
        if not text or not text.strip():
            return []
        
        # 移除标点符号和停用词
        cleaned_text = re.sub(r'[^\w\s]', '', text)
        words = cleaned_text.split()
        
        # 简单的关键词提取 - 过滤停用词
        stop_words = {'的', '了', '在', '是', '我', '你', '他', '她', '它', '我们', '你们', '他们',
                     '这', '那', '这个', '那个', '这些', '那些', '和', '或者', '但是', '然后',
                     '因为', '所以', '如果', '虽然', '但是', '而且', '不过', '还有', '没有',
                     '什么', '怎么', '为什么', '哪里', '什么时候', '怎样'}
        
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        # 统计词频，返回出现频率较高的词
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回出现次数大于1的词作为关键词
        return [word for word, freq in word_freq.items() if freq > 1]
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """计算语义相似度(简化版本)"""
        # 使用简单的字符级相似度作为语义相似度的近似
        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()
    
    def _check_first_person_consistency(self, text: str) -> float:
        """检查第一人称一致性"""
        # 统计人称代词
        first_person = len(re.findall(r'我|自己', text))
        second_person = len(re.findall(r'你|您', text))
        third_person = len(re.findall(r'他|她|它|他们|她们|它们', text))
        
        total_pronouns = first_person + second_person + third_person
        
        if total_pronouns == 0:
            return 1.0  # 没有人称代词，认为是一致的
        
        # 第一人称占比越高，一致性越好
        consistency = first_person / total_pronouns
        return min(consistency * 1.2, 1.0)  # 轻微加权，最大值为1.0
    
    def _calculate_coherence(self, text: str) -> float:
        """计算连贯性评分"""
        sentences = self._split_sentences(text)
        if len(sentences) < 2:
            return 1.0
        
        # 检查连接词使用
        connectives = ['然后', '接着', '后来', '之后', '因此', '所以', '但是', '不过', '而且', '同时']
        connective_count = sum(1 for sentence in sentences for conn in connectives if conn in sentence)
        
        # 连接词密度
        connective_density = connective_count / len(sentences)
        
        # 句子长度一致性
        sentence_lengths = [len(s) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        length_variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        length_consistency = 1 / (1 + length_variance / 100)  # 归一化
        
        # 综合连贯性评分
        coherence = (connective_density * 0.6 + length_consistency * 0.4)
        return min(coherence, 1.0)
    
    def _calculate_fluency(self, text: str) -> float:
        """计算流畅度评分"""
        # 类型检查和安全处理
        if not isinstance(text, str):
            if isinstance(text, list):
                # 如果传入的是列表，将其连接为字符串
                text = ' '.join(str(item) for item in text)
            else:
                # 其他类型转换为字符串
                text = str(text)
        
        if not text or not text.strip():
            return 1.0  # 空文本认为是流畅的
        
        # 检查语法错误和不自然表达
        issues = 0
        
        # 检查重复词汇
        words = text.split()
        word_positions = {}
        for i, word in enumerate(words):
            if word in word_positions and i - word_positions[word] < 5:  # 5个词内重复
                issues += 1
            word_positions[word] = i
        
        # 检查不完整句子
        sentences = self._split_sentences(text)
        for sentence in sentences:
            if len(sentence.strip()) < 3:  # 过短的句子
                issues += 1
        
        # 计算流畅度分数
        total_elements = len(sentences) + len(words)
        fluency = max(0, 1 - issues / total_elements) if total_elements > 0 else 1.0
        return fluency
    
    def _check_redundancy(self, text: str) -> float:
        """检查冗余度"""
        sentences = self._split_sentences(text)
        if len(sentences) < 2:
            return 1.0
        
        # 计算句子间相似度
        redundancy_score = 0
        comparisons = 0
        
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                similarity = difflib.SequenceMatcher(None, sentences[i], sentences[j]).ratio()
                if similarity > 0.7:  # 高相似度阈值
                    redundancy_score += similarity
                comparisons += 1
        
        if comparisons == 0:
            return 1.0
        
        avg_redundancy = redundancy_score / comparisons
        return max(0, 1 - avg_redundancy)  # 冗余度越低，分数越高
    
    def _count_dialogue_turns(self, text: str) -> int:
        """统计对话轮次"""
        dialogue_markers = ['问：', '答：', '访谈者：', '被访者：']
        count = 0
        for marker in dialogue_markers:
            count += text.count(marker)
        return count
    
    def _count_sentences(self, text: str) -> int:
        """统计句子数量"""
        return len(self._split_sentences(text))
    
    def _split_sentences(self, text: str) -> List[str]:
        """分割句子"""
        # 类型检查和安全处理
        if not isinstance(text, str):
            if isinstance(text, list):
                # 如果传入的是列表，将其连接为字符串
                text = ' '.join(str(item) for item in text)
            else:
                # 其他类型转换为字符串
                text = str(text)
        
        if not text or not text.strip():
            return []
        
        # 按句号、问号、感叹号分割
        sentences = re.split(r'[。！？]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """计算综合评分"""
        try:
            scores = {
                "word_retention_rate": metrics.get("word_count", {}).get("retention_rate", 0),
                "content_preservation": metrics.get("content_preservation", {}).get("overall_preservation", 0),
                "coherence_score": metrics.get("language_quality", {}).get("coherence_score", 0),
                "first_person_consistency": metrics.get("language_quality", {}).get("first_person_consistency", 0),
                "redundancy_reduction": metrics.get("language_quality", {}).get("redundancy_score", 0)
            }
            
            # 加权平均
            weighted_score = sum(
                scores[key] * self.quality_weights[key] 
                for key in scores.keys() 
                if key in self.quality_weights
            )
            
            return round(weighted_score * 100, 2)  # 转换为0-100分制
            
        except Exception as e:
            logger.error(f"计算综合评分失败: {e}")
            return 0.0
    
    def _generate_quality_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成质量报告"""
        overall_score = metrics.get("overall_score", 0)
        
        # 评级
        if overall_score >= 90:
            grade = "优秀"
            grade_color = "green"
        elif overall_score >= 80:
            grade = "良好"
            grade_color = "blue"
        elif overall_score >= 70:
            grade = "中等"
            grade_color = "orange"
        elif overall_score >= 60:
            grade = "及格"
            grade_color = "yellow"
        else:
            grade = "需要改进"
            grade_color = "red"
        
        # 生成建议
        suggestions = []
        
        word_retention = metrics.get("word_count", {}).get("retention_rate", 0)
        if word_retention < 0.7:
            suggestions.append("文本压缩过度，可能丢失了重要信息")
        elif word_retention > 0.95:
            suggestions.append("文本压缩不足，可以进一步精简")
        
        content_preservation = metrics.get("content_preservation", {}).get("overall_preservation", 0)
        if content_preservation < 0.8:
            suggestions.append("关键信息保留不足，建议检查实体和关键词")
        
        coherence = metrics.get("language_quality", {}).get("coherence_score", 0)
        if coherence < 0.7:
            suggestions.append("文本连贯性有待提升，建议增加连接词")
        
        first_person = metrics.get("language_quality", {}).get("first_person_consistency", 0)
        if first_person < 0.8:
            suggestions.append("第一人称转换不够彻底，存在其他人称表述")
        
        return {
            "grade": grade,
            "grade_color": grade_color,
            "score": overall_score,
            "suggestions": suggestions,
            "summary": f"转换质量评级：{grade}（{overall_score:.1f}分）"
        }


# 创建全局质量服务实例
quality_service = QualityService() 