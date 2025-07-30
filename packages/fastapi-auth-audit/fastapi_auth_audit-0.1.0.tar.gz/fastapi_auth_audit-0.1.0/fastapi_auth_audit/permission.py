import logging
from fastapi import Request, Depends, BackgroundTasks, HTTPException, status
from typing import Callable
from pydantic import BaseModel
from .audit import audit_background

logger = logging.getLogger("fastapi_auth_audit.permission")

class User(BaseModel):
    id: int
    username: str

def get_current_user() -> User:
    return User(id=1, username="alice")

async def check_permission(user: User, action: str, resource: str) -> bool:
    if action == "delete_user" and user.id != 1:
        return False
    return True

def PermissionDependency(action: str, resource_getter: Callable[[Request], str],current_user_dep: Callable = get_current_user):
    async def dep(
        request: Request,
        tasks: BackgroundTasks,
        user: User = Depends(current_user_dep)
    ):
        try:
            resource = resource_getter(request)
        except Exception as e:
            logger.error(f"resource_getter error: {e!r}", exc_info=True)
            resource = "unknown"
        try:
            allowed = await check_permission(user, action, resource)
        except Exception as e:
            logger.error(f"permission check error: {e!r}", exc_info=True)
            allowed = False

        detail = {
            "path": request.url.path,
            "method": request.method,
            "params": dict(request.path_params),
            "query": dict(request.query_params),
        }
        audit_background(
            tasks,
            user_id=user.id,
            action=action,
            resource=resource,
            status="allow" if allowed else "deny",
            detail=detail
        )

        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return True
    return dep
