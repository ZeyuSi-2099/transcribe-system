"""
规则管理 API 端点
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select
from sqlalchemy.orm import Session

from app.core.database import SessionDep
from app.models.rule import (
    Rule, RuleSet,
    RuleCreate, RuleUpdate, RulePublic,
    RuleSetCreate, RuleSetUpdate, RuleSetPublic, RuleSetWithRules,
    RuleType, RuleScope
)
from app.services.rule_engine import rule_engine
from app.services.rule_service import RuleService
from pydantic import BaseModel

router = APIRouter()


# 规则管理 API

@router.post("/rules", response_model=RulePublic)
async def create_rule(rule_data: RuleCreate, session: SessionDep):
    """创建新规则"""
    # 验证规则
    validation_result = await rule_engine.validate_rule(rule_data.dict())
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"规则验证失败: {', '.join(validation_result['issues'])}"
        )
    
    # 创建规则
    rule = Rule(**rule_data.dict())
    session.add(rule)
    session.commit()
    session.refresh(rule)
    
    return rule


@router.get("/rules", response_model=List[RulePublic])
async def list_rules(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    rule_type: Optional[RuleType] = None,
    scope: Optional[RuleScope] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
):
    """获取规则列表"""
    statement = select(Rule)
    
    # 应用过滤条件
    if rule_type:
        statement = statement.where(Rule.rule_type == rule_type)
    if scope:
        statement = statement.where(Rule.scope == scope)
    if is_active is not None:
        statement = statement.where(Rule.is_active == is_active)
    if search:
        statement = statement.where(
            Rule.name.contains(search) | Rule.description.contains(search)
        )
    
    statement = statement.offset(skip).limit(limit).order_by(Rule.priority.desc(), Rule.created_at.desc())
    rules = session.exec(statement).all()
    
    return rules


@router.get("/rules/{rule_id}", response_model=RulePublic)
async def get_rule(rule_id: int, session: SessionDep):
    """获取规则详情"""
    rule = session.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return rule


@router.put("/rules/{rule_id}", response_model=RulePublic)
async def update_rule(rule_id: int, rule_update: RuleUpdate, session: SessionDep):
    """更新规则"""
    rule = session.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    # 验证更新的规则
    update_data = rule_update.dict(exclude_unset=True)
    if update_data:
        # 合并当前规则数据和更新数据进行验证
        rule_dict = rule.dict()
        rule_dict.update(update_data)
        validation_result = await rule_engine.validate_rule(rule_dict)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"规则验证失败: {', '.join(validation_result['issues'])}"
            )
    
    # 应用更新
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    rule.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(rule)
    
    return rule


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: int, session: SessionDep):
    """删除规则"""
    rule = session.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    session.delete(rule)
    session.commit()
    
    return {"message": "规则已删除"}


@router.post("/rules/{rule_id}/test")
async def test_rule(
    rule_id: int, 
    test_data: dict,
    session: SessionDep
):
    """测试规则效果"""
    rule = session.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    test_text = test_data.get("text", "")
    if not test_text:
        raise HTTPException(status_code=400, detail="测试文本不能为空")
    
    # 测试规则
    rule_dict = rule.dict()
    result = await rule_engine.test_rule(test_text, rule_dict)
    
    return result


# 规则集管理 API

@router.post("/rule-sets", response_model=RuleSetPublic)
async def create_rule_set(rule_set_data: RuleSetCreate, session: SessionDep):
    """创建新规则集"""
    # 验证规则ID是否存在
    if rule_set_data.rules:
        statement = select(Rule).where(Rule.id.in_(rule_set_data.rules))
        existing_rules = session.exec(statement).all()
        existing_rule_ids = [rule.id for rule in existing_rules]
        
        invalid_ids = set(rule_set_data.rules) - set(existing_rule_ids)
        if invalid_ids:
            raise HTTPException(
                status_code=400,
                detail=f"以下规则ID不存在: {list(invalid_ids)}"
            )
    
    # 创建规则集
    rule_set = RuleSet(**rule_set_data.dict())
    session.add(rule_set)
    session.commit()
    session.refresh(rule_set)
    
    return rule_set


@router.get("/rule-sets", response_model=List[RuleSetPublic])
async def list_rule_sets(
    session: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_default: Optional[bool] = None,
    is_public: Optional[bool] = None,
    search: Optional[str] = None
):
    """获取规则集列表"""
    statement = select(RuleSet)
    
    # 应用过滤条件
    if is_default is not None:
        statement = statement.where(RuleSet.is_default == is_default)
    if is_public is not None:
        statement = statement.where(RuleSet.is_public == is_public)
    if search:
        statement = statement.where(
            RuleSet.name.contains(search) | RuleSet.description.contains(search)
        )
    
    statement = statement.offset(skip).limit(limit).order_by(RuleSet.created_at.desc())
    rule_sets = session.exec(statement).all()
    
    return rule_sets


@router.get("/rule-sets/{rule_set_id}", response_model=RuleSetWithRules)
async def get_rule_set(rule_set_id: int, session: SessionDep):
    """获取规则集详情"""
    rule_set = session.get(RuleSet, rule_set_id)
    if not rule_set:
        raise HTTPException(status_code=404, detail="规则集不存在")
    
    # 获取规则集中的规则详情
    rule_details = []
    if rule_set.rules:
        statement = select(Rule).where(Rule.id.in_(rule_set.rules))
        rules = session.exec(statement).all()
        rule_details = [RulePublic.from_orm(rule) for rule in rules]
    
    # 构建带规则详情的规则集
    rule_set_with_rules = RuleSetWithRules(
        **rule_set.dict(),
        rule_details=rule_details
    )
    
    return rule_set_with_rules


@router.put("/rule-sets/{rule_set_id}", response_model=RuleSetPublic)
async def update_rule_set(
    rule_set_id: int, 
    rule_set_update: RuleSetUpdate, 
    session: SessionDep
):
    """更新规则集"""
    rule_set = session.get(RuleSet, rule_set_id)
    if not rule_set:
        raise HTTPException(status_code=404, detail="规则集不存在")
    
    # 验证规则ID是否存在
    update_data = rule_set_update.dict(exclude_unset=True)
    if "rules" in update_data and update_data["rules"]:
        statement = select(Rule).where(Rule.id.in_(update_data["rules"]))
        existing_rules = session.exec(statement).all()
        existing_rule_ids = [rule.id for rule in existing_rules]
        
        invalid_ids = set(update_data["rules"]) - set(existing_rule_ids)
        if invalid_ids:
            raise HTTPException(
                status_code=400,
                detail=f"以下规则ID不存在: {list(invalid_ids)}"
            )
    
    # 应用更新
    for field, value in update_data.items():
        setattr(rule_set, field, value)
    
    rule_set.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(rule_set)
    
    return rule_set


@router.delete("/rule-sets/{rule_set_id}")
async def delete_rule_set(rule_set_id: int, session: SessionDep):
    """删除规则集"""
    rule_set = session.get(RuleSet, rule_set_id)
    if not rule_set:
        raise HTTPException(status_code=404, detail="规则集不存在")
    
    session.delete(rule_set)
    session.commit()
    
    return {"message": "规则集已删除"}


@router.post("/rule-sets/{rule_set_id}/test")
async def test_rule_set(
    rule_set_id: int,
    test_data: dict,
    session: SessionDep
):
    """测试规则集效果"""
    rule_set = session.get(RuleSet, rule_set_id)
    if not rule_set:
        raise HTTPException(status_code=404, detail="规则集不存在")
    
    test_text = test_data.get("text", "")
    if not test_text:
        raise HTTPException(status_code=400, detail="测试文本不能为空")
    
    # 应用规则集
    result_text, rule_info = await rule_engine.apply_rules(
        test_text, rule_set_id
    )
    
    return {
        "success": True,
        "original_text": test_text,
        "result_text": result_text,
        "applied_rules": rule_info.get("applied_rules", []),
        "transformations": rule_info.get("transformations", []),
        "total_rules_applied": rule_info.get("total_rules_applied", 0)
    }


# 工具 API

@router.get("/rule-types")
async def get_rule_types():
    """获取规则类型列表"""
    return [
        {"value": RuleType.PREPROCESSING, "label": "预处理规则"},
        {"value": RuleType.DIALOGUE_STRUCTURE, "label": "对话结构规则"},
        {"value": RuleType.LANGUAGE_STYLE, "label": "语言风格规则"},
        {"value": RuleType.CONTENT_FILTER, "label": "内容过滤规则"},
        {"value": RuleType.POSTPROCESSING, "label": "后处理规则"}
    ]


@router.get("/rule-scopes")
async def get_rule_scopes():
    """获取规则范围列表"""
    return [
        {"value": RuleScope.GLOBAL, "label": "全局规则"},
        {"value": RuleScope.DOMAIN, "label": "领域特定规则"},
        {"value": RuleScope.USER, "label": "用户自定义规则"}
    ]


@router.get("/default-rules")
async def get_default_rules():
    """获取默认规则列表"""
    default_rules = await rule_engine._get_default_rules()
    return default_rules


class RuleGenerateRequest(BaseModel):
    description: str

@router.post("/generate")
async def generate_rule(request: RuleGenerateRequest, session: SessionDep):
    """
    根据自然语言描述生成规则
    """
    try:
        rule_service = RuleService(db)
        generated_rule = await rule_service.generate_rule_from_description(request.description)
        return generated_rule
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成规则失败: {str(e)}")

@router.get("/", response_model=List[Rule])
def get_rules(session: SessionDep):
    """
    获取所有规则
    """
    rule_service = RuleService(db)
    return rule_service.get_all_rules()

@router.post("/", response_model=Rule)
def create_rule(rule: RuleCreate, session: SessionDep):
    """
    创建新规则
    """
    rule_service = RuleService(db)
    return rule_service.create_rule(rule)

@router.get("/{rule_id}", response_model=Rule)
def get_rule(rule_id: int, session: SessionDep):
    """
    获取指定规则
    """
    rule_service = RuleService(db)
    rule = rule_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return rule

@router.put("/{rule_id}", response_model=Rule)
def update_rule(rule_id: int, rule: RuleUpdate, session: SessionDep):
    """
    更新规则
    """
    rule_service = RuleService(db)
    updated_rule = rule_service.update_rule(rule_id, rule)
    if not updated_rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return updated_rule

@router.delete("/{rule_id}")
def delete_rule(rule_id: int, session: SessionDep):
    """
    删除规则
    """
    rule_service = RuleService(db)
    success = rule_service.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="规则不存在")
    return {"message": "规则删除成功"} 