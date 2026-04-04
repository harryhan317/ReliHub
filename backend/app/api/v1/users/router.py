"""
User profile endpoints.
"""
from fastapi import APIRouter, Depends

from app.core.deps import get_current_active_user
from app.models.users import User
from app.schemas.auth import UserInfoResponse

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
