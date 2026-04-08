"""
Central API router – mounts all v1 sub-routers.
"""
from fastapi import APIRouter

from app.api.v1.ai.router import router as ai_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.community.router import router as community_router
from app.api.v1.files.router import router as files_router
from app.api.v1.ledger.router import router as ledger_router
from app.api.v1.notification.router import router as notification_router
from app.api.v1.payment.router import router as payment_router
from app.api.v1.resources.router import router as resources_router
from app.api.v1.users.router import router as users_router

from app.api.v1.admin.audit import router as admin_audit_router
from app.api.v1.admin.config import router as admin_config_router
from app.api.v1.admin.content import router as admin_content_router
from app.api.v1.admin.dashboard import router as admin_dashboard_router
from app.api.v1.admin.feedback import router as admin_feedback_router
from app.api.v1.admin.llm_provider import router as admin_llm_provider_router
from app.api.v1.admin.packages import router as admin_packages_router
from app.api.v1.admin.users import router as admin_users_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["认证鉴权"])
api_router.include_router(users_router, prefix="/users", tags=["用户模块"])
api_router.include_router(resources_router, prefix="/resources", tags=["资源模块"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI助手"])
api_router.include_router(community_router, prefix="/community", tags=["社区模块"])
api_router.include_router(files_router, prefix="/files", tags=["文件模块"])
api_router.include_router(ledger_router, prefix="/ledger", tags=["账本模块"])
api_router.include_router(notification_router, prefix="/notifications", tags=["通知模块"])
api_router.include_router(payment_router, tags=["支付模块"])

api_router.include_router(admin_users_router, prefix="/admin/users", tags=["管理后台-用户管理"])
api_router.include_router(admin_content_router, prefix="/admin", tags=["管理后台-内容审核"])
api_router.include_router(admin_audit_router, prefix="/admin", tags=["管理后台-审计日志"])
api_router.include_router(admin_config_router, prefix="/admin", tags=["管理后台-系统配置"])
api_router.include_router(admin_feedback_router, prefix="/admin", tags=["管理后台-反馈处理"])
api_router.include_router(admin_packages_router, prefix="/admin", tags=["管理后台-扩容包管理"])
api_router.include_router(admin_dashboard_router, prefix="/admin", tags=["管理后台-仪表盘"])
api_router.include_router(admin_llm_provider_router, prefix="/admin", tags=["管理后台-LLM配置"])
