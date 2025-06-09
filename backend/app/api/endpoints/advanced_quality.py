"""
阶段三：深度质量分析API端点
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from loguru import logger

from app.services.advanced_quality_service import advanced_quality_service
from app.models.transcription import Transcription
from app.core.database import get_session
from sqlmodel import select

router = APIRouter(prefix="/advanced-quality", tags=["advanced-quality"])


class AdvancedQualityRequest(BaseModel):
    """深度质量分析请求"""
    original_text: str = Field(..., description="原始文本")
    converted_text: str = Field(..., description="转换后文本")
    analysis_options: Optional[Dict[str, bool]] = Field(
        default={
            "semantic_analysis": True,
            "style_analysis": True,
            "readability_analysis": True,
            "topic_analysis": True,
            "visualization": True
        },
        description="分析选项配置"
    )


class BatchQualityRequest(BaseModel):
    """批量质量分析请求"""
    record_ids: List[int] = Field(..., description="转换记录ID列表")
    analysis_options: Optional[Dict[str, bool]] = Field(default=None, description="分析选项配置")


class QualityComparisonRequest(BaseModel):
    """质量对比分析请求"""
    record_id_1: int = Field(..., description="第一个转换记录ID")
    record_id_2: int = Field(..., description="第二个转换记录ID")


@router.post("/analyze")
async def advanced_quality_analysis(request: AdvancedQualityRequest):
    """
    执行深度质量分析
    """
    try:
        logger.info("开始深度质量分析...")
        
        if not request.original_text.strip() or not request.converted_text.strip():
            raise HTTPException(status_code=400, detail="原始文本和转换文本不能为空")
        
        # 执行深度分析
        result = await advanced_quality_service.advanced_quality_analysis(
            original_text=request.original_text,
            converted_text=request.converted_text,
            analysis_options=request.analysis_options
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"分析失败: {result['error']}")
        
        logger.info(f"深度质量分析完成，评分: {result.get('advanced_score', 0)}")
        
        return {
            "success": True,
            "message": "深度质量分析完成",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"深度质量分析API错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.post("/analyze-record/{record_id}")
async def analyze_transcription_record(record_id: int, analysis_options: Optional[Dict[str, bool]] = None):
    """
    对指定转换记录执行深度质量分析
    """
    try:
        async with get_session() as session:
            # 查询转换记录
            statement = select(Transcription).where(Transcription.id == record_id)
            result = await session.exec(statement)
            record = result.first()
            
            if not record:
                raise HTTPException(status_code=404, detail="转换记录未找到")
            
            if not record.result_text:
                raise HTTPException(status_code=400, detail="转换记录没有结果文本")
            
            # 执行深度分析
            analysis_result = await advanced_quality_service.advanced_quality_analysis(
                original_text=record.original_text,
                converted_text=record.result_text,
                analysis_options=analysis_options
            )
            
            if "error" in analysis_result:
                raise HTTPException(status_code=500, detail=f"分析失败: {analysis_result['error']}")
            
            # 更新记录的质量分析结果
            if record.quality_metrics:
                record.quality_metrics["advanced_analysis"] = analysis_result
            else:
                record.quality_metrics = {"advanced_analysis": analysis_result}
            
            session.add(record)
            await session.commit()
            
            return {
                "success": True,
                "message": "转换记录深度质量分析完成",
                "data": {
                    "record_id": record_id,
                    "analysis_result": analysis_result
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转换记录深度分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.post("/batch-analyze")
async def batch_quality_analysis(request: BatchQualityRequest, background_tasks: BackgroundTasks):
    """
    批量质量分析
    """
    try:
        if not request.record_ids:
            raise HTTPException(status_code=400, detail="记录ID列表不能为空")
        
        if len(request.record_ids) > 50:
            raise HTTPException(status_code=400, detail="单次批量分析最多支持50条记录")
        
        logger.info(f"开始批量质量分析，记录数量: {len(request.record_ids)}")
        
        # 添加后台任务
        background_tasks.add_task(
            _execute_batch_analysis,
            request.record_ids,
            request.analysis_options
        )
        
        return {
            "success": True,
            "message": f"批量质量分析任务已启动，共{len(request.record_ids)}条记录",
            "data": {
                "record_count": len(request.record_ids),
                "status": "processing"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量质量分析API错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.post("/compare")
async def quality_comparison_analysis(request: QualityComparisonRequest):
    """
    质量对比分析
    """
    try:
        async with get_session() as session:
            # 查询两个转换记录
            statement1 = select(Transcription).where(Transcription.id == request.record_id_1)
            statement2 = select(Transcription).where(Transcription.id == request.record_id_2)
            
            result1 = await session.exec(statement1)
            result2 = await session.exec(statement2)
            
            record1 = result1.first()
            record2 = result2.first()
            
            if not record1:
                raise HTTPException(status_code=404, detail=f"转换记录 {request.record_id_1} 未找到")
            if not record2:
                raise HTTPException(status_code=404, detail=f"转换记录 {request.record_id_2} 未找到")
            
            # 执行两次深度分析
            analysis1 = await advanced_quality_service.advanced_quality_analysis(
                original_text=record1.original_text,
                converted_text=record1.result_text,
                analysis_options={"semantic_analysis": True, "style_analysis": True, "readability_analysis": True, "topic_analysis": True, "visualization": False}
            )
            
            analysis2 = await advanced_quality_service.advanced_quality_analysis(
                original_text=record2.original_text,
                converted_text=record2.result_text,
                analysis_options={"semantic_analysis": True, "style_analysis": True, "readability_analysis": True, "topic_analysis": True, "visualization": False}
            )
            
            # 生成对比报告
            comparison_result = _generate_comparison_report(analysis1, analysis2, record1, record2)
            
            return {
                "success": True,
                "message": "质量对比分析完成",
                "data": comparison_result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"质量对比分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/trends")
async def quality_trends_analysis(user_id: Optional[str] = None, limit: int = 20):
    """
    质量趋势分析
    """
    try:
        async with get_session() as session:
            # 构建查询
            statement = select(Transcription).order_by(Transcription.created_at.desc()).limit(limit)
            
            if user_id:
                statement = statement.where(Transcription.user_id == user_id)
            
            result = await session.exec(statement)
            records = result.all()
            
            if not records:
                return {
                    "success": True,
                    "message": "暂无转换记录",
                    "data": {"trends": [], "summary": {"total_records": 0}}
                }
            
            # 分析质量趋势
            trends_data = []
            total_score = 0
            score_count = 0
            
            for record in records:
                if record.quality_metrics and "overall_score" in record.quality_metrics:
                    score = record.quality_metrics["overall_score"]
                    trends_data.append({
                        "record_id": record.id,
                        "created_at": record.created_at.isoformat(),
                        "quality_score": score,
                        "file_name": record.file_name or "文本输入"
                    })
                    total_score += score
                    score_count += 1
            
            # 计算趋势统计
            avg_score = total_score / score_count if score_count > 0 else 0
            trends_analysis = _analyze_quality_trends(trends_data)
            
            return {
                "success": True,
                "message": "质量趋势分析完成",
                "data": {
                    "trends": trends_data,
                    "summary": {
                        "total_records": len(records),
                        "analyzed_records": score_count,
                        "average_score": round(avg_score, 2),
                        "trend_analysis": trends_analysis
                    }
                }
            }
            
    except Exception as e:
        logger.error(f"质量趋势分析错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/statistics")
async def quality_statistics():
    """
    质量统计概览
    """
    try:
        async with get_session() as session:
            # 查询所有有质量评分的记录
            statement = select(Transcription).where(Transcription.quality_metrics.isnot(None))
            result = await session.exec(statement)
            records = result.all()
            
            if not records:
                return {
                    "success": True,
                    "message": "暂无质量统计数据",
                    "data": {"statistics": {}}
                }
            
            # 统计分析
            scores = []
            advanced_scores = []
            
            for record in records:
                metrics = record.quality_metrics
                if metrics:
                    if "overall_score" in metrics:
                        scores.append(metrics["overall_score"])
                    
                    if "advanced_analysis" in metrics and "advanced_score" in metrics["advanced_analysis"]:
                        advanced_scores.append(metrics["advanced_analysis"]["advanced_score"])
            
            statistics = {
                "total_analyzed_records": len(records),
                "basic_quality_stats": _calculate_score_statistics(scores) if scores else {},
                "advanced_quality_stats": _calculate_score_statistics(advanced_scores) if advanced_scores else {},
                "quality_distribution": _calculate_quality_distribution(scores) if scores else {},
                "advanced_distribution": _calculate_quality_distribution(advanced_scores) if advanced_scores else {}
            }
            
            return {
                "success": True,
                "message": "质量统计完成",
                "data": {"statistics": statistics}
            }
            
    except Exception as e:
        logger.error(f"质量统计错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


# 辅助函数
async def _execute_batch_analysis(record_ids: List[int], analysis_options: Optional[Dict[str, bool]]):
    """执行批量分析的后台任务"""
    try:
        logger.info(f"开始批量分析任务，记录数量: {len(record_ids)}")
        
        async with get_session() as session:
            for record_id in record_ids:
                try:
                    # 查询记录
                    statement = select(Transcription).where(Transcription.id == record_id)
                    result = await session.exec(statement)
                    record = result.first()
                    
                    if not record or not record.result_text:
                        logger.warning(f"跳过记录 {record_id}: 记录不存在或无结果文本")
                        continue
                    
                    # 执行深度分析
                    analysis_result = await advanced_quality_service.advanced_quality_analysis(
                        original_text=record.original_text,
                        converted_text=record.result_text,
                        analysis_options=analysis_options or {"semantic_analysis": True, "style_analysis": True, "readability_analysis": True, "topic_analysis": True, "visualization": False}
                    )
                    
                    # 更新记录
                    if record.quality_metrics:
                        record.quality_metrics["advanced_analysis"] = analysis_result
                    else:
                        record.quality_metrics = {"advanced_analysis": analysis_result}
                    
                    session.add(record)
                    await session.commit()
                    
                    logger.info(f"记录 {record_id} 深度分析完成")
                    
                except Exception as e:
                    logger.error(f"批量分析记录 {record_id} 失败: {e}")
                    continue
        
        logger.info("批量分析任务完成")
        
    except Exception as e:
        logger.error(f"批量分析任务失败: {e}")


def _generate_comparison_report(analysis1: Dict[str, Any], analysis2: Dict[str, Any], record1: Transcription, record2: Transcription) -> Dict[str, Any]:
    """生成对比报告"""
    try:
        score1 = analysis1.get("advanced_score", 0)
        score2 = analysis2.get("advanced_score", 0)
        
        comparison = {
            "record_1": {
                "id": record1.id,
                "file_name": record1.file_name or "文本输入",
                "score": score1,
                "analysis": analysis1.get("advanced_report", {})
            },
            "record_2": {
                "id": record2.id,
                "file_name": record2.file_name or "文本输入",
                "score": score2,
                "analysis": analysis2.get("advanced_report", {})
            },
            "comparison_result": {
                "score_difference": round(score2 - score1, 2),
                "better_record": record2.id if score2 > score1 else record1.id,
                "performance_analysis": _analyze_performance_difference(analysis1, analysis2)
            }
        }
        
        return comparison
        
    except Exception as e:
        logger.error(f"生成对比报告失败: {e}")
        return {"error": str(e)}


def _analyze_performance_difference(analysis1: Dict[str, Any], analysis2: Dict[str, Any]) -> Dict[str, Any]:
    """分析性能差异"""
    try:
        differences = {}
        
        # 比较各项指标
        metrics = ["semantic_analysis", "information_density", "narrative_coherence", "style_consistency", "readability_analysis", "topic_preservation"]
        
        for metric in metrics:
            if metric in analysis1 and metric in analysis2:
                score1 = _extract_metric_score(analysis1[metric])
                score2 = _extract_metric_score(analysis2[metric])
                
                if score1 is not None and score2 is not None:
                    differences[metric] = {
                        "score_1": score1,
                        "score_2": score2,
                        "difference": round(score2 - score1, 4),
                        "improvement": score2 > score1
                    }
        
        return differences
        
    except Exception as e:
        logger.error(f"分析性能差异失败: {e}")
        return {}


def _extract_metric_score(metric_data: Dict[str, Any]) -> Optional[float]:
    """提取指标评分"""
    if isinstance(metric_data, dict):
        # 根据不同指标类型提取评分
        score_keys = ["similarity_score", "information_preservation_rate", "coherence_score", "style_consistency_score", "readability_score", "topic_preservation_score"]
        
        for key in score_keys:
            if key in metric_data:
                score = metric_data[key]
                # 可读性评分已经是0-100，其他需要转换
                return score if key == "readability_score" else score * 100
    
    return None


def _analyze_quality_trends(trends_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析质量趋势"""
    try:
        if len(trends_data) < 2:
            return {"trend": "insufficient_data", "analysis": "数据不足，无法分析趋势"}
        
        scores = [item["quality_score"] for item in trends_data]
        
        # 计算趋势方向
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        trend_direction = "improving" if avg_second > avg_first else "declining" if avg_second < avg_first else "stable"
        
        # 计算变化幅度
        change_magnitude = abs(avg_second - avg_first)
        
        return {
            "trend": trend_direction,
            "change_magnitude": round(change_magnitude, 2),
            "first_half_avg": round(avg_first, 2),
            "second_half_avg": round(avg_second, 2),
            "analysis": _interpret_trend(trend_direction, change_magnitude)
        }
        
    except Exception as e:
        logger.error(f"分析质量趋势失败: {e}")
        return {"trend": "error", "analysis": f"分析失败: {str(e)}"}


