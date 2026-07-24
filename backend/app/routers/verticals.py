"""Magazine issues, Podcast episodes, Awards, Events."""
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from ..database import get_db
from ..deps import require_admin, get_optional_user
from ..models import (
    MagazineIssue, PodcastEpisode, AwardCategory, AwardWinner, AwardNomination,
    Event, EventRSVP, now_iso,
)

router = APIRouter(prefix="/api", tags=["verticals"])


def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s.strip("-")


# =========== Magazine ===========
@router.get("/magazine/issues")
async def list_issues(published: Optional[bool] = True, limit: int = 50):
    db = get_db()
    q = {}
    if published is not None:
        q["is_published"] = published
    items = await db.magazine_issues.find(q, {"_id": 0}).sort("published_at", -1).limit(limit).to_list(limit)
    return items


@router.get("/magazine/current")
async def current_issue():
    db = get_db()
    it = await db.magazine_issues.find_one({"is_current": True, "is_published": True}, {"_id": 0})
    if not it:
        it = await db.magazine_issues.find_one({"is_published": True}, {"_id": 0}, sort=[("published_at", -1)])
    return it


@router.get("/magazine/issues/{ident}")
async def get_issue(ident: str):
    db = get_db()
    it = await db.magazine_issues.find_one({"$or": [{"id": ident}, {"slug": ident}]}, {"_id": 0})
    if not it:
        raise HTTPException(404, "Issue not found")
    return it


@router.post("/magazine/issues")
async def create_issue(payload: MagazineIssue, _u=Depends(require_admin())):
    db = get_db()
    payload.slug = payload.slug or _slugify(payload.title)
    if payload.is_current:
        await db.magazine_issues.update_many({}, {"$set": {"is_current": False}})
    await db.magazine_issues.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/magazine/issues/{iid}")
