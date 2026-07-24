"""Advertisements marketplace + client portal."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import AdSlot, AdCampaign, Sponsor, now_iso

router = APIRouter(prefix="/api", tags=["ads"])


# ---------- Ad Slots (public catalog) ----------
@router.get("/ads/slots")
async def list_slots(active: Optional[bool] = True):
    db = get_db()
    q = {}
    if active is not None:
        q["is_active"] = active
    return await db.ad_slots.find(q, {"_id": 0}).to_list(500)


@router.post("/ads/slots")
async def create_slot(payload: AdSlot, _u=Depends(require_admin())):
    db = get_db()
    await db.ad_slots.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/ads/slots/{sid}")
async def update_slot(sid: str, payload: AdSlot, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = sid
    await db.ad_slots.update_one({"id": sid}, {"$set": data})
    return data


@router.delete("/ads/slots/{sid}")
async def delete_slot(sid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.ad_slots.delete_one({"id": sid})
    return {"ok": True}


# ---------- Active Ads served on website ----------
@router.get("/ads/active")
async def active_ads(location: Optional[str] = None):
    """Return active approved campaigns filtered by slot location for website injection."""
    db = get_db()
    slot_q = {"is_active": True}
    if location:
        slot_q["location"] = location
    slots = await db.ad_slots.find(slot_q, {"_id": 0}).to_list(200)
    slot_ids = [s["id"] for s in slots]
    campaigns = await db.ad_campaigns.find(
        {"status": {"$in": ["approved", "active"]}, "slot_id": {"$in": slot_ids}},
        {"_id": 0},
    ).to_list(500)
    slot_map = {s["id"]: s for s in slots}
    for c in campaigns:
        c["slot"] = slot_map.get(c.get("slot_id"))
    return campaigns


# ---------- Campaigns ----------
@router.get("/ads/campaigns")
async def list_campaigns(status: Optional[str] = None, _u=Depends(require_admin())):
    db = get_db()
    q = {}
    if status:
        q["status"] = status
    items = await db.ad_campaigns.find(q, {"_id": 0}).sort("created_at", -1).to_list(500)
    slot_map = {s["id"]: s for s in await db.ad_slots.find({}, {"_id": 0}).to_list(500)}
    client_map = {u["id"]: {"id": u["id"], "email": u["email"], "full_name": u.get("full_name"), "company": u.get("company")}
                  for u in await db.users.find({"role": "client"}, {"_id": 0}).to_list(1000)}
    for c in items:
        c["slot"] = slot_map.get(c.get("slot_id"))
        c["client"] = client_map.get(c.get("client_id"))
    return items


@router.get("/ads/my-campaigns")
async def my_campaigns(user=Depends(get_current_user)):
    db = get_db()
    items = await db.ad_campaigns.find({"client_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(500)
    slot_map = {s["id"]: s for s in await db.ad_slots.find({}, {"_id": 0}).to_list(500)}
    for c in items:
        c["slot"] = slot_map.get(c.get("slot_id"))
    return items


@router.post("/ads/campaigns")
async def create_campaign(payload: AdCampaign, user=Depends(get_current_user)):
    db = get_db()
    # if client role, force client_id to self
    if user["role"] == "client":
        payload.client_id = user["id"]
        payload.status = "pending"
    slot = await db.ad_slots.find_one({"id": payload.slot_id}, {"_id": 0})
    if not slot:
        raise HTTPException(404, "Slot not found")
    await db.ad_campaigns.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/ads/campaigns/{cid}")
async def update_campaign(cid: str, payload: AdCampaign, user=Depends(get_current_user)):
    db = get_db()
    existing = await db.ad_campaigns.find_one({"id": cid}, {"_id": 0})
    if not existing:
        raise HTTPException(404, "Campaign not found")
    # clients can only edit own & cannot change status
    if user["role"] == "client":
        if existing["client_id"] != user["id"]:
            raise HTTPException(403, "Not your campaign")
        payload.status = existing["status"]
        payload.client_id = user["id"]
    data = payload.model_dump()
    data["id"] = cid
    await db.ad_campaigns.update_one({"id": cid}, {"$set": data})
    return data


@router.delete("/ads/campaigns/{cid}")
async def delete_campaign(cid: str, user=Depends(get_current_user)):
    db = get_db()
    existing = await db.ad_campaigns.find_one({"id": cid}, {"_id": 0})
    if not existing:
        return {"ok": True}
    if user["role"] == "client" and existing["client_id"] != user["id"]:
        raise HTTPException(403, "Not your campaign")
    await db.ad_campaigns.delete_one({"id": cid})
    return {"ok": True}


# ---------- Sponsors ----------
@router.get("/sponsors")
async def list_sponsors(active: Optional[bool] = True):
    db = get_db()
    q = {}
    if active is not None:
        q["is_active"] = active
    return await db.sponsors.find(q, {"_id": 0}).sort("order", 1).to_list(500)


@router.post("/sponsors")
async def create_sponsor(payload: Sponsor, _u=Depends(require_admin())):
    db = get_db()
    await db.sponsors.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/sponsors/{sid}")
async def update_sponsor(sid: str, payload: Sponsor, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = sid
    await db.sponsors.update_one({"id": sid}, {"$set": data})
    return data


@router.delete("/sponsors/{sid}")
async def delete_sponsor(sid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.sponsors.delete_one({"id": sid})
    return {"ok": True}
