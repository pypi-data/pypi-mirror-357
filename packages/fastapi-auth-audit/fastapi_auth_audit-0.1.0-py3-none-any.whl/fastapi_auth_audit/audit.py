import logging
from fastapi import BackgroundTasks
from .database import SessionLocal
from .models import AuditLog

logger = logging.getLogger("fastapi_auth_audit.audit")

def write_audit_log(user_id, action, resource, status, detail):
    db = None
    try:
        db = SessionLocal()
        db.add(AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            status=status,
            detail=detail
        ))
        db.commit()
    except Exception as e:
        logger.error(f"audit write failed: {e!r}", exc_info=True)
        if db:
            db.rollback()
    finally:
        if db:
            db.close()

def audit_background(tasks: BackgroundTasks, *, user_id, action, resource, status, detail):
    try:
        tasks.add_task(
            write_audit_log,
            user_id, action, resource, status, detail
        )
    except Exception as e:
        logger.error(f"audit schedule failed: {e!r}", exc_info=True)
