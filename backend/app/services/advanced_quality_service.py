"""
阶段三：深度质量分析服务
提供更深入和全面的文本转换质量分析
"""

import re
import jieba
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import textstat
from loguru import logger
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import pandas as pd


class AdvancedQualityService:
    """深度质量分析服务"""
    
    def __init__(self):
        # 初始化jieba分词
        jieba.initialize()
        
        # 质量指标权重配置
        self.quality_weights = {
            "semantic_similarity": 0.25,        # 语义相似度
            "information_density": 0.20,        # 信息密度
            "narrative_coherence": 0.20,        # 叙述连贯性
            "style_consistency": 0.15,          # 风格一致性
            "readability_score": 0.10,          # 可读性评分
            "topic_preservation": 0.10,         # 主题保持度
        }
        
        # 中文停用词
        self.stop_words = {
            '的', '了', '在', '是', '我', '你', '他', '她', '它', '我们', '你们', '他们',
            '这', '那', '这个', '那个', '这些', '那些', '和', '或者', '但是', '然后',
            '因为', '所以', '如果', '虽然', '但是', '而且', '不过', '还有', '没有',
            '什么', '怎么', '为什么', '哪里', '什么时候', '怎样', '就是', '还是', '已经',
            '可以', '应该', '能够', '需要', '只是', '一些', '一个', '一种', '一直'
        }
    
    async def advanced_quality_analysis(
        self, 
        original_text: str, 
        converted_text: str,
        analysis_options: Dict[str, bool] = None
    ) -> Dict[str, Any]:
        """
        执行深度质量分析
        
        Args:
            original_text: 原始文本
            converted_text: 转换后文本
            analysis_options: 分析选项配置
            
        Returns:
            深度分析结果
        """
        try:
            # 默认分析选项
            options = analysis_options or {
                "semantic_analysis": True,
                "style_analysis": True,
                "readability_analysis": True,
                "topic_analysis": True,
                "visualization": True
            }
            
            logger.info("开始深度质量分析...")
            
            results = {
                "analysis_timestamp": pd.Timestamp.now().isoformat(),
                "analysis_options": options
            }
            
            # 1. 语义相似度分析
            if options.get("semantic_analysis", True):
                results["semantic_analysis"] = await self._semantic_similarity_analysis(
                    original_text, converted_text
                )
            
            # 2. 信息密度分析
            results["information_density"] = await self._information_density_analysis(
                original_text, converted_text
            )
            
            # 3. 叙述连贯性分析
            results["narrative_coherence"] = await self._narrative_coherence_analysis(
                converted_text
            )
            
            # 4. 风格一致性分析
            if options.get("style_analysis", True):
                results["style_consistency"] = await self._style_consistency_analysis(
                    original_text, converted_text
                )
            
            # 5. 可读性分析
            if options.get("readability_analysis", True):
                results["readability_analysis"] = await self._readability_analysis(
                    converted_text
                )
            
            # 6. 主题保持度分析
            if options.get("topic_analysis", True):
                results["topic_preservation"] = await self._topic_preservation_analysis(
                    original_text, converted_text
                )
            
            # 7. 计算综合深度评分
            results["advanced_score"] = self._calculate_advanced_score(results)
            
            # 8. 生成可视化图表
            if options.get("visualization", True):
                results["visualizations"] = await self._generate_visualizations(results)
            
            # 9. 生成深度质量报告
            results["advanced_report"] = self._generate_advanced_report(results)
            
            logger.info(f"深度质量分析完成，综合评分: {results['advanced_score']:.2f}")
            return results
            
        except Exception as e:
            logger.error(f"深度质量分析失败: {str(e)}")
            return {"error": str(e), "advanced_score": 0.0}
    
    async def _semantic_similarity_analysis(
        self, original: str, converted: str
    ) -> Dict[str, Any]:
        """语义相似度分析"""
        try:
            # 分词处理
            original_words = [w for w in jieba.cut(original) if w not in self.stop_words and len(w) > 1]
            converted_words = [w for w in jieba.cut(converted) if w not in self.stop_words and len(w) > 1]
            
            # TF-IDF向量化
            texts = [' '.join(original_words), ' '.join(converted_words)]
            
            if len(texts[0]) == 0 or len(texts[1]) == 0:
                return {"similarity_score": 0.0, "analysis": "文本为空或无有效词汇"}
            
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # 计算余弦相似度
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # 词汇重叠度分析
            original_set = set(original_words)
            converted_set = set(converted_words)
            
            overlap_ratio = len(original_set & converted_set) / len(original_set) if original_set else 0
            
            # 语义变化分析
            semantic_change = self._analyze_semantic_change(original_words, converted_words)
            
            return {
                "similarity_score": round(similarity, 4),
                "word_overlap_ratio": round(overlap_ratio, 4),
                "semantic_change": semantic_change,
                "analysis": self._interpret_semantic_similarity(similarity, overlap_ratio)
            }
            
        except Exception as e:
            logger.error(f"语义相似度分析失败: {e}")
            return {"similarity_score": 0.0, "error": str(e)}
    
    async def _information_density_analysis(
        self, original: str, converted: str
    ) -> Dict[str, Any]:
        """信息密度分析"""
        try:
            # 提取信息要素
            original_entities = self._extract_information_entities(original)
            converted_entities = self._extract_information_entities(converted)
            
            # 计算信息密度
            original_density = len(original_entities) / len(original) if original else 0
            converted_density = len(converted_entities) / len(converted) if converted else 0
            
            # 信息保留率
            preserved_entities = set(original_entities) & set(converted_entities)
            preservation_rate = len(preserved_entities) / len(original_entities) if original_entities else 1.0
            
            # 信息压缩效率
            compression_efficiency = converted_density / original_density if original_density > 0 else 0
            
            return {
                "original_density": round(original_density, 6),
                "converted_density": round(converted_density, 6),
                "information_preservation_rate": round(preservation_rate, 4),
                "compression_efficiency": round(compression_efficiency, 4),
                "preserved_entities": list(preserved_entities),
                "lost_entities": list(set(original_entities) - preserved_entities),
                "analysis": self._interpret_information_density(preservation_rate, compression_efficiency)
            }
            
        except Exception as e:
            logger.error(f"信息密度分析失败: {e}")
            return {"information_preservation_rate": 0.0, "error": str(e)}
    
    async def _narrative_coherence_analysis(self, text: str) -> Dict[str, Any]:
        """叙述连贯性分析"""
        try:
            sentences = self._split_sentences(text)
            if len(sentences) < 2:
                return {"coherence_score": 1.0, "analysis": "文本过短，无法评估连贯性"}
            
            # 1. 连接词使用分析
            connective_analysis = self._analyze_connectives(sentences)
            
            # 2. 时间序列一致性
            temporal_consistency = self._analyze_temporal_consistency(sentences)
            
            # 3. 代词指代一致性
            pronoun_consistency = self._analyze_pronoun_consistency(sentences)
            
            # 4. 主题连续性
            topic_continuity = self._analyze_topic_continuity(sentences)
            
            # 综合连贯性评分
            coherence_score = (
                connective_analysis["score"] * 0.3 +
                temporal_consistency * 0.25 +
                pronoun_consistency * 0.25 +
                topic_continuity * 0.2
            )
            
            return {
                "coherence_score": round(coherence_score, 4),
                "connective_analysis": connective_analysis,
                "temporal_consistency": round(temporal_consistency, 4),
                "pronoun_consistency": round(pronoun_consistency, 4),
                "topic_continuity": round(topic_continuity, 4),
                "analysis": self._interpret_coherence(coherence_score)
            }
            
        except Exception as e:
            logger.error(f"叙述连贯性分析失败: {e}")
            return {"coherence_score": 0.0, "error": str(e)}
    
    async def _style_consistency_analysis(
        self, original: str, converted: str
    ) -> Dict[str, Any]:
        """风格一致性分析"""
        try:
            # 1. 句子长度分布
            original_lengths = [len(s) for s in self._split_sentences(original)]
            converted_lengths = [len(s) for s in self._split_sentences(converted)]
            
            length_consistency = self._calculate_distribution_similarity(
                original_lengths, converted_lengths
            )
            
            # 2. 词汇复杂度
            original_complexity = self._calculate_lexical_complexity(original)
            converted_complexity = self._calculate_lexical_complexity(converted)
            
            complexity_consistency = 1 - abs(original_complexity - converted_complexity)
            
            # 3. 语调风格
            original_tone = self._analyze_tone_style(original)
            converted_tone = self._analyze_tone_style(converted)
            
            tone_consistency = self._calculate_tone_similarity(original_tone, converted_tone)
            
            # 4. 人称一致性
            person_consistency = self._analyze_person_consistency(converted)
            
            # 综合风格一致性
            style_score = (
                length_consistency * 0.25 +
                complexity_consistency * 0.25 +
                tone_consistency * 0.25 +
                person_consistency * 0.25
            )
            
            return {
                "style_consistency_score": round(style_score, 4),
                "length_consistency": round(length_consistency, 4),
                "complexity_consistency": round(complexity_consistency, 4),
                "tone_consistency": round(tone_consistency, 4),
                "person_consistency": round(person_consistency, 4),
                "original_tone": original_tone,
                "converted_tone": converted_tone,
                "analysis": self._interpret_style_consistency(style_score)
            }
            
        except Exception as e:
            logger.error(f"风格一致性分析失败: {e}")
            return {"style_consistency_score": 0.0, "error": str(e)}
    
    async def _readability_analysis(self, text: str) -> Dict[str, Any]:
        """可读性分析"""
        try:
            # 基础统计
            char_count = len(text)
            word_count = len(list(jieba.cut(text)))
            sentence_count = len(self._split_sentences(text))
            
            # 平均指标
            avg_chars_per_word = char_count / word_count if word_count > 0 else 0
            avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
            
            # 复杂度评估
            complexity_score = self._calculate_text_complexity(text)
            
            # 流畅度评估
            fluency_score = self._calculate_fluency_score(text)
            
            # 可读性评分 (0-100)
            readability_score = (
                (1 - min(complexity_score, 1.0)) * 50 +  # 复杂度越低，可读性越高
                fluency_score * 50  # 流畅度直接影响可读性
            )
            
            return {
                "readability_score": round(readability_score, 2),
                "character_count": char_count,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_chars_per_word": round(avg_chars_per_word, 2),
                "avg_words_per_sentence": round(avg_words_per_sentence, 2),
                "complexity_score": round(complexity_score, 4),
                "fluency_score": round(fluency_score, 4),
                "analysis": self._interpret_readability(readability_score)
            }
            
        except Exception as e:
            logger.error(f"可读性分析失败: {e}")
            return {"readability_score": 0.0, "error": str(e)}
    
    async def _topic_preservation_analysis(
        self, original: str, converted: str
    ) -> Dict[str, Any]:
        """主题保持度分析"""
        try:
            # 提取关键词
            original_keywords = self._extract_keywords_advanced(original)
            converted_keywords = self._extract_keywords_advanced(converted)
            
            # 主题词保留率
            if not original_keywords:
                return {"topic_preservation_score": 1.0, "analysis": "原文无明显主题词"}
            
            preserved_keywords = set(original_keywords) & set(converted_keywords)
            preservation_rate = len(preserved_keywords) / len(original_keywords)
            
            # 主题连贯性
            topic_coherence = self._calculate_topic_coherence(converted_keywords)
            
            # 主题集中度
            topic_focus = self._calculate_topic_focus(converted_keywords)
            
            # 综合主题保持度
            topic_score = (
                preservation_rate * 0.5 +
                topic_coherence * 0.3 +
                topic_focus * 0.2
            )
            
            return {
                "topic_preservation_score": round(topic_score, 4),
                "keyword_preservation_rate": round(preservation_rate, 4),
                "topic_coherence": round(topic_coherence, 4),
                "topic_focus": round(topic_focus, 4),
                "original_keywords": original_keywords[:10],  # 显示前10个
                "converted_keywords": converted_keywords[:10],
                "preserved_keywords": list(preserved_keywords)[:10],
                "analysis": self._interpret_topic_preservation(topic_score)
            }
            
        except Exception as e:
            logger.error(f"主题保持度分析失败: {e}")
            return {"topic_preservation_score": 0.0, "error": str(e)}
    
    def _calculate_advanced_score(self, results: Dict[str, Any]) -> float:
        """计算综合深度评分"""
        try:
            scores = {}
            
            # 提取各项评分
            if "semantic_analysis" in results:
                scores["semantic_similarity"] = results["semantic_analysis"].get("similarity_score", 0)
            
            if "information_density" in results:
                scores["information_density"] = results["information_density"].get("information_preservation_rate", 0)
            
            if "narrative_coherence" in results:
                scores["narrative_coherence"] = results["narrative_coherence"].get("coherence_score", 0)
            
            if "style_consistency" in results:
                scores["style_consistency"] = results["style_consistency"].get("style_consistency_score", 0)
            
            if "readability_analysis" in results:
                scores["readability_score"] = results["readability_analysis"].get("readability_score", 0) / 100
            
            if "topic_preservation" in results:
                scores["topic_preservation"] = results["topic_preservation"].get("topic_preservation_score", 0)
            
            # 加权平均
            weighted_score = sum(
                scores.get(key, 0) * weight 
                for key, weight in self.quality_weights.items()
                if key in scores
            )
            
            return round(weighted_score * 100, 2)  # 转换为0-100分制
            
        except Exception as e:
            logger.error(f"计算综合评分失败: {e}")
            return 0.0
    
    async def _generate_visualizations(self, results: Dict[str, Any]) -> Dict[str, str]:
        """生成可视化图表"""
        try:
            visualizations = {}
            
            # 1. 质量指标雷达图
            visualizations["radar_chart"] = self._create_radar_chart(results)
            
            # 2. 评分分布图
            visualizations["score_distribution"] = self._create_score_distribution(results)
            
            # 3. 时间序列图（如果有历史数据）
            # visualizations["trend_chart"] = self._create_trend_chart(results)
            
            return visualizations
            
        except Exception as e:
            logger.error(f"生成可视化图表失败: {e}")
            return {}
    
    def _generate_advanced_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成深度质量报告"""
        advanced_score = results.get("advanced_score", 0)
        
        # 评级
        if advanced_score >= 95:
            grade = "卓越"
            grade_color = "green"
        elif advanced_score >= 90:
            grade = "优秀"
            grade_color = "green"
        elif advanced_score >= 80:
            grade = "良好"
            grade_color = "blue"
        elif advanced_score >= 70:
            grade = "中等"
            grade_color = "orange"
        elif advanced_score >= 60:
            grade = "及格"
            grade_color = "yellow"
        else:
            grade = "需要改进"
            grade_color = "red"
        
        # 详细建议
        suggestions = self._generate_detailed_suggestions(results)
        
        # 分析摘要
        summary = self._generate_analysis_summary(results)
        
        return {
            "grade": grade,
            "grade_color": grade_color,
            "score": advanced_score,
            "suggestions": suggestions,
            "summary": summary,
            "detailed_analysis": self._extract_key_insights(results)
        }
    
    # 辅助方法实现...
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
        
        sentences = re.split(r'[。！？]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_information_entities(self, text: str) -> List[str]:
        """提取信息实体"""
        entities = []
        
        # 时间实体
        time_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{1,2}[点时](\d{1,2}分?)?',
            r'(昨天|今天|明天|前天|后天|上午|下午|晚上)',
        ]
        
        # 地点实体
        location_patterns = [
            r'在([^，。！？\s]{2,8})(里|内|中|上|下|旁|边)',
            r'(公司|学校|医院|银行|商店|餐厅|酒店|家|办公室)',
        ]
        
        # 人物实体
        person_patterns = [
            r'(先生|女士|老师|医生|经理|主任)',
            r'[A-Z][a-z]+',  # 英文姓名
        ]
        
        for pattern_list in [time_patterns, location_patterns, person_patterns]:
            for pattern in pattern_list:
                matches = re.findall(pattern, text)
                entities.extend([m if isinstance(m, str) else m[0] for m in matches])
        
        return list(set(entities))
    
    def _extract_keywords_advanced(self, text: str) -> List[str]:
        """高级关键词提取"""
        words = [w for w in jieba.cut(text) if w not in self.stop_words and len(w) > 1]
        
        # 计算词频
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序并返回前20个关键词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:20] if freq > 1]
    
    def _analyze_semantic_change(self, original_words: List[str], converted_words: List[str]) -> Dict[str, Any]:
        """分析语义变化"""
        added_words = set(converted_words) - set(original_words)
        removed_words = set(original_words) - set(converted_words)
        
        return {
            "added_words": list(added_words)[:10],
            "removed_words": list(removed_words)[:10],
            "change_ratio": len(added_words | removed_words) / len(set(original_words)) if original_words else 0
        }
    
    def _interpret_semantic_similarity(self, similarity: float, overlap: float) -> str:
        """解释语义相似度"""
        if similarity >= 0.8 and overlap >= 0.7:
            return "语义保持度优秀，转换质量很高"
        elif similarity >= 0.6 and overlap >= 0.5:
            return "语义保持度良好，转换基本准确"
        elif similarity >= 0.4:
            return "语义保持度一般，需要优化转换策略"
        else:
            return "语义保持度较低，转换存在较大偏差"
    
    def _interpret_information_density(self, preservation: float, efficiency: float) -> str:
        """解释信息密度"""
        if preservation >= 0.9 and efficiency >= 0.8:
            return "信息保留充分，压缩效率高"
        elif preservation >= 0.7:
            return "信息保留良好，压缩适度"
        elif preservation >= 0.5:
            return "信息保留一般，可能丢失重要内容"
        else:
            return "信息保留不足，存在重要信息丢失"
    
    def _analyze_connectives(self, sentences: List[str]) -> Dict[str, Any]:
        """分析连接词使用"""
        connectives = ['然后', '接着', '后来', '之后', '因此', '所以', '但是', '不过', '而且', '同时', '另外', '此外']
        connective_count = 0
        
        for sentence in sentences:
            for conn in connectives:
                if conn in sentence:
                    connective_count += 1
                    break
        
        density = connective_count / len(sentences) if sentences else 0
        score = min(density * 2, 1.0)  # 连接词密度评分
        
        return {
            "connective_count": connective_count,
            "connective_density": round(density, 4),
            "score": round(score, 4)
        }
    
    def _analyze_temporal_consistency(self, sentences: List[str]) -> float:
        """分析时间序列一致性"""
        # 简化版本：检查时间词的使用一致性
        time_words = ['然后', '接着', '后来', '之后', '最后', '首先', '其次', '再次']
        
        time_word_count = sum(1 for sentence in sentences for word in time_words if word in sentence)
        consistency = min(time_word_count / len(sentences), 1.0) if sentences else 0
        
        return consistency
    
    def _analyze_pronoun_consistency(self, sentences: List[str]) -> float:
        """分析代词指代一致性"""
        first_person_count = sum(sentence.count('我') + sentence.count('自己') for sentence in sentences)
        other_person_count = sum(sentence.count('你') + sentence.count('他') + sentence.count('她') for sentence in sentences)
        
        total_pronouns = first_person_count + other_person_count
        if total_pronouns == 0:
            return 1.0
        
        # 第一人称占比越高，一致性越好（因为是转换为被访者视角）
        consistency = first_person_count / total_pronouns
        return min(consistency * 1.2, 1.0)
    
    def _analyze_topic_continuity(self, sentences: List[str]) -> float:
        """分析主题连续性"""
        if len(sentences) < 2:
            return 1.0
        
        # 简化版本：计算相邻句子的词汇重叠度
        total_similarity = 0
        comparisons = 0
        
        for i in range(len(sentences) - 1):
            words1 = set(jieba.cut(sentences[i]))
            words2 = set(jieba.cut(sentences[i + 1]))
            
            if words1 and words2:
                overlap = len(words1 & words2) / len(words1 | words2)
                total_similarity += overlap
                comparisons += 1
        
        return total_similarity / comparisons if comparisons > 0 else 0
    
    def _calculate_distribution_similarity(self, dist1: List[float], dist2: List[float]) -> float:
        """计算分布相似度"""
        if not dist1 or not dist2:
            return 0.0
        
        # 使用KL散度的简化版本
        mean1, std1 = np.mean(dist1), np.std(dist1)
        mean2, std2 = np.mean(dist2), np.std(dist2)
        
        mean_diff = abs(mean1 - mean2) / max(mean1, mean2) if max(mean1, mean2) > 0 else 0
        std_diff = abs(std1 - std2) / max(std1, std2) if max(std1, std2) > 0 else 0
        
        similarity = 1 - (mean_diff + std_diff) / 2
        return max(similarity, 0)
    
    def _calculate_lexical_complexity(self, text: str) -> float:
        """计算词汇复杂度"""
        words = list(jieba.cut(text))
        if not words:
            return 0.0
        
        # 词汇丰富度 (Type-Token Ratio)
        unique_words = len(set(words))
        total_words = len(words)
        
        return unique_words / total_words if total_words > 0 else 0
    
    def _analyze_tone_style(self, text: str) -> Dict[str, float]:
        """分析语调风格"""
        # 简化版本：基于标点符号和特定词汇分析
        exclamation_count = text.count('！')
        question_count = text.count('？')
        period_count = text.count('。')
        
        total_sentences = exclamation_count + question_count + period_count
        
        if total_sentences == 0:
            return {"neutral": 1.0, "excited": 0.0, "questioning": 0.0}
        
        return {
            "neutral": period_count / total_sentences,
            "excited": exclamation_count / total_sentences,
            "questioning": question_count / total_sentences
        }
    
    def _calculate_tone_similarity(self, tone1: Dict[str, float], tone2: Dict[str, float]) -> float:
        """计算语调相似度"""
        similarity = 0
        for key in tone1:
            if key in tone2:
                similarity += 1 - abs(tone1[key] - tone2[key])
        
        return similarity / len(tone1) if tone1 else 0
    
    def _analyze_person_consistency(self, text: str) -> float:
        """分析人称一致性"""
        # 与之前quality_service中的方法类似
        first_person = len(re.findall(r'我|自己', text))
        second_person = len(re.findall(r'你|您', text))
        third_person = len(re.findall(r'他|她|它|他们|她们|它们', text))
        
        total_pronouns = first_person + second_person + third_person
        
        if total_pronouns == 0:
            return 1.0
        
        consistency = first_person / total_pronouns
        return min(consistency * 1.2, 1.0)
    
    def _calculate_text_complexity(self, text: str) -> float:
        """计算文本复杂度"""
        sentences = self._split_sentences(text)
        if not sentences:
            return 0.0
        
        # 平均句子长度
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
        
        # 词汇复杂度
        lexical_complexity = self._calculate_lexical_complexity(text)
        
        # 标准化复杂度分数
        length_complexity = min(avg_sentence_length / 50, 1.0)  # 50字为基准
        
        return (length_complexity + lexical_complexity) / 2
    
    def _calculate_fluency_score(self, text: str) -> float:
        """计算流畅度评分"""
        # 检查重复词汇
        words = list(jieba.cut(text))
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 重复度惩罚
        repetition_penalty = sum(1 for freq in word_freq.values() if freq > 3) / len(words) if words else 0
        
        # 句子完整性检查
        sentences = self._split_sentences(text)
        incomplete_sentences = sum(1 for s in sentences if len(s) < 5)
        completeness_penalty = incomplete_sentences / len(sentences) if sentences else 0
        
        fluency = 1 - repetition_penalty - completeness_penalty
        return max(fluency, 0)
    
    def _calculate_topic_coherence(self, keywords: List[str]) -> float:
        """计算主题连贯性"""
        if len(keywords) < 2:
            return 1.0
        
        # 简化版本：基于词汇共现分析
        # 这里可以扩展为更复杂的主题模型
        return 0.8  # 占位符值
    
    def _calculate_topic_focus(self, keywords: List[str]) -> float:
        """计算主题集中度"""
        if not keywords:
            return 0.0
        
        # 基于关键词分布的集中度
        # 这里可以使用更复杂的算法
        return 0.75  # 占位符值
    
    def _interpret_coherence(self, score: float) -> str:
        """解释连贯性评分"""
        if score >= 0.9:
            return "叙述连贯性优秀，逻辑清晰"
        elif score >= 0.7:
            return "叙述连贯性良好，表达流畅"
        elif score >= 0.5:
            return "叙述连贯性一般，逻辑稍显松散"
        else:
            return "叙述连贯性较差，需要优化逻辑结构"
    
    def _interpret_style_consistency(self, score: float) -> str:
        """解释风格一致性"""
        if score >= 0.9:
            return "风格转换一致性优秀，保持统一"
        elif score >= 0.7:
            return "风格转换一致性良好，基本统一"
        elif score >= 0.5:
            return "风格转换一致性一般，存在不统一之处"
        else:
            return "风格转换一致性较差，风格变化较大"
    
    def _interpret_readability(self, score: float) -> str:
        """解释可读性评分"""
        if score >= 90:
            return "可读性优秀，易于理解"
        elif score >= 80:
            return "可读性良好，表达清晰"
        elif score >= 70:
            return "可读性一般，稍显复杂"
        else:
            return "可读性较差，表达复杂难懂"
    
    def _interpret_topic_preservation(self, score: float) -> str:
        """解释主题保持度"""
        if score >= 0.9:
            return "主题保持度优秀，核心内容完整"
        elif score >= 0.7:
            return "主题保持度良好，主要内容保留"
        elif score >= 0.5:
            return "主题保持度一般，部分主题模糊"
        else:
            return "主题保持度较差，主题偏离较大"
    
    def _create_radar_chart(self, results: Dict[str, Any]) -> str:
        """创建雷达图"""
        try:
            # 提取各项指标
            metrics = {
                "语义相似度": results.get("semantic_analysis", {}).get("similarity_score", 0) * 100,
                "信息密度": results.get("information_density", {}).get("information_preservation_rate", 0) * 100,
                "叙述连贯性": results.get("narrative_coherence", {}).get("coherence_score", 0) * 100,
                "风格一致性": results.get("style_consistency", {}).get("style_consistency_score", 0) * 100,
                "可读性": results.get("readability_analysis", {}).get("readability_score", 0),
                "主题保持度": results.get("topic_preservation", {}).get("topic_preservation_score", 0) * 100
            }
            
            # 创建雷达图
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False)
            values = list(metrics.values())
            labels = list(metrics.keys())
            
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            ax.plot(angles, values, 'o-', linewidth=2, label='质量评分')
            ax.fill(angles, values, alpha=0.25)
            ax.set_xticks(angles)
            ax.set_xticklabels(labels, fontsize=10)
            ax.set_ylim(0, 100)
            ax.set_title('质量分析雷达图', fontsize=14, fontweight='bold', pad=20)
            ax.grid(True)
            
            # 转换为base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"创建雷达图失败: {e}")
            return ""
    
    def _create_score_distribution(self, results: Dict[str, Any]) -> str:
        """创建评分分布图"""
        try:
            # 提取评分数据
            scores = {
                "语义相似度": results.get("semantic_analysis", {}).get("similarity_score", 0) * 100,
                "信息密度": results.get("information_density", {}).get("information_preservation_rate", 0) * 100,
                "叙述连贯性": results.get("narrative_coherence", {}).get("coherence_score", 0) * 100,
                "风格一致性": results.get("style_consistency", {}).get("style_consistency_score", 0) * 100,
                "可读性": results.get("readability_analysis", {}).get("readability_score", 0),
                "主题保持度": results.get("topic_preservation", {}).get("topic_preservation_score", 0) * 100
            }
            
            # 创建柱状图
            fig, ax = plt.subplots(figsize=(12, 6))
            bars = ax.bar(scores.keys(), scores.values(), color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'])
            
            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}', ha='center', va='bottom', fontsize=10)
            
            ax.set_ylabel('评分', fontsize=12)
            ax.set_title('各项质量指标评分分布', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 100)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # 转换为base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"创建评分分布图失败: {e}")
            return ""
    
    def _generate_detailed_suggestions(self, results: Dict[str, Any]) -> List[str]:
        """生成详细建议"""
        suggestions = []
        
        # 基于各项指标给出建议
        semantic_score = results.get("semantic_analysis", {}).get("similarity_score", 0)
        if semantic_score < 0.7:
            suggestions.append("语义保持度偏低，建议检查关键信息是否完整转换")
        
        info_preservation = results.get("information_density", {}).get("information_preservation_rate", 0)
        if info_preservation < 0.8:
            suggestions.append("信息保留不足，建议增强关键信息识别和保留机制")
        
        coherence_score = results.get("narrative_coherence", {}).get("coherence_score", 0)
        if coherence_score < 0.7:
            suggestions.append("叙述连贯性有待提升，建议增加逻辑连接词和过渡语句")
        
        style_score = results.get("style_consistency", {}).get("style_consistency_score", 0)
        if style_score < 0.7:
            suggestions.append("风格一致性需要改进，建议统一语言风格和表达方式")
        
        readability_score = results.get("readability_analysis", {}).get("readability_score", 0)
        if readability_score < 80:
            suggestions.append("可读性可以进一步提升，建议简化复杂句式和用词")
        
        topic_score = results.get("topic_preservation", {}).get("topic_preservation_score", 0)
        if topic_score < 0.8:
            suggestions.append("主题保持度有提升空间，建议加强主题词汇的保留")
        
        if not suggestions:
            suggestions.append("转换质量整体表现优秀，建议继续保持当前标准")
        
        return suggestions
    
    def _generate_analysis_summary(self, results: Dict[str, Any]) -> str:
        """生成分析摘要"""
        advanced_score = results.get("advanced_score", 0)
        
        if advanced_score >= 90:
            return f"本次转换质量评分{advanced_score:.1f}分，达到优秀水平。各项指标表现均衡，转换效果理想。"
        elif advanced_score >= 80:
            return f"本次转换质量评分{advanced_score:.1f}分，达到良好水平。整体表现不错，部分指标仍有提升空间。"
        elif advanced_score >= 70:
            return f"本次转换质量评分{advanced_score:.1f}分，达到中等水平。转换基本完成，但在某些方面需要改进。"
        else:
            return f"本次转换质量评分{advanced_score:.1f}分，有较大提升空间。建议重点关注低分项指标的改进。"
    
    def _extract_key_insights(self, results: Dict[str, Any]) -> List[str]:
        """提取关键洞察"""
        insights = []
        
        # 分析各项指标的表现
        semantic_score = results.get("semantic_analysis", {}).get("similarity_score", 0)
        if semantic_score >= 0.9:
            insights.append("语义转换准确度极高，内容保真度优秀")
        
        info_density = results.get("information_density", {}).get("compression_efficiency", 0)
        if info_density >= 0.8:
            insights.append("信息压缩效率高，在保持信息完整性的同时实现了有效精简")
        
        coherence = results.get("narrative_coherence", {}).get("coherence_score", 0)
        if coherence >= 0.9:
            insights.append("叙述逻辑清晰，文本连贯性强")
        
        person_consistency = results.get("style_consistency", {}).get("person_consistency", 0)
        if person_consistency >= 0.9:
            insights.append("人称转换彻底，成功实现被访者视角")
        
        if not insights:
            insights.append("转换过程中各项指标表现平均，建议针对性优化")
        
        return insights


# 创建全局深度质量服务实例
advanced_quality_service = AdvancedQualityService() 