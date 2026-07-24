"""FastAPI dependencies: auth extraction, RBAC."""
from fastapi import Depends, Header, HTTPException, status
from typing import Optional, List

from .database import get_db
from .security import decode_token
from .models import DEFAULT_ROLE_PERMISSIONS


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    db = get_db()
    user = await db.users.find_one({"id": payload.get("sub")}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    return user


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    if not authorization:
        return None
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None


def _has_perm(role: str, needed: str, custom_perms: Optional[dict] = None) -> bool:
    perms = (custom_perms or DEFAULT_ROLE_PERMISSIONS).get(role, [])
    if "*" in perms:
        return True
    if needed in perms:
        return True
    # Support wildcard entries like "article:*"
    prefix = needed.split(":", 1)[0]
    if f"{prefix}:*" in perms:
        return True
    return False


def require_roles(*allowed_roles: str):
    async def dep(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in allowed_roles and user["role"] not in ("super_admin", "director"):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dep


def require_admin():
    """Any staff-level role (not subscriber/guest/client)."""
    staff_roles = {
        "super_admin", "director", "editor_in_chief", "editor", "journalist", "author",
        "podcast_manager", "awards_manager", "advertisement_manager", "sales_manager",
        "finance", "customer_support",
    }
    async def dep(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in staff_roles:
            raise HTTPException(status_code=403, detail="Admin access required")
        return user
    return dep


def require_super_admin():
    async def dep(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in ("super_admin", "director"):
            raise HTTPException(status_code=403, detail="Super admin required")
        return user
    return dep
