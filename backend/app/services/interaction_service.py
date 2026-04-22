"""
Service layer for user interactions: collections, likes, reports, and checkins.
"""
import logging
import uuid
from datetime import date, datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, select, update
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ErrorCode
from app.models.interaction import (
    ReportReason,
    ReportStatus,
    TargetType,
    UserCheckin,
    UserCollection,
    UserLike,
    UserReport,
)
from app.models.ledger import OrderType, PointLedger, PointType
from app.models.resources import Resource, ResourceStatus
from app.models.topic import Post, Topic, TopicStatus
from app.models.users import User

logger = logging.getLogger(__name__)


class InteractionService:
    """Service for user interactions (collect, like, report)"""

    def __init__(self, db: Session):
        self.db = db

    def like_resource(self, user_id: str, resource_id: str) -> dict:
        resource = self._get_resource(resource_id)
        existing = self._find_like(user_id, TargetType.RESOURCE, resource_id)
        if existing:
            raise BusinessException(ErrorCode.COM_4005, "您已点赞过该内容，请勿重复操作")

        like = UserLike(
            id=str(uuid.uuid4()),
            user_id=user_id,
            target_type=TargetType.RESOURCE,
            target_id=resource_id,
        )
        self.db.add(like)
        
        # 使用原子操作更新点赞计数
        stmt = update(Resource).where(Resource.id == resource_id).values(
            like_count=Resource.like_count + 1
        )
        self.db.execute(stmt)
        
        self.db.commit()
        
        # 重新获取更新后的计数
        updated_resource = self._get_resource(resource_id)
        return {"message": "点赞成功", "like_count": updated_resource.like_count}

    def unlike_resource(self, user_id: str, resource_id: str) -> dict:
        resource = self._get_resource(resource_id)
        existing = self._find_like(user_id, TargetType.RESOURCE, resource_id)
        if not existing:
            raise BusinessException(ErrorCode.COM_4005, "尚未点赞该内容")

        self.db.delete(existing)
        
        # 使用原子操作更新点赞计数
        stmt = update(Resource).where(Resource.id == resource_id).values(
            like_count=func.greatest(Resource.like_count - 1, 0)
        )
        self.db.execute(stmt)
        
        self.db.commit()
        
        # 重新获取更新后的计数
        updated_resource = self._get_resource(resource_id)
        return {"message": "取消点赞成功", "like_count": updated_resource.like_count}

    def collect_resource(self, user_id: str, resource_id: str) -> dict:
        self._get_resource(resource_id)
        existing = self._find_collection(user_id, TargetType.RESOURCE, resource_id)
        if existing:
            raise BusinessException(ErrorCode.COM_4005, "您已收藏过该资源")

        collection = UserCollection(
            id=str(uuid.uuid4()),
            user_id=user_id,
            target_type=TargetType.RESOURCE,
            target_id=resource_id,
        )
        self.db.add(collection)
        self.db.commit()
        return {"message": "收藏成功"}

    def uncollect_resource(self, user_id: str, resource_id: str) -> dict:
        self._get_resource(resource_id)
        existing = self._find_collection(user_id, TargetType.RESOURCE, resource_id)
        if not existing:
            raise BusinessException(ErrorCode.COM_4005, "尚未收藏该资源")

        self.db.delete(existing)
        self.db.commit()
        return {"message": "取消收藏成功"}

    def report_resource(self, user_id: str, resource_id: str, reason: str, detail: Optional[str] = None) -> dict:
        self._get_resource(resource_id)
        report = UserReport(
            id=str(uuid.uuid4()),
            user_id=user_id,
            target_type=TargetType.RESOURCE,
            target_id=resource_id,
            reason=reason,
            detail=detail,
            status=ReportStatus.PENDING,
        )
        self.db.add(report)
        self.db.commit()
        return {"message": "举报已提交，我们会尽快处理"}

    def like_topic(self, user_id: str, topic_id: str) -> dict:
        topic = self._get_topic(topic_id)
        existing = self._find_like(user_id, TargetType.TOPIC, topic_id)
        if existing:
            raise BusinessException(ErrorCode.COM_4005, "您已点赞过该内容，请勿重复操作")

        like = UserLike(
            id=str(uuid.uuid4()),
            user_id=user_id,
            target_type=TargetType.TOPIC,
            target_id=topic_id,
        )
        self.db.add(like)
        topic.like_count += 1
        self.db.commit()
        return {"message": "点赞成功", "like_count": topic.like_count}

    def unlike_topic(self, user_id: str, topic_id: str) -> dict:
        topic = self._get_topic(topic_id)
        existing = self._find_like(user_id, TargetType.TOPIC, topic_id)
        if not existing:
            raise BusinessException(ErrorCode.COM_4005, "尚未点赞该内容")

        self.db.delete(existing)
        topic.like_count = max(0, topic.like_count - 1)
        self.db.commit()
        return {"message": "取消点赞成功", "like_count": topic.like_count}

    def collect_topic(self, user_id: str, topic_id: str) -> dict:
        self._get_topic(topic_id)
        existing = self._find_collection(user_id, TargetType.TOPIC, topic_id)
        if existing:
            raise BusinessException(ErrorCode.COM_4005, "您已收藏过该话题")

        collection = UserCollection(
            id=str(uuid.uuid4()),
            user_id=user_id,
            target_type=TargetType.TOPIC,
            target_id=topic_id,
        )
        self.db.add(collection)
        self.db.commit()
        return {"message": "收藏成功"}

    def uncollect_topic(self, user_id: str, topic_id: str) -> dict:
        self._get_topic(topic_id)
        existing = self._find_collection(user_id, TargetType.TOPIC, topic_id)
        if not existing:
            raise BusinessException(ErrorCode.COM_4005, "尚未收藏该话题")

        self.db.delete(existing)
        self.db.commit()
        return {"message": "取消收藏成功"}

    def report_topic(self, user_id: str, topic_id: str, reason: str, detail: Optional[str] = None) -> dict:
        self._get_topic(topic_id)
        report = UserReport(
            id=str(uuid.uuid4()),
            user_id=user_id,
            target_type=TargetType.TOPIC,
            target_id=topic_id,
            reason=reason,
            detail=detail,
            status=ReportStatus.PENDING,
        )
        self.db.add(report)
        self.db.commit()
        return {"message": "举报已提交，我们会尽快处理"}

    def get_user_collections(
        self,
        user_id: str,
        target_type: Optional[TargetType] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[UserCollection], int]:
        filters = [UserCollection.user_id == user_id]
        if target_type:
            filters.append(UserCollection.target_type == target_type)

        count_query = select(func.count()).where(and_(*filters))
        total = self.db.execute(count_query).scalar()

        query = (
            select(UserCollection)
            .where(and_(*filters))
            .order_by(UserCollection.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = self.db.execute(query)
        collections = list(result.scalars().all())
        return collections, total

    def check_user_collected(self, user_id: str, target_type: TargetType, target_id: str) -> bool:
        existing = self._find_collection(user_id, target_type, target_id)
        return existing is not None

    def check_user_liked(self, user_id: str, target_type: TargetType, target_id: str) -> bool:
        existing = self._find_like(user_id, target_type, target_id)
        return existing is not None

    def _get_resource(self, resource_id: str) -> Resource:
        query = select(Resource).where(
            Resource.id == resource_id,
            Resource.is_deleted == False,
            Resource.status == ResourceStatus.APPROVED,
        )
        result = self.db.execute(query)
        resource = result.scalar_one_or_none()
        if not resource:
            raise BusinessException(ErrorCode.RES_4008, "资源不存在或已被删除")
        return resource

    def _get_topic(self, topic_id: str) -> Topic:
        query = select(Topic).where(
            Topic.id == topic_id,
            Topic.is_deleted == False,
            Topic.status == TopicStatus.NORMAL,
        )
        result = self.db.execute(query)
        topic = result.scalar_one_or_none()
        if not topic:
            raise BusinessException(ErrorCode.COM_4006, "话题不存在或已被删除")
        return topic

    def _find_like(self, user_id: str, target_type: TargetType, target_id: str) -> Optional[UserLike]:
        query = select(UserLike).where(
            UserLike.user_id == user_id,
            UserLike.target_type == target_type,
            UserLike.target_id == target_id,
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def _find_collection(self, user_id: str, target_type: TargetType, target_id: str) -> Optional[UserCollection]:
        query = select(UserCollection).where(
            UserCollection.user_id == user_id,
            UserCollection.target_type == target_type,
            UserCollection.target_id == target_id,
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()


class CheckinService:
    """Service for daily checkin"""

    def __init__(self, db: Session):
        self.db = db

    def checkin(self, user_id: str) -> dict:
        today = date.today().isoformat()

        existing_query = select(UserCheckin).where(
            UserCheckin.user_id == user_id,
            UserCheckin.checkin_date == today,
        )
        result = self.db.execute(existing_query)
        existing = result.scalar_one_or_none()

        if existing:
            return {
                "message": "今日已签到",
                "already_checked_in": True,
                "reward_beans": existing.reward_beans,
                "checkin_date": today,
            }

        user_query = select(User).where(User.id == user_id)
        user_result = self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        if not user:
            raise BusinessException(ErrorCode.AUTH_4000, "用户不存在")

        reward_beans = 5

        checkin = UserCheckin(
            id=str(uuid.uuid4()),
            user_id=user_id,
            checkin_date=today,
            reward_beans=reward_beans,
        )
        self.db.add(checkin)

        new_bonus = user.bonus_beans + reward_beans
        user.bonus_beans = new_bonus

        ledger = PointLedger(
            id=str(uuid.uuid4()),
            transaction_uuid=str(uuid.uuid4()),
            user_id=user_id,
            amount=reward_beans,
            point_type=PointType.BONUS_BEAN,
            order_type=OrderType.SIGN_IN,
            balance_after=new_bonus,
            description="每日签到奖励",
        )
        self.db.add(ledger)

        self.db.commit()
        logger.info(f"User {user_id} checked in, rewarded {reward_beans} bonus beans")

        return {
            "message": "签到成功",
            "already_checked_in": False,
            "reward_beans": reward_beans,
            "checkin_date": today,
        }

    def get_checkin_status(self, user_id: str) -> dict:
        today = date.today().isoformat()

        existing_query = select(UserCheckin).where(
            UserCheckin.user_id == user_id,
            UserCheckin.checkin_date == today,
        )
        result = self.db.execute(existing_query)
        existing = result.scalar_one_or_none()

        return {
            "checked_in_today": existing is not None,
            "checkin_date": today,
            "reward_beans": existing.reward_beans if existing else 0,
        }
