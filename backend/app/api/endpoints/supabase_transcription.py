"""
基于 Supabase 的笔录转换 API 端点
支持用户身份验证和数据隔离
"""

import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
import io
from pydantic import BaseModel
from loguru import logger

from app.core.auth import CurrentUser, AuthUser
from app.models.supabase_models import (
    ConversionHistory,
    ConversionHistoryCreate, 
    ConversionHistoryUpdate,
    ConversionHistorySummary
)
from app.services.supabase_service import ConversionHistoryService
from app.services.llm_service_simple import simple_llm_service

router = APIRouter()


class SimpleConversionRequest(BaseModel):
    text: str


class AdvancedConversionRequest(BaseModel):
    text: str
    rule_config: Optional[Dict[str, Any]] = None
    conversation_type: Optional[str] = None


@router.post("/upload", response_model=ConversionHistory)
async def upload_file_conversion(
    current_user: CurrentUser,
    file: UploadFile = File(...),
    rule_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    上传文件进行转换 (Supabase版本)
    支持 .txt, .docx 等文本文件格式
    """
    # 验证文件类型
    allowed_types = {
        'text/plain': 'txt',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'text/csv': 'csv'
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}。支持的类型: {', '.join(allowed_types.values())}"
        )
    
    # 验证文件大小 (10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="文件大小超过限制 (最大10MB)"
        )
    
    try:
        # 提取文本内容
        if file.content_type == 'text/plain':
            # 尝试不同编码
            for encoding in ['utf-8', 'gbk', 'gb2312']:
                try:
                    text_content = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise HTTPException(
                    status_code=400,
                    detail="无法解码文件内容，请确保文件为UTF-8或GBK编码"
                )
        elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # 处理Word文档
            try:
                from docx import Document
                doc = Document(io.BytesIO(content))
                text_content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"无法解析Word文档: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="不支持的文件格式"
            )
        
        # 验证文本长度
        if len(text_content) > 50000:
            raise HTTPException(
                status_code=400,
                detail="文件内容过长 (最大50000字符)"
            )
        
        if not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="文件内容为空"
            )
        
        # 创建转换记录
        conversion_service = ConversionHistoryService(
            current_user.user_id, 
            current_user.access_token
        )
        
        conversion_data = ConversionHistoryCreate(
            original_text=text_content,
            rule_id=rule_id,
            file_name=file.filename,
            file_size=len(content),
            metadata={
                "file_type": file.content_type,
                "upload_method": "file"
            }
        )
        
        conversion = await conversion_service.create_conversion(conversion_data)
        
        # 添加后台任务进行转换
        background_tasks.add_task(
            process_supabase_transcription,
            current_user.user_id,
            current_user.access_token,
            conversion.id,
            text_content,
            rule_id
        )
        
        return conversion
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件处理失败: {str(e)}"
        )


@router.post("/convert", response_model=ConversionHistory)
async def create_transcription(
    current_user: CurrentUser,
    original_text: str = Form(...),
    rule_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    直接文本转换 (Supabase版本)
    """
    # 验证文本长度
    if len(original_text) > 50000:
        raise HTTPException(
            status_code=400, 
            detail="文本长度超过限制 (最大50000字符)"
        )
    
    if not original_text.strip():
        raise HTTPException(
            status_code=400,
            detail="文本内容为空"
        )
    
    try:
        # 创建转换记录
        conversion_service = ConversionHistoryService(
            current_user.user_id, 
            current_user.access_token
        )
        
        conversion_data = ConversionHistoryCreate(
            original_text=original_text,
            rule_id=rule_id,
            metadata={
                "upload_method": "text"
            }
        )
        
        conversion = await conversion_service.create_conversion(conversion_data)
        
        # 添加后台任务进行转换
        background_tasks.add_task(
            process_supabase_transcription,
            current_user.user_id,
            current_user.access_token,
            conversion.id,
            original_text,
            rule_id
        )
        
        return conversion
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"转换任务创建失败: {str(e)}"
        )


@router.get("/history", response_model=List[ConversionHistorySummary])
async def list_conversion_history(
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    rule_id: Optional[str] = Query(None)
):
    """
    获取转换历史列表 (Supabase版本)
    """
    try:
        conversion_service = ConversionHistoryService(
            current_user.user_id, 
            current_user.access_token
        )
        
        return await conversion_service.list_conversions(
            skip=skip,
            limit=limit,
            search=search,
            rule_id=rule_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取历史记录失败: {str(e)}"
        )


