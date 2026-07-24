"""Authentication routes: register, login, me, Google OAuth."""
from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db
from ..deps import get_current_user
from ..models import User, UserLogin, UserPublic, UserRegister, GoogleAuthPayload, now_iso
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(payload: UserRegister):
    db = get_db()
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    role = payload.role or "subscriber"
    if role in ("super_admin", "director"):
        # cannot self-register as elevated role
        role = "subscriber"
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=role,
        password_hash=hash_password(payload.password),
        provider="local",
    )
    await db.users.insert_one(user.model_dump())
    token = create_access_token({"sub": user.id, "role": user.role, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserPublic(**user.model_dump()).model_dump(),
    }


@router.post("/login")
async def login(payload: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": payload.email}, {"_id": 0})
    if not user or not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account disabled")
    token = create_access_token({"sub": user["id"], "role": user["role"], "email": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserPublic(**user).model_dump(),
    }


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return UserPublic(**user).model_dump()


@router.post("/google")
async def google_oauth(payload: GoogleAuthPayload):
    """Verify Google ID token and issue JWT.

    Requires a `google_oauth` integration setting with `client_id` populated.
    If not configured, returns HTTP 501 so the frontend can hide the button gracefully.
    """
    db = get_db()
    setting = await db.integration_settings.find_one({"provider": "google_oauth"}, {"_id": 0})
    if not setting or not setting.get("is_enabled") or not setting.get("config", {}).get("client_id"):
        raise HTTPException(status_code=501, detail="Google OAuth not configured. Enable it under Admin > Integrations.")

    try:
        from google.oauth2 import id_token as google_id_token  # type: ignore
        from google.auth.transport import requests as google_requests  # type: ignore
    except ImportError:
        raise HTTPException(status_code=501, detail="google-auth library not installed")

    try:
        idinfo = google_id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            setting["config"]["client_id"],
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {exc}")

    email = idinfo.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google token missing email")

    user_doc = await db.users.find_one({"email": email}, {"_id": 0})
    if not user_doc:
        user = User(
            email=email,
            full_name=idinfo.get("name", email.split("@")[0]),
            role="subscriber",
            provider="google",
            avatar_url=idinfo.get("picture"),
        )
        await db.users.insert_one(user.model_dump())
        user_doc = user.model_dump()
    else:
        await db.users.update_one({"id": user_doc["id"]}, {"$set": {"updated_at": now_iso()}})

    token = create_access_token({"sub": user_doc["id"], "role": user_doc["role"], "email": user_doc["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserPublic(**user_doc).model_dump(),
    }
