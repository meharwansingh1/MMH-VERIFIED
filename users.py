"""User management (admin)."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..deps import require_admin, require_super_admin, get_current_user
from ..models import User, UserPublic, ROLES, now_iso
from ..security import hash_password

router = APIRouter(prefix="/api/users", tags=["users"])


class UserCreatePayload(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "editor"
    company: Optional[str] = None
    phone: Optional[str] = None


class UserUpdatePayload(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("")
async def list_users(role: Optional[str] = None, q: Optional[str] = None, _u=Depends(require_admin())):
    db = get_db()
    query: dict = {}
    if role:
        query["role"] = role
    if q:
        query["$or"] = [
            {"email": {"$regex": q, "$options": "i"}},
            {"full_name": {"$regex": q, "$options": "i"}},
        ]
    items = await db.users.find(query, {"_id": 0, "password_hash": 0}).sort("created_at", -1).limit(500).to_list(500)
    return items


@router.post("")
async def create_user(payload: UserCreatePayload, _u=Depends(require_super_admin())):
    db = get_db()
    if payload.role not in ROLES:
        raise HTTPException(400, "Invalid role")
    if await db.users.find_one({"email": payload.email}):
        raise HTTPException(400, "Email already exists")
    u = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        password_hash=hash_password(payload.password),
        company=payload.company,
        phone=payload.phone,
    )
    await db.users.insert_one(u.model_dump())
    return UserPublic(**u.model_dump()).model_dump()


@router.put("/{uid}")
async def update_user(uid: str, payload: UserUpdatePayload, _u=Depends(require_super_admin())):
    db = get_db()
    patch = {k: v for k, v in payload.model_dump().items() if v is not None}
    if "role" in patch and patch["role"] not in ROLES:
        raise HTTPException(400, "Invalid role")
    patch["updated_at"] = now_iso()
    await db.users.update_one({"id": uid}, {"$set": patch})
    return {"ok": True}


@router.delete("/{uid}")
async def delete_user(uid: str, current=Depends(require_super_admin())):
    if current["id"] == uid:
        raise HTTPException(400, "Cannot delete self")
    db = get_db()
    await db.users.delete_one({"id": uid})
    return {"ok": True}


@router.put("/me/profile")
async def update_own_profile(payload: UserUpdatePayload, user=Depends(get_current_user)):
    db = get_db()
    patch = {k: v for k, v in payload.model_dump().items() if v is not None and k not in ("role", "is_active")}
    patch["updated_at"] = now_iso()
    await db.users.update_one({"id": user["id"]}, {"$set": patch})
    doc = await db.users.find_one({"id": user["id"]}, {"_id": 0, "password_hash": 0})
    return UserPublic(**doc).model_dump()
