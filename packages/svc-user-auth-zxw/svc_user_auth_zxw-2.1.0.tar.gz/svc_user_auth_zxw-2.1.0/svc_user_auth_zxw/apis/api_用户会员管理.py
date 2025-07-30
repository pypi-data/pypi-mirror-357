"""
# File       : api_用户会员管理.py
# Time       ：2024/12/20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：用户会员管理API
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from svc_user_auth_zxw.db.models import User, Membership, MembershipType, MembershipStatus
from svc_user_auth_zxw.db.get_db import get_db
from svc_user_auth_zxw.SDK_jwt.jwt import get_current_user
from svc_user_auth_zxw.apis.schemas import (
    用户购买会员请求, 用户会员响应, 用户会员状态更新请求, 通用响应
)
from app_tools_zxw.Errors.api_errors import HTTPException_AppToolsSZXW
from svc_user_auth_zxw.tools.error_code import ErrorCode

router = APIRouter(prefix="/memberships", tags=["用户会员管理"])


def _convert_membership_to_response(membership: Membership) -> 用户会员响应:
    """将Membership对象转换为响应格式"""
    return 用户会员响应(
        id=membership.id,
        user_id=membership.user_id,
        membership_type_id=membership.membership_type_id,
        membership_type_name=membership.membership_type.name,
        start_time=membership.start_time,
        end_time=membership.end_time,
        status=membership.status.value,
        created_at=membership.created_at,
        updated_at=membership.updated_at,
        notes=membership.notes,
        is_valid=membership.is_valid()
    )


@router.post("/purchase", response_model=通用响应[用户会员响应])
async def 购买会员(
        request: 用户购买会员请求,
        db: AsyncSession = Depends(get_db)
):
    """用户购买会员"""
    try:
        # 检查用户是否存在
        user_result = await db.execute(
            select(User).where(User.id == request.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="用户不存在",
                http_status_code=404
            )

        # 检查会员类型是否存在且启用
        membership_type_result = await db.execute(
            select(MembershipType).where(
                MembershipType.id == request.membership_type_id,
                MembershipType.is_active == True
            )
        )
        membership_type = membership_type_result.scalar_one_or_none()
        if not membership_type:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员类型不存在或已停用",
                http_status_code=400
            )

        # 检查用户是否已有相同类型的活跃会员
        existing_membership_result = await db.execute(
            select(Membership).where(
                Membership.user_id == request.user_id,
                Membership.membership_type_id == request.membership_type_id,
                Membership.status == MembershipStatus.ACTIVE
            )
        )
        existing_membership = existing_membership_result.scalar_one_or_none()

        now = datetime.utcnow()

        if existing_membership and existing_membership.is_valid():
            # 如果已有有效会员，延长到期时间
            existing_membership.end_time = existing_membership.end_time + timedelta(days=membership_type.duration_days)
            existing_membership.updated_at = now
            if request.notes:
                existing_membership.notes = f"{existing_membership.notes or ''}\n{request.notes}".strip()

            await db.commit()
            await db.refresh(existing_membership)

            return 通用响应(
                data=_convert_membership_to_response(existing_membership),
                message="会员时长已延长"
            )
        else:
            # 创建新的会员记录
            start_time = now
            end_time = start_time + timedelta(days=membership_type.duration_days)

            new_membership = Membership(
                user_id=request.user_id,
                membership_type_id=request.membership_type_id,
                start_time=start_time,
                end_time=end_time,
                status=MembershipStatus.ACTIVE,
                notes=request.notes
            )

            db.add(new_membership)
            await db.commit()
            await db.refresh(new_membership)

            # 加载关联的membership_type
            await db.refresh(new_membership, ["membership_type"])

            return 通用响应(
                data=_convert_membership_to_response(new_membership),
                message="会员开通成功"
            )

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"购买会员失败: {str(e)}",
            http_status_code=500
        )


@router.get("/my", response_model=通用响应[List[用户会员响应]])
async def 获取我的会员(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """获取当前用户的会员列表"""
    try:
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(Membership.user_id == current_user.id)
            .order_by(Membership.created_at.desc())
        )
        memberships = result.scalars().all()

        return 通用响应(
            data=[_convert_membership_to_response(m) for m in memberships],
            message="获取成功"
        )

    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取会员列表失败: {str(e)}",
            http_status_code=500
        )


@router.get("/user/{user_id}", response_model=通用响应[List[用户会员响应]])
async def 获取用户会员(
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    """管理员获取指定用户的会员列表"""
    try:
        # 检查用户是否存在
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="用户不存在",
                http_status_code=404
            )

        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(Membership.user_id == user_id)
            .order_by(Membership.created_at.desc())
        )
        memberships = result.scalars().all()

        return 通用响应(
            data=[_convert_membership_to_response(m) for m in memberships],
            message="获取成功"
        )

    except Exception as e:
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取用户会员列表失败: {str(e)}",
            http_status_code=500
        )


@router.get("/{membership_id}", response_model=通用响应[用户会员响应])
async def 获取会员详情(
        membership_id: int,
        db: AsyncSession = Depends(get_db)
):
    """获取会员详情"""
    try:
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(Membership.id == membership_id)
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员记录不存在",
                http_status_code=404
            )

        return 通用响应(
            data=_convert_membership_to_response(membership),
            message="获取成功"
        )

    except Exception as e:
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取会员详情失败: {str(e)}",
            http_status_code=500
        )


@router.put("/{membership_id}/status", response_model=通用响应[用户会员响应])
async def 更新会员状态(
        membership_id: int,
        request: 用户会员状态更新请求,
        db: AsyncSession = Depends(get_db)
):
    """更新会员状态（管理员功能）"""
    try:
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(Membership.id == membership_id)
        )
        membership = result.scalar_one_or_none()

        if not membership:
            raise HTTPException_AppToolsSZXW(
                error_code=ErrorCode.参数错误,
                detail="会员记录不存在",
                http_status_code=404
            )

        # 更新状态
        membership.status = MembershipStatus(request.status.value)
        membership.updated_at = datetime.utcnow()

        if request.notes:
            membership.notes = f"{membership.notes or ''}\n{request.notes}".strip()

        await db.commit()
        await db.refresh(membership)

        return 通用响应(
            data=_convert_membership_to_response(membership),
            message="会员状态更新成功"
        )

    except Exception as e:
        await db.rollback()
        if isinstance(e, HTTPException_AppToolsSZXW):
            raise
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"更新会员状态失败: {str(e)}",
            http_status_code=500
        )


@router.get("/active/all", response_model=通用响应[List[用户会员响应]])
async def 获取所有活跃会员(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    """获取所有活跃会员列表（管理员功能）"""
    try:
        now = datetime.utcnow()
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(
                Membership.status == MembershipStatus.ACTIVE,
                Membership.start_time <= now,
                Membership.end_time >= now
            )
            .offset(skip)
            .limit(limit)
            .order_by(Membership.end_time.asc())
        )
        memberships = result.scalars().all()

        return 通用响应(
            data=[_convert_membership_to_response(m) for m in memberships],
            message="获取成功"
        )

    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取活跃会员列表失败: {str(e)}",
            http_status_code=500
        )


@router.get("/expired/all", response_model=通用响应[List[用户会员响应]])
async def 获取所有过期会员(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    """获取所有过期会员列表（管理员功能）"""
    try:
        now = datetime.utcnow()
        result = await db.execute(
            select(Membership)
            .options(selectinload(Membership.membership_type))
            .where(
                Membership.status == MembershipStatus.ACTIVE,
                Membership.end_time < now
            )
            .offset(skip)
            .limit(limit)
            .order_by(Membership.end_time.desc())
        )
        memberships = result.scalars().all()

        return 通用响应(
            data=[_convert_membership_to_response(m) for m in memberships],
            message="获取成功"
        )

    except Exception as e:
        raise HTTPException_AppToolsSZXW(
            error_code=ErrorCode.系统异常,
            detail=f"获取过期会员列表失败: {str(e)}",
            http_status_code=500
        )
