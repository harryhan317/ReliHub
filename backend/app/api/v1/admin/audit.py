"""
Admin API - Audit Logs
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models.administrators import AdminUser
from app.schemas.admin import AuditLogListResponse, AuditLogResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/audit-logs", tags=["Admin - Audit"])


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    admin_id: Optional[str] = Query(None, description="Filter by admin ID"),
    action: Optional[str] = Query(None, description="Filter by action type(s), comma-separated for multiple"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    List audit logs with pagination and filtering.

    - **admin_id**: Filter by admin who performed the action
    - **action**: Filter by action type (BAN_USER, APPROVE_RESOURCE, etc.), comma-separated for multiple
    """
    actions = None
    if action:
        actions = [a.strip() for a in action.split(',')]

    service = AdminService(db, admin)
    logs, total = service.list_audit_logs(
        admin_id=admin_id,
        actions=actions,
        page=page,
        page_size=page_size
    )

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(
    log_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin)
):
    """
    Get audit log details by ID.
    """
    service = AdminService(db, admin)
    log = service.get_audit_log(log_id)
    
    if not log:
        from app.core.exceptions import BusinessException, ErrorCode
        raise BusinessException(ErrorCode.ADMIN_4003, "审计日志不存在")
    
    return AuditLogResponse.model_validate(log)