def _interpret_trend(direction: str, magnitude: float) -> str:
    """解释趋势"""
    if direction == "improving":
        if magnitude > 10:
            return "质量显著提升，转换效果持续改善"
        elif magnitude > 5:
            return "质量稳步提升，转换能力逐渐增强"
        else:
            return "质量略有提升，保持良好发展趋势"
    elif direction == "declining":
        if magnitude > 10:
            return "质量明显下降，需要重点关注和改进"
        elif magnitude > 5:
            return "质量有所下降，建议检查转换策略"
        else:
            return "质量略有下降，需要适当调整"
    else:
        return "质量保持稳定，转换效果基本一致"


def _calculate_score_statistics(scores: List[float]) -> Dict[str, float]:
    """计算评分统计"""
    try:
        import statistics
        
        return {
            "count": len(scores),
            "average": round(statistics.mean(scores), 2),
            "median": round(statistics.median(scores), 2),
            "min": round(min(scores), 2),
            "max": round(max(scores), 2),
            "std_dev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0
        }
        
    except Exception as e:
        logger.error(f"计算评分统计失败: {e}")
        return {}


def _calculate_quality_distribution(scores: List[float]) -> Dict[str, int]:
    """计算质量分布"""
    try:
        distribution = {
            "excellent": 0,    # 90-100
            "good": 0,         # 80-89
            "fair": 0,         # 70-79
            "poor": 0          # <70
        }
        
        for score in scores:
            if score >= 90:
                distribution["excellent"] += 1
            elif score >= 80:
                distribution["good"] += 1
            elif score >= 70:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1
        
        return distribution
        
    except Exception as e:
        logger.error(f"计算质量分布失败: {e}")
        return {} 