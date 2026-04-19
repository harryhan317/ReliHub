"""
Service layer for Admin module.
"""
import hashlib
import json
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ErrorCode
from app.models.administrators import AdminAuditLog, AdminUser
from app.models.feedback import Feedback, FeedbackStatus
from app.models.ledger import AssetPackage
from app.models.resources import Resource, ResourceStatus
from app.models.system_config import SystemConfig
from app.models.topic import Post, Topic, TopicStatus
from app.models.users import User
from app.schemas.admin import (
    AssetPackageUpdateRequest,
    BanUserRequest,
    FeedbackReplyRequest,
    LockUserRequest,
    ResourceReviewRequest,
    SystemConfigUpdateRequest,
)


class AdminService:
    """Service class for Admin management"""

    def __init__(self, db: Session, admin: AdminUser):
        self.db = db
        self.admin = admin

    def _create_audit_log(
        self,
        action: str,
        target_type: str,
        target_id: str,
        before_data: dict,
        after_data: dict,
        ip_address: Optional[str] = None
    ) -> AdminAuditLog:
        last_log = self.db.execute(
            select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(1)
        ).scalar_one_or_none()
        prev_hash = last_log.log_hash if last_log else "0" * 64
        
        log_data = f"{self.admin.id}{action}{target_type}{target_id}{json.dumps(before_data, sort_keys=True)}{json.dumps(after_data, sort_keys=True)}{prev_hash}"
        log_hash = hashlib.sha256(log_data.encode()).hexdigest()
        
        log = AdminAuditLog(
            id=str(uuid.uuid4()),
            admin_id=self.admin.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            before_data=json.dumps(before_data),
            after_data=json.dumps(after_data),
            ip_address=ip_address,
            prev_log_hash=prev_hash,
            log_hash=log_hash
        )
        self.db.add(log)
        return log

    def check_permission(self, allowed_roles: List[str]) -> bool:
        if self.admin.role not in allowed_roles:
            raise BusinessException(ErrorCode.ADMIN_4002, "权限不足")
        return True

    def list_users(
        self,
        status: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[User], int]:
        filters = []
        
        if status:
            filters.append(User.status == status)
        
        if search:
            filters.append(
                or_(
                    User.nickname.ilike(f"%{search}%"),
                    User.phone.ilike(f"%{search}%")
                )
            )
        
        count_query = select(func.count()).where(and_(*filters)) if filters else select(func.count()).select_from(User)
        total = self.db.execute(count_query).scalar() or 0
        
        query = select(User)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        
        result = self.db.execute(query)
        users = result.scalars().all()
        
        return list(users), total

    def get_user(self, user_id: str) -> Optional[User]:
        return self.db.get(User, user_id)

    def ban_user(self, user_id: str, request: BanUserRequest, ip_address: Optional[str] = None) -> User:
        self.check_permission(["SUPER_ADMIN", "OPERATOR"])
        
        user = self.get_user(user_id)
        if not user:
            raise BusinessException(ErrorCode.ADMIN_4004, "用户不存在")
        
        before_data = {"status": user.status}
        user.status = "DISABLED"
        after_data = {"status": "DISABLED", "reason": request.reason}
        
        self._create_audit_log(
            action="BAN_USER",
            target_type="users",
            target_id=user_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def unban_user(self, user_id: str, ip_address: Optional[str] = None) -> User:
        self.check_permission(["SUPER_ADMIN", "OPERATOR"])
        
        user = self.get_user(user_id)
        if not user:
            raise BusinessException(ErrorCode.ADMIN_4004, "用户不存在")
        
        before_data = {"status": user.status}
        user.status = "ACTIVE"
        after_data = {"status": "ACTIVE"}
        
        self._create_audit_log(
            action="UNBAN_USER",
            target_type="users",
            target_id=user_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def lock_user(self, user_id: str, request: LockUserRequest, ip_address: Optional[str] = None) -> User:
        self.check_permission(["SUPER_ADMIN", "OPERATOR"])
        
        user = self.get_user(user_id)
        if not user:
            raise BusinessException(ErrorCode.ADMIN_4004, "用户不存在")
        
        before_data = {"status": user.status}
        user.status = "LOCKED"
        after_data = {"status": "LOCKED", "reason": request.reason}
        
        self._create_audit_log(
            action="LOCK_USER",
            target_type="users",
            target_id=user_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def unlock_user(self, user_id: str, ip_address: Optional[str] = None) -> User:
        self.check_permission(["SUPER_ADMIN", "OPERATOR"])
        
        user = self.get_user(user_id)
        if not user:
            raise BusinessException(ErrorCode.ADMIN_4004, "用户不存在")
        
        before_data = {"status": user.status}
        user.status = "ACTIVE"
        after_data = {"status": "ACTIVE"}
        
        self._create_audit_log(
            action="UNLOCK_USER",
            target_type="users",
            target_id=user_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_pending_resources(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Resource], int]:
        filters = [Resource.status == ResourceStatus.PENDING_REVIEW]
        
        count_query = select(func.count()).where(and_(*filters))
        total = self.db.execute(count_query).scalar() or 0
        
        query = (
            select(Resource)
            .where(and_(*filters))
            .order_by(Resource.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = self.db.execute(query)
        resources = result.scalars().all()
        
        return list(resources), total

    def list_resources(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Resource], int]:
        filters = []
        if status:
            try:
                status_enum = ResourceStatus(status)
                filters.append(Resource.status == status_enum)
            except ValueError:
                pass
        
        count_query = select(func.count()).where(and_(*filters)) if filters else select(func.count())
        total = self.db.execute(count_query).scalar() or 0
        
        query = select(Resource).order_by(Resource.created_at.desc())
        if filters:
            query = query.where(and_(*filters))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = self.db.execute(query)
        resources = result.scalars().all()
        
        return list(resources), total

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        return self.db.get(Resource, resource_id)

    def approve_resource(self, resource_id: str, request: ResourceReviewRequest, ip_address: Optional[str] = None) -> Resource:
        self.check_permission(["SUPER_ADMIN", "OPERATOR"])
        
        resource = self.get_resource(resource_id)
        if not resource:
            raise BusinessException(ErrorCode.ADMIN_4005, "资源不存在")
        
        before_data = {"status": resource.status.value}
        resource.status = ResourceStatus.APPROVED
        after_data = {"status": "APPROVED", "reason": request.reason}
        
        self._create_audit_log(
            action="APPROVE_RESOURCE",
            target_type="resources",
            target_id=resource_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def reject_resource(self, resource_id: str, request: ResourceReviewRequest, ip_address: Optional[str] = None) -> Resource:
        self.check_permission(["SUPER_ADMIN", "OPERATOR"])
        
        resource = self.get_resource(resource_id)
        if not resource:
            raise BusinessException(ErrorCode.ADMIN_4005, "资源不存在")
        
        before_data = {"status": resource.status.value}
        resource.status = ResourceStatus.REJECTED
        after_data = {"status": "REJECTED", "reason": request.reason}
        
        self._create_audit_log(
            action="REJECT_RESOURCE",
            target_type="resources",
            target_id=resource_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def block_resource(self, resource_id: str, request: ResourceReviewRequest, ip_address: Optional[str] = None) -> Resource:
        self.check_permission(["SUPER_ADMIN", "OPERATOR"])
        
        resource = self.get_resource(resource_id)
        if not resource:
            raise BusinessException(ErrorCode.ADMIN_4005, "资源不存在")
        
        before_data = {"status": resource.status.value}
        resource.status = ResourceStatus.BLOCKED
        after_data = {"status": "BLOCKED", "reason": request.reason}
        
        self._create_audit_log(
            action="BLOCK_RESOURCE",
            target_type="resources",
            target_id=resource_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(resource)
        return resource

    def list_topics(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Topic], int]:
        filters = [Topic.is_deleted == False]
        
        if status:
            filters.append(Topic.status == status)
        
        count_query = select(func.count()).where(and_(*filters))
        total = self.db.execute(count_query).scalar() or 0
        
        query = (
            select(Topic)
            .where(and_(*filters))
            .order_by(Topic.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = self.db.execute(query)
        topics = result.scalars().all()
        
        return list(topics), total

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        return self.db.get(Topic, topic_id)

    def block_topic(self, topic_id: str, request: ResourceReviewRequest, ip_address: Optional[str] = None) -> Topic:
        self.check_permission(["SUPER_ADMIN", "OPERATOR"])
        
        topic = self.get_topic(topic_id)
        if not topic:
            raise BusinessException(ErrorCode.ADMIN_4006, "话题不存在")
        
        before_data = {"status": topic.status.value}
        topic.status = TopicStatus.BLOCKED
        after_data = {"status": "BLOCKED", "reason": request.reason}
        
        self._create_audit_log(
            action="BLOCK_TOPIC",
            target_type="topics",
            target_id=topic_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def list_audit_logs(
        self,
        admin_id: Optional[str] = None,
        action: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[AdminAuditLog], int]:
        filters = []
        
        if admin_id:
            filters.append(AdminAuditLog.admin_id == admin_id)
        
        if action:
            filters.append(AdminAuditLog.action == action)
        
        count_query = select(func.count()).where(and_(*filters)) if filters else select(func.count()).select_from(AdminAuditLog)
        total = self.db.execute(count_query).scalar() or 0
        
        query = select(AdminAuditLog)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(AdminAuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        
        result = self.db.execute(query)
        logs = result.scalars().all()
        
        return list(logs), total

    def get_audit_log(self, log_id: str) -> Optional[AdminAuditLog]:
        return self.db.get(AdminAuditLog, log_id)

    def list_system_configs(self) -> List[SystemConfig]:
        query = select(SystemConfig).order_by(SystemConfig.config_key)
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_system_config(self, config_key: str) -> Optional[SystemConfig]:
        query = select(SystemConfig).where(SystemConfig.config_key == config_key)
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def update_system_config(
        self,
        request: SystemConfigUpdateRequest,
        ip_address: Optional[str] = None
    ) -> SystemConfig:
        self.check_permission(["SUPER_ADMIN"])
        
        # Validate config_key format
        try:
            request.validate_config_key()
        except ValueError as e:
            raise BusinessException(
                ErrorCode.ADMIN_4002,
                str(e)
            )
        
        # Validate config_key against whitelist
        allowed_keys = [
            "site_name",
            "site_description",
            "max_upload_size",
            "feature_flags",
            "maintenance_mode",
            "registration_enabled",
            "email_verification_required",
            "search_cache_ttl",
            "trending_search_limit",
            "sensitive_words_enabled",
        ]
        
        if request.config_key not in allowed_keys:
            raise BusinessException(
                ErrorCode.ADMIN_4002,
                f"配置项 {request.config_key} 不在允许列表中。允许的配置项：{', '.join(allowed_keys)}"
            )
        
        config = self.get_system_config(request.config_key)
        
        if config:
            before_data = {"config_key": config.config_key, "config_value": config.config_value}
            config.config_value = request.config_value
            config.description = request.description or config.description
            config.updated_by = self.admin.id
            after_data = {"config_key": request.config_key, "config_value": request.config_value}
        else:
            before_data = {}
            config = SystemConfig(
                id=str(uuid.uuid4()),
                config_key=request.config_key,
                config_value=request.config_value,
                description=request.description,
                updated_by=self.admin.id
            )
            self.db.add(config)
            after_data = {"config_key": request.config_key, "config_value": request.config_value}
        
        self._create_audit_log(
            action="UPDATE_CONFIG",
            target_type="system_configs",
            target_id=config.id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(config)
        return config

    def list_feedbacks(
        self,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Feedback], int]:
        filters = []
        
        if status:
            filters.append(Feedback.status == status)
        
        count_query = select(func.count()).where(and_(*filters)) if filters else select(func.count()).select_from(Feedback)
        total = self.db.execute(count_query).scalar() or 0
        
        query = select(Feedback)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(Feedback.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        
        result = self.db.execute(query)
        feedbacks = result.scalars().all()
        
        return list(feedbacks), total

    def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        return self.db.get(Feedback, feedback_id)

    def reply_feedback(
        self,
        feedback_id: str,
        request: FeedbackReplyRequest,
        ip_address: Optional[str] = None
    ) -> Feedback:
        self.check_permission(["SUPER_ADMIN", "OPERATOR"])
        
        feedback = self.get_feedback(feedback_id)
        if not feedback:
            raise BusinessException(ErrorCode.ADMIN_4007, "反馈不存在")
        
        before_data = {"status": feedback.status.value, "reply": feedback.reply}
        feedback.reply = request.reply
        feedback.replied_by = self.admin.id
        feedback.status = FeedbackStatus.RESOLVED
        after_data = {"status": "RESOLVED", "reply": request.reply}
        
        self._create_audit_log(
            action="REPLY_FEEDBACK",
            target_type="feedbacks",
            target_id=feedback_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def list_asset_packages(self) -> List[AssetPackage]:
        query = select(AssetPackage).order_by(AssetPackage.price_beans)
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_asset_package(self, package_id: str) -> Optional[AssetPackage]:
        return self.db.get(AssetPackage, package_id)

    def update_asset_package(
        self,
        package_id: str,
        request: AssetPackageUpdateRequest,
        ip_address: Optional[str] = None
    ) -> AssetPackage:
        self.check_permission(["SUPER_ADMIN"])
        
        package = self.get_asset_package(package_id)
        if not package:
            raise BusinessException(ErrorCode.ADMIN_4009, "扩容包不存在")
        
        before_data = {
            "price_beans": package.price_beans,
            "discount_rate": package.discount_rate
        }
        
        if request.price_beans is not None:
            package.price_beans = request.price_beans
        if request.discount_rate is not None:
            package.discount_rate = request.discount_rate
        
        after_data = {
            "price_beans": package.price_beans,
            "discount_rate": package.discount_rate
        }
        
        self._create_audit_log(
            action="UPDATE_ASSET_PACKAGE",
            target_type="asset_packages",
            target_id=package_id,
            before_data=before_data,
            after_data=after_data,
            ip_address=ip_address
        )
        
        self.db.commit()
        self.db.refresh(package)
        return package

    def get_dashboard_stats(self) -> dict:
        total_users = self.db.execute(select(func.count()).select_from(User)).scalar() or 0
        active_users = self.db.execute(
            select(func.count()).where(User.status == "ACTIVE")
        ).scalar() or 0
        
        total_resources = self.db.execute(
            select(func.count()).where(Resource.is_deleted == False)
        ).scalar() or 0
        pending_resources = self.db.execute(
            select(func.count()).where(Resource.status == ResourceStatus.PENDING_REVIEW)
        ).scalar() or 0
        
        total_topics = self.db.execute(
            select(func.count()).where(Topic.is_deleted == False)
        ).scalar() or 0
        total_posts = self.db.execute(select(func.count()).select_from(Post)).scalar() or 0
        
        total_feedbacks = self.db.execute(select(func.count()).select_from(Feedback)).scalar() or 0
        pending_feedbacks = self.db.execute(
            select(func.count()).where(Feedback.status == FeedbackStatus.PENDING)
        ).scalar() or 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_resources": total_resources,
            "pending_resources": pending_resources,
            "total_topics": total_topics,
            "total_posts": total_posts,
            "total_revenue": 0,
            "total_feedbacks": total_feedbacks,
            "pending_feedbacks": pending_feedbacks,
        }
