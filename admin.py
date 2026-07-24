"""Homepage builder, Menus, Integration Settings, Site Settings, Enquiries, Analytics."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..database import get_db
from ..deps import require_admin, require_super_admin
from ..models import (
    HomepageSection, MenuItem, IntegrationSetting, SiteSettings, Enquiry,
    AnalyticsEvent, DEFAULT_ROLE_PERMISSIONS, ROLES, now_iso,
)

router = APIRouter(prefix="/api", tags=["admin"])


# ---------- Homepage Builder ----------
@router.get("/homepage/sections")
async def list_sections(active: Optional[bool] = None):
    db = get_db()
    q = {}
    if active is not None:
        q["is_active"] = active
    return await db.homepage_sections.find(q, {"_id": 0}).sort("order", 1).to_list(200)


@router.post("/homepage/sections")
async def create_section(payload: HomepageSection, _u=Depends(require_admin())):
    db = get_db()
    await db.homepage_sections.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/homepage/sections/{sid}")
async def update_section(sid: str, payload: HomepageSection, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = sid
    await db.homepage_sections.update_one({"id": sid}, {"$set": data})
    return data


@router.delete("/homepage/sections/{sid}")
async def delete_section(sid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.homepage_sections.delete_one({"id": sid})
    return {"ok": True}


class ReorderPayload(BaseModel):
    ids: List[str]


@router.post("/homepage/reorder")
async def reorder_sections(payload: ReorderPayload, _u=Depends(require_admin())):
    db = get_db()
    for idx, sid in enumerate(payload.ids):
        await db.homepage_sections.update_one({"id": sid}, {"$set": {"order": idx}})
    return {"ok": True}


# ---------- Menus ----------
@router.get("/menus")
async def list_menus(location: Optional[str] = None):
    db = get_db()
    q = {}
    if location:
        q["location"] = location
    return await db.menus.find(q, {"_id": 0}).sort("order", 1).to_list(500)


@router.post("/menus")
async def create_menu(payload: MenuItem, _u=Depends(require_admin())):
    db = get_db()
    await db.menus.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/menus/{mid}")
async def update_menu(mid: str, payload: MenuItem, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = mid
    await db.menus.update_one({"id": mid}, {"$set": data})
    return data


@router.delete("/menus/{mid}")
async def delete_menu(mid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.menus.delete_one({"id": mid})
    return {"ok": True}


# ---------- Integrations ----------
@router.get("/integrations")
async def list_integrations(_u=Depends(require_admin())):
    db = get_db()
    items = await db.integration_settings.find({}, {"_id": 0}).to_list(200)
    # Mask secrets except last 4 chars for display
    for it in items:
        cfg = it.get("config", {}) or {}
        masked = {}
        for k, v in cfg.items():
            if not v:
                masked[k] = ""
            elif "key" in k.lower() or "secret" in k.lower() or "token" in k.lower():
                masked[k] = ("•" * max(0, len(str(v)) - 4)) + str(v)[-4:]
            else:
                masked[k] = v
        it["config_masked"] = masked
    return items


@router.put("/integrations/{provider}")
async def update_integration(provider: str, payload: IntegrationSetting, _u=Depends(require_super_admin())):
    db = get_db()
    existing = await db.integration_settings.find_one({"provider": provider}, {"_id": 0})
    data = payload.model_dump()
    data["provider"] = provider
    data["updated_at"] = now_iso()
    if existing:
        await db.integration_settings.update_one({"provider": provider}, {"$set": data})
    else:
        await db.integration_settings.insert_one(dict(data))
    doc = await db.integration_settings.find_one({"provider": provider}, {"_id": 0})
    return doc


# ---------- Site Settings ----------
@router.get("/settings")
async def get_settings():
    db = get_db()
    doc = await db.site_settings.find_one({"id": "site_settings"}, {"_id": 0})
    if not doc:
        s = SiteSettings()
        await db.site_settings.insert_one(s.model_dump())
        return s.model_dump()
    return doc


@router.put("/settings")
async def update_settings(payload: SiteSettings, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = "site_settings"
    await db.site_settings.update_one({"id": "site_settings"}, {"$set": data}, upsert=True)
    return data


# ---------- Enquiries / Contact form ----------
@router.post("/enquiries")
async def create_enquiry(payload: Enquiry):
    db = get_db()
    await db.enquiries.insert_one(payload.model_dump())
    return {"ok": True, "id": payload.id}


@router.get("/enquiries")
async def list_enquiries(status: Optional[str] = None, kind: Optional[str] = None, _u=Depends(require_admin())):
    db = get_db()
    q = {}
    if status:
        q["status"] = status
    if kind:
        q["kind"] = kind
    return await db.enquiries.find(q, {"_id": 0}).sort("created_at", -1).to_list(1000)


@router.put("/enquiries/{eid}")
async def update_enquiry(eid: str, payload: Enquiry, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = eid
    await db.enquiries.update_one({"id": eid}, {"$set": data})
    return data


@router.delete("/enquiries/{eid}")
async def delete_enquiry(eid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.enquiries.delete_one({"id": eid})
    return {"ok": True}


# ---------- Roles ----------
@router.get("/roles")
async def list_roles(_u=Depends(require_admin())):
    db = get_db()
    override = await db.role_permissions.find_one({"id": "custom"}, {"_id": 0})
    permissions = override["permissions"] if override else DEFAULT_ROLE_PERMISSIONS
    return {"roles": ROLES, "permissions": permissions}


class PermsPayload(BaseModel):
    permissions: dict


@router.put("/roles/permissions")
async def update_role_permissions(payload: PermsPayload, _u=Depends(require_super_admin())):
    db = get_db()
    await db.role_permissions.update_one(
        {"id": "custom"},
        {"$set": {"id": "custom", "permissions": payload.permissions, "updated_at": now_iso()}},
        upsert=True,
    )
    return {"ok": True}


# ---------- Analytics ----------
class TrackPayload(BaseModel):
    kind: str
    entity_id: Optional[str] = None
    path: Optional[str] = None
    referrer: Optional[str] = None
    session_id: Optional[str] = None


@router.post("/analytics/track")
async def track_event(payload: TrackPayload):
    db = get_db()
    ev = AnalyticsEvent(**payload.model_dump())
    await db.analytics_events.insert_one(ev.model_dump())
    return {"ok": True}


@router.get("/analytics/summary")
async def analytics_summary(_u=Depends(require_admin())):
    db = get_db()
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    d7 = (now - timedelta(days=7)).isoformat()
    d30 = (now - timedelta(days=30)).isoformat()

    async def _count(coll, q=None):
        return await db[coll].count_documents(q or {})

    total_articles = await _count("articles", {"status": "published"})
    total_episodes = await _count("podcast_episodes", {"is_published": True})
    total_issues = await _count("magazine_issues", {"is_published": True})
    total_events = await _count("events")
    total_subs = await _count("subscribers", {"is_active": True})
    total_users = await _count("users")
    total_enquiries = await _count("enquiries", {"status": "new"})
    total_campaigns = await _count("ad_campaigns", {"status": {"$in": ["approved", "active"]}})

    page_views_7d = await db.analytics_events.count_documents({"kind": "page_view", "created_at": {"$gte": d7}})
    article_views_7d = await db.analytics_events.count_documents({"kind": "article_view", "created_at": {"$gte": d7}})
    page_views_30d = await db.analytics_events.count_documents({"kind": "page_view", "created_at": {"$gte": d30}})

    top_articles = await db.articles.find({"status": "published"}, {"_id": 0, "id": 1, "title": 1, "slug": 1, "views": 1}).sort("views", -1).limit(6).to_list(6)

    # daily buckets for last 14 days
    from collections import Counter
    events = await db.analytics_events.find(
        {"created_at": {"$gte": (now - timedelta(days=14)).isoformat()}},
        {"_id": 0, "kind": 1, "created_at": 1},
    ).to_list(20000)
    by_day = Counter()
    for e in events:
        day = str(e["created_at"])[:10]
        by_day[day] += 1
    daily = [{"date": day, "count": count} for day, count in sorted(by_day.items())]

    recent_enquiries = await db.enquiries.find({}, {"_id": 0}).sort("created_at", -1).limit(6).to_list(6)

    return {
        "kpis": {
            "articles": total_articles,
            "episodes": total_episodes,
            "issues": total_issues,
            "events": total_events,
            "subscribers": total_subs,
            "users": total_users,
            "new_enquiries": total_enquiries,
            "active_campaigns": total_campaigns,
            "page_views_7d": page_views_7d,
            "article_views_7d": article_views_7d,
            "page_views_30d": page_views_30d,
        },
        "top_articles": top_articles,
        "daily_events": daily,
        "recent_enquiries": recent_enquiries,
    }
