"""Newsletter issues + subscribers."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from ..database import get_db
from ..deps import require_admin
from ..models import NewsletterIssue, Subscriber, now_iso

router = APIRouter(prefix="/api/newsletter", tags=["newsletter"])


class SubscribePayload(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    source: str = "website"


@router.post("/subscribe")
async def subscribe(payload: SubscribePayload):
    db = get_db()
    existing = await db.subscribers.find_one({"email": payload.email}, {"_id": 0})
    if existing:
        if not existing.get("is_active", True):
            await db.subscribers.update_one({"id": existing["id"]}, {"$set": {"is_active": True}})
        return {"ok": True, "already_subscribed": True}
    sub = Subscriber(email=payload.email, name=payload.name, source=payload.source)
    await db.subscribers.insert_one(sub.model_dump())
    return {"ok": True}


@router.get("/subscribers")
async def list_subscribers(active: Optional[bool] = None, _u=Depends(require_admin())):
    db = get_db()
    q = {}
    if active is not None:
        q["is_active"] = active
    total = await db.subscribers.count_documents(q)
    items = await db.subscribers.find(q, {"_id": 0}).sort("created_at", -1).limit(500).to_list(500)
    return {"total": total, "items": items}


@router.delete("/subscribers/{sid}")
async def delete_subscriber(sid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.subscribers.delete_one({"id": sid})
    return {"ok": True}


@router.get("/issues")
async def list_issues(_u=Depends(require_admin())):
    db = get_db()
    return await db.newsletter_issues.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)


@router.post("/issues")
async def create_issue(payload: NewsletterIssue, _u=Depends(require_admin())):
    db = get_db()
    await db.newsletter_issues.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/issues/{iid}")
async def update_issue(iid: str, payload: NewsletterIssue, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = iid
    await db.newsletter_issues.update_one({"id": iid}, {"$set": data})
    return data


@router.delete("/issues/{iid}")
async def delete_issue(iid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.newsletter_issues.delete_one({"id": iid})
    return {"ok": True}


@router.post("/issues/{iid}/send")
async def send_issue(iid: str, _u=Depends(require_admin())):
    """Mark as sent. Actual delivery goes through Resend/SendGrid once configured in Integrations."""
    db = get_db()
    subs = await db.subscribers.count_documents({"is_active": True})
    await db.newsletter_issues.update_one(
        {"id": iid},
        {"$set": {"status": "sent", "sent_at": now_iso(), "recipients_count": subs}},
    )
    # If Resend/SendGrid is enabled, we would enqueue actual delivery here.
    return {"ok": True, "queued": subs}
