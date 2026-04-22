"""
User profile endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_db
from app.core.exceptions import BusinessException, ErrorCode
from app.models.users import User
from app.schemas.auth import UserInfoResponse
from app.schemas.interaction import UserProfileUpdateRequest

router = APIRouter()


@router.get("/me", response_model=UserInfoResponse, summary="获取当前用户信息")
def read_current_user(user: User = Depends(get_current_active_user)):
    return UserInfoResponse(
        id=user.id,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        rank=user.rank,
        reputation_points=user.reputation_points,
        gold_beans=user.gold_beans,
        bonus_beans=user.bonus_beans,
        is_reward_triggered=user.is_reward_triggered,
    )


@router.put("/me", response_model=UserInfoResponse, summary="更新当前用户资料")
def update_current_user(
    request: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    if request.nickname is not None:
        if len(request.nickname.strip()) == 0:
            raise BusinessException(ErrorCode.AUTH_4003, "昵称不能为空")
        user.nickname = request.nickname.strip()

    if request.avatar_url is not None:
        user.avatar_url = request.avatar_url

    db.commit()
    db.refresh(user)

    return UserInfoResponse(
        id=user.id,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        rank=user.rank,
        reputation_points=user.reputation_points,
        gold_beans=user.gold_beans,
        bonus_beans=user.bonus_beans,
        is_reward_triggered=user.is_reward_triggered,
    )