@router.get("/history/{conversion_id}", response_model=ConversionHistory)
async def get_conversion_detail(
    conversion_id: str,
    current_user: CurrentUser
):
    """
    获取转换记录详情 (Supabase版本)
    """
    try:
        conversion_service = ConversionHistoryService(
            current_user.user_id, 
            current_user.access_token
        )
        
        conversion = await conversion_service.get_conversion(conversion_id)
        
        if not conversion:
            raise HTTPException(
                status_code=404,
                detail="转换记录不存在"
            )
        
        return conversion
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取转换详情失败: {str(e)}"
        )


@router.delete("/history/{conversion_id}")
async def delete_conversion(
    conversion_id: str,
    current_user: CurrentUser
):
    """
    删除转换记录 (Supabase版本)
    """
    try:
        conversion_service = ConversionHistoryService(
            current_user.user_id, 
            current_user.access_token
        )
        
        success = await conversion_service.delete_conversion(conversion_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="转换记录不存在或删除失败"
            )
        
        return {"message": "转换记录删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除转换记录失败: {str(e)}"
        )


@router.get("/stats")
async def get_user_stats(current_user: CurrentUser):
    """
    获取用户转换统计信息 (Supabase版本)
    """
    try:
        conversion_service = ConversionHistoryService(
            current_user.user_id, 
            current_user.access_token
        )
        
        return await conversion_service.get_user_stats()
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/convert/test", response_model=dict)
async def test_conversion(current_user: CurrentUser):
    """
    测试转换功能 (Supabase版本)
    """
    test_text = """
问：你昨天晚上在哪里？
答：我在家里看电视。
问：看的什么节目？
答：看的是新闻联播，然后又看了一个电视剧。
问：几点睡的？
答：大概11点左右就睡了。
"""
    
    try:
        start_time = time.time()
        result = await simple_llm_service.convert_transcription(test_text)
        processing_time = time.time() - start_time
        
        return {
            "original_text": test_text,
            "converted_text": result,
            "processing_time": round(processing_time, 2),
            "user_id": current_user.user_id,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "original_text": test_text,
            "error": str(e),
            "status": "failed",
            "user_id": current_user.user_id
        }


async def process_supabase_transcription(
    user_id: str,
    access_token: str,
    conversion_id: str,
    original_text: str,
    rule_id: Optional[str] = None
):
    """
    后台处理转换任务 (Supabase版本)
    """
    conversion_service = ConversionHistoryService(user_id, access_token)
    
    try:
        start_time = time.time()
        
        # 执行转换
        converted_text = await simple_llm_service.convert_transcription(original_text, rule_id)
        
        processing_time = time.time() - start_time
        
        # 更新转换结果
        update_data = ConversionHistoryUpdate(
            converted_text=converted_text,
            processing_time=processing_time,
            metadata={
                "status": "completed",
                "completion_time": datetime.utcnow().isoformat()
            }
        )
        
        await conversion_service.update_conversion(conversion_id, update_data)
        
    except Exception as e:
        # 记录错误
        error_data = ConversionHistoryUpdate(
            metadata={
                "status": "failed",
                "error": str(e),
                "failure_time": datetime.utcnow().isoformat()
            }
        )
        
        try:
            await conversion_service.update_conversion(conversion_id, error_data)
        except Exception:
            pass  # 忽略更新错误


@router.post("/convert/simple", response_model=dict)
async def simple_conversion_test(request: SimpleConversionRequest):
    """
    简单转换测试 (无需认证，支持自定义文本输入)
    """
    try:
        # 使用用户提供的文本
        input_text = request.text
        
        # 验证文本长度
        if len(input_text) > 10000:
            return {
                "success": False,
                "error": "文本长度超过限制 (最大10000字符)",
                "message": "文本过长，请缩短后重试"
            }
        
        if not input_text.strip():
            return {
                "success": False,
                "error": "文本内容为空",
                "message": "请输入有效的文本内容"
            }
        
        # 直接调用LLM服务进行转换
        start_time = time.time()
        result = await simple_llm_service.convert_transcription(input_text)
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "original_text": input_text,
            "converted_text": result,
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "model_used": "deepseek-chat",
            "message": "转换成功"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "转换失败，请检查网络连接或稍后重试"
        }