async def update_issue(iid: str, payload: MagazineIssue, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = iid
    if data.get("is_current"):
        await db.magazine_issues.update_many({"id": {"$ne": iid}}, {"$set": {"is_current": False}})
    await db.magazine_issues.update_one({"id": iid}, {"$set": data})
    return data


@router.delete("/magazine/issues/{iid}")
async def delete_issue(iid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.magazine_issues.delete_one({"id": iid})
    return {"ok": True}


# =========== Podcast ===========
@router.get("/podcast/episodes")
async def list_episodes(published: Optional[bool] = True, limit: int = 50):
    db = get_db()
    q = {}
    if published is not None:
        q["is_published"] = published
    items = await db.podcast_episodes.find(q, {"_id": 0}).sort("published_at", -1).limit(limit).to_list(limit)
    return items


@router.get("/podcast/episodes/{ident}")
async def get_episode(ident: str):
    db = get_db()
    ep = await db.podcast_episodes.find_one({"$or": [{"id": ident}, {"slug": ident}]}, {"_id": 0})
    if not ep:
        raise HTTPException(404, "Episode not found")
    return ep


@router.post("/podcast/episodes")
async def create_episode(payload: PodcastEpisode, _u=Depends(require_admin())):
    db = get_db()
    payload.slug = payload.slug or _slugify(payload.title)
    if await db.podcast_episodes.find_one({"slug": payload.slug}):
        raise HTTPException(400, "Slug already exists")
    await db.podcast_episodes.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/podcast/episodes/{eid}")
async def update_episode(eid: str, payload: PodcastEpisode, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = eid
    await db.podcast_episodes.update_one({"id": eid}, {"$set": data})
    return data


@router.delete("/podcast/episodes/{eid}")
async def delete_episode(eid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.podcast_episodes.delete_one({"id": eid})
    return {"ok": True}


# =========== Awards ===========
@router.get("/awards/categories")
async def list_award_categories(year: Optional[int] = None):
    db = get_db()
    q = {}
    if year:
        q["year"] = year
    return await db.award_categories.find(q, {"_id": 0}).to_list(200)


@router.post("/awards/categories")
async def create_award_category(payload: AwardCategory, _u=Depends(require_admin())):
    db = get_db()
    payload.slug = payload.slug or _slugify(payload.name)
    await db.award_categories.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/awards/categories/{cid}")
async def update_award_category(cid: str, payload: AwardCategory, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = cid
    await db.award_categories.update_one({"id": cid}, {"$set": data})
    return data


@router.delete("/awards/categories/{cid}")
async def delete_award_category(cid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.award_categories.delete_one({"id": cid})
    return {"ok": True}


@router.get("/awards/winners")
async def list_winners(year: Optional[int] = None, category_id: Optional[str] = None):
    db = get_db()
    q = {}
    if year:
        q["year"] = year
    if category_id:
        q["category_id"] = category_id
    items = await db.award_winners.find(q, {"_id": 0}).to_list(500)
    cat_map = {c["id"]: c for c in await db.award_categories.find({}, {"_id": 0}).to_list(500)}
    for it in items:
        it["category"] = cat_map.get(it.get("category_id"))
    return items


@router.post("/awards/winners")
async def create_winner(payload: AwardWinner, _u=Depends(require_admin())):
    db = get_db()
    await db.award_winners.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/awards/winners/{wid}")
async def update_winner(wid: str, payload: AwardWinner, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = wid
    await db.award_winners.update_one({"id": wid}, {"$set": data})
    return data


@router.delete("/awards/winners/{wid}")
async def delete_winner(wid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.award_winners.delete_one({"id": wid})
    return {"ok": True}


@router.post("/awards/nominations")
async def create_nomination(payload: AwardNomination):
    db = get_db()
    await db.award_nominations.insert_one(payload.model_dump())
    return {"ok": True, "id": payload.id}


@router.get("/awards/nominations")
async def list_nominations(year: Optional[int] = None, status: Optional[str] = None, _u=Depends(require_admin())):
    db = get_db()
    q = {}
    if year:
        q["year"] = year
    if status:
        q["status"] = status
    return await db.award_nominations.find(q, {"_id": 0}).sort("created_at", -1).to_list(1000)


@router.put("/awards/nominations/{nid}")
async def update_nomination(nid: str, payload: AwardNomination, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = nid
    await db.award_nominations.update_one({"id": nid}, {"$set": data})
    return data


# =========== Events ===========
@router.get("/events")
async def list_events(status: Optional[str] = None, featured: Optional[bool] = None, limit: int = 50):
    db = get_db()
    q = {}
    if status:
        q["status"] = status
    if featured is not None:
        q["is_featured"] = featured
    return await db.events.find(q, {"_id": 0}).sort("start_at", -1).limit(limit).to_list(limit)


@router.get("/events/{ident}")
async def get_event(ident: str):
    db = get_db()
    ev = await db.events.find_one({"$or": [{"id": ident}, {"slug": ident}]}, {"_id": 0})
    if not ev:
        raise HTTPException(404, "Event not found")
    return ev


@router.post("/events")
async def create_event(payload: Event, _u=Depends(require_admin())):
    db = get_db()
    payload.slug = payload.slug or _slugify(payload.title)
    await db.events.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/events/{eid}")
async def update_event(eid: str, payload: Event, _u=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = eid
    await db.events.update_one({"id": eid}, {"$set": data})
    return data


@router.delete("/events/{eid}")
async def delete_event(eid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.events.delete_one({"id": eid})
    return {"ok": True}


@router.post("/events/{eid}/rsvp")
async def rsvp_event(eid: str, payload: EventRSVP):
    db = get_db()
    ev = await db.events.find_one({"id": eid}, {"_id": 0})
    if not ev:
        raise HTTPException(404, "Event not found")
    payload.event_id = eid
    await db.event_rsvps.insert_one(payload.model_dump())
    return {"ok": True, "id": payload.id}


@router.get("/events/{eid}/rsvps")
async def list_rsvps(eid: str, _u=Depends(require_admin())):
    db = get_db()
    return await db.event_rsvps.find({"event_id": eid}, {"_id": 0}).sort("created_at", -1).to_list(1000)
