"""
笔录转换 API 端点
"""

import time
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlmodel import select
import io

from app.core.database import SessionDep
from app.models.transcription import (
    Transcription, 
    TranscriptionCreate, 
    TranscriptionPublic,
    TranscriptionSummary,
    TranscriptionStatus
)
from app.services.llm_service import llm_service

router = APIRouter()


@router.post("/upload", response_model=TranscriptionPublic)
async def upload_file_conversion(
    file: UploadFile = File(...),
    title: str = Form(None),
    rule_config: str = Form("{}"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: SessionDep = None
):
    """
    上传文件进行转换
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
        
        # 解析规则配置
        import json
        try:
            rule_config_dict = json.loads(rule_config) if rule_config else {}
        except json.JSONDecodeError:
            rule_config_dict = {}
        
        # 创建转换记录
        transcription = Transcription(
            title=title or f"文件转换-{file.filename}",
            original_text=text_content,
            file_name=file.filename,
            file_type=file.content_type,
            rule_config=rule_config_dict,
            status=TranscriptionStatus.PENDING
        )
        
        session.add(transcription)
        session.commit()
        session.refresh(transcription)
        
        # 添加后台任务进行转换
        background_tasks.add_task(
            process_transcription,
            transcription.id,
            text_content,
            rule_config_dict
        )
        
        return transcription
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件处理失败: {str(e)}"
        )


@router.post("/convert", response_model=TranscriptionPublic)
async def create_transcription(
    transcription_data: TranscriptionCreate,
    background_tasks: BackgroundTasks,
    session: SessionDep
):
    """
    创建新的转换任务
    """
    # 验证文本长度
    if len(transcription_data.original_text) > 50000:
        raise HTTPException(
            status_code=400, 
            detail="文本长度超过限制 (最大50000字符)"
        )
    
    # 创建转换记录
    transcription = Transcription(
        title=transcription_data.title,
        original_text=transcription_data.original_text,
        file_name=transcription_data.file_name,
        file_type=transcription_data.file_type,
        rule_config=transcription_data.rule_config,
        status=TranscriptionStatus.PENDING
    )
    
    session.add(transcription)
    session.commit()
    session.refresh(transcription)
    
    # 添加后台任务进行转换
    background_tasks.add_task(
        process_transcription, 
        transcription.id, 
        transcription_data.original_text,
        transcription_data.rule_config
    )
    
    return transcription


@router.get("/convert/test", response_model=dict)
async def test_conversion():
    """
    测试转换功能
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
        result = await llm_service.convert_transcription(test_text)
        processing_time = time.time() - start_time
        
        if result.get("success"):
            return {
                "success": True,
                "original_text": test_text.strip(),
                "converted_text": result.get("converted_text"),
                "processing_time": round(processing_time, 2),
                "quality_score": result.get("quality_metrics", {}).get("overall_score", 0),
                "conversion_summary": result.get("conversion_summary", {}),
                "processing_stages": result.get("processing_stages", {})
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"转换测试失败: {result.get('error', '未知错误')}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"转换测试失败: {str(e)}")


@router.get("/{transcription_id}", response_model=TranscriptionPublic)
async def get_transcription(transcription_id: int, session: SessionDep):
    """
    获取转换记录详情
    """
    transcription = session.get(Transcription, transcription_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="转换记录不存在")
    
    return transcription


@router.get("/", response_model=List[TranscriptionSummary])
async def list_transcriptions(
    session: SessionDep,
    skip: int = 0, 
    limit: int = 20
):
    """
    获取转换记录列表
    """
    statement = select(Transcription).offset(skip).limit(limit).order_by(Transcription.created_at.desc())
    transcriptions = session.exec(statement).all()
    
    return [
        TranscriptionSummary(
            id=t.id,
            title=t.title,
            status=t.status,
            created_at=t.created_at,
            processing_time=t.processing_time
        )
        for t in transcriptions
    ]


@router.delete("/{transcription_id}")
async def delete_transcription(transcription_id: int, session: SessionDep):
    """
    删除转换记录
    """
    transcription = session.get(Transcription, transcription_id)
    if not transcription:
        raise HTTPException(status_code=404, detail="转换记录不存在")
    
    session.delete(transcription)
    session.commit()
    
    return {"message": "转换记录已删除"}


async def process_transcription(
    transcription_id: int, 
    original_text: str, 
    rule_config: dict = None
):
    """
    后台处理转换任务
    """
    from app.core.database import engine
    from sqlmodel import Session
    
    with Session(engine) as session:
        try:
            # 获取转换记录
            transcription = session.get(Transcription, transcription_id)
            if not transcription:
                return
            
            # 更新状态为处理中
            transcription.status = TranscriptionStatus.PROCESSING
            transcription.updated_at = datetime.utcnow()
            session.commit()
            
            # 执行转换
            start_time = time.time()
            conversion_result = await llm_service.convert_transcription(
                original_text, 
                rule_config
            )
            processing_time = time.time() - start_time
            
            if conversion_result.get("success"):
                # 更新转换结果
                transcription.converted_text = conversion_result.get("converted_text")
                transcription.status = TranscriptionStatus.COMPLETED
                transcription.completed_at = datetime.utcnow()
                transcription.processing_time = processing_time
                transcription.updated_at = datetime.utcnow()
                
                # 保存详细的质量指标
                quality_metrics = conversion_result.get("quality_metrics", {})
                conversion_summary = conversion_result.get("conversion_summary", {})
                
                # 整合质量指标
                transcription.quality_metrics = {
                    **quality_metrics,
                    "conversion_summary": conversion_summary,
                    "processing_stages": conversion_result.get("processing_stages", {})
                }
                
                session.commit()
                
            else:
                # 处理失败
                transcription.status = TranscriptionStatus.FAILED
                transcription.error_message = conversion_result.get("error", "转换失败")
                transcription.updated_at = datetime.utcnow()
                session.commit()
                
        except Exception as e:
            # 处理异常
            transcription = session.get(Transcription, transcription_id)
            if transcription:
                transcription.status = TranscriptionStatus.FAILED
                transcription.error_message = str(e)
                transcription.updated_at = datetime.utcnow()
                session.commit() 