@router.post("/convert/advanced", response_model=dict)
async def advanced_conversion_test(request: AdvancedConversionRequest):
    """
    高级转换测试 (支持规则配置和对话类型)
    """
    try:
        # 使用用户提供的文本和配置
        input_text = request.text
        rule_config = request.rule_config or {}
        
        # 验证文本长度
        if len(input_text) > 10000:
            return {
                "success": False,
                "error": "文本长度超过限制 (最大10000字符)",
                "message": "文本过长，请缩短后重试"
            }
        
        if not input_text.strip():
            return {
                "success": False,
                "error": "文本内容为空",
                "message": "请输入有效的文本内容"
            }
        
        # 调用带规则配置的LLM服务
        start_time = time.time()
        result = await simple_llm_service.convert_transcription(input_text, rule_config)
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "original_text": input_text,
            "converted_text": result.get("converted_text", ""),
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "model_used": "deepseek-chat",
            "rule_config": rule_config,
            "quality_metrics": result.get("quality_metrics", {}),
            "conversion_summary": result.get("conversion_summary", {}),
            "message": "高级转换成功"
        }
        
    except Exception as e:
        logger.error(f"高级转换失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "转换失败，请检查网络连接或稍后重试"
        }


@router.post("/convert/smart", response_model=dict)
async def smart_conversion_test(request: SimpleConversionRequest):
    """
    智能转换 (自动检测对话类型并应用最佳规则)
    """
    try:
        from app.services.prompt_templates import prompt_manager
        
        input_text = request.text
        
        # 验证文本长度
        if len(input_text) > 10000:
            return {
                "success": False,
                "error": "文本长度超过限制 (最大10000字符)",
                "message": "文本过长，请缩短后重试"
            }
        
        if not input_text.strip():
            return {
                "success": False,
                "error": "文本内容为空",
                "message": "请输入有效的文本内容"
            }
        
        # 自动检测对话类型
        detected_type = prompt_manager.detect_conversation_type(input_text)
        
        # 获取推荐规则
        recommended_rules = prompt_manager.get_recommended_rules(detected_type)
        
        # 构建规则配置
        rule_config = {"rules": recommended_rules} if recommended_rules else {}
        
        # 调用LLM服务
        start_time = time.time()
        result = await simple_llm_service.convert_transcription(input_text, rule_config)
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "original_text": input_text,
            "converted_text": result.get("converted_text", ""),
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "model_used": "deepseek-chat",
            "detected_type": detected_type.value,
            "applied_rules": recommended_rules,
            "rule_config": rule_config,
            "quality_metrics": result.get("quality_metrics", {}),
            "conversion_summary": result.get("conversion_summary", {}),
            "message": f"智能转换成功 (检测为{detected_type.value}类型)"
        }
        
    except Exception as e:
        logger.error(f"智能转换失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "转换失败，请检查网络连接或稍后重试"
        }


@router.post("/convert/stream")
async def stream_conversion(request: AdvancedConversionRequest):
    """
    流式转换API - 实时返回转换进度和结果
    支持Server-Sent Events (SSE)
    """
    # 验证输入
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="文本内容为空"
        )
    
    if len(request.text) > 50000:
        raise HTTPException(
            status_code=400,
            detail="文本长度超过限制 (最大50000字符)"
        )
    
    try:
        logger.info(f"开始流式转换，文本长度: {len(request.text)}")
        
        # 返回流式响应
        return StreamingResponse(
            simple_llm_service.stream_convert_transcription(
                original_text=request.text,
                rule_config=request.rule_config
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except Exception as e:
        logger.error(f"流式转换API失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"流式转换失败: {str(e)}"
        )


@router.post("/convert/stream-simple")
async def stream_simple_conversion(request: SimpleConversionRequest):
    """
    简化版流式转换API - 使用默认配置
    """
    # 验证输入
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="文本内容为空"
        )
    
    if len(request.text) > 50000:
        raise HTTPException(
            status_code=400,
            detail="文本长度超过限制 (最大50000字符)"
        )
    
    try:
        logger.info(f"开始简化流式转换，文本长度: {len(request.text)}")
        
        # 返回流式响应
        return StreamingResponse(
            simple_llm_service.stream_convert_transcription(
                original_text=request.text,
                rule_config=None
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except Exception as e:
        logger.error(f"简化流式转换API失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"流式转换失败: {str(e)}"
        ) 