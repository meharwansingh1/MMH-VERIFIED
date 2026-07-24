"""Articles, Categories, Authors."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..database import get_db
from ..deps import get_current_user, get_optional_user, require_admin
from ..models import Article, Author, Category, SeoMeta, now_iso

router = APIRouter(prefix="/api", tags=["content"])


def _slugify(s: str) -> str:
    import re
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s.strip("-")


# ---------- Categories ----------
@router.get("/categories")
async def list_categories():
    db = get_db()
    items = await db.categories.find({}, {"_id": 0}).sort("order", 1).to_list(500)
    return items


@router.post("/categories")
async def create_category(payload: Category, _user=Depends(require_admin())):
    db = get_db()
    payload.slug = payload.slug or _slugify(payload.name)
    if await db.categories.find_one({"slug": payload.slug}):
        raise HTTPException(400, "Slug already exists")
    await db.categories.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/categories/{cid}")
async def update_category(cid: str, payload: Category, _user=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = cid
    await db.categories.update_one({"id": cid}, {"$set": data}, upsert=False)
    return data


@router.delete("/categories/{cid}")
async def delete_category(cid: str, _user=Depends(require_admin())):
    db = get_db()
    await db.categories.delete_one({"id": cid})
    return {"ok": True}


# ---------- Authors ----------
@router.get("/authors")
async def list_authors():
    db = get_db()
    return await db.authors.find({}, {"_id": 0}).to_list(500)


@router.get("/authors/{aid}")
async def get_author(aid: str):
    db = get_db()
    a = await db.authors.find_one({"$or": [{"id": aid}, {"slug": aid}]}, {"_id": 0})
    if not a:
        raise HTTPException(404, "Author not found")
    return a


@router.post("/authors")
async def create_author(payload: Author, _user=Depends(require_admin())):
    db = get_db()
    payload.slug = payload.slug or _slugify(payload.name)
    if await db.authors.find_one({"slug": payload.slug}):
        raise HTTPException(400, "Slug already exists")
    await db.authors.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/authors/{aid}")
async def update_author(aid: str, payload: Author, _user=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = aid
    await db.authors.update_one({"id": aid}, {"$set": data})
    return data


@router.delete("/authors/{aid}")
async def delete_author(aid: str, _user=Depends(require_admin())):
    db = get_db()
    await db.authors.delete_one({"id": aid})
    return {"ok": True}


# ---------- Articles ----------
class ArticleQuery(BaseModel):
    status: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    tag: Optional[str] = None
    q: Optional[str] = None
    featured: Optional[bool] = None
    hero: Optional[bool] = None
    limit: int = 20
    skip: int = 0


@router.get("/articles")
async def list_articles(
    status: Optional[str] = "published",
    category: Optional[str] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    featured: Optional[bool] = None,
    hero: Optional[bool] = None,
    limit: int = Query(20, le=100),
    skip: int = 0,
):
    db = get_db()
    query: dict = {}
    if status and status != "all":
        query["status"] = status
    if category:
        cat = await db.categories.find_one({"$or": [{"id": category}, {"slug": category}]}, {"_id": 0})
        if cat:
            query["category_id"] = cat["id"]
    if author:
        au = await db.authors.find_one({"$or": [{"id": author}, {"slug": author}]}, {"_id": 0})
        if au:
            query["author_id"] = au["id"]
    if tag:
        query["tags"] = tag
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"excerpt": {"$regex": q, "$options": "i"}},
        ]
    if featured is not None:
        query["is_featured"] = featured
    if hero is not None:
        query["is_hero"] = hero

    total = await db.articles.count_documents(query)
    items = (
        await db.articles.find(query, {"_id": 0})
        .sort("published_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list(limit)
    )
    # attach author + category
    author_map = {a["id"]: a for a in await db.authors.find({}, {"_id": 0}).to_list(500)}
    cat_map = {c["id"]: c for c in await db.categories.find({}, {"_id": 0}).to_list(500)}
    for it in items:
        it["author"] = author_map.get(it.get("author_id"))
        it["category"] = cat_map.get(it.get("category_id"))
    return {"items": items, "total": total, "limit": limit, "skip": skip}


@router.get("/articles/{ident}")
async def get_article(ident: str, user=Depends(get_optional_user)):
    db = get_db()
    art = await db.articles.find_one({"$or": [{"id": ident}, {"slug": ident}]}, {"_id": 0})
    if not art:
        raise HTTPException(404, "Article not found")
    # Only expose non-published to staff
    if art.get("status") != "published":
        if not user or user.get("role") in ("subscriber", "guest", "client"):
            raise HTTPException(404, "Article not found")
    # increment views (fire and forget)
    await db.articles.update_one({"id": art["id"]}, {"$inc": {"views": 1}})
    art["author"] = await db.authors.find_one({"id": art.get("author_id")}, {"_id": 0})
    art["category"] = await db.categories.find_one({"id": art.get("category_id")}, {"_id": 0})
    # related
    related_q = {"status": "published", "id": {"$ne": art["id"]}}
    if art.get("category_id"):
        related_q["category_id"] = art["category_id"]
    related = await db.articles.find(related_q, {"_id": 0, "body": 0}).sort("published_at", -1).limit(4).to_list(4)
    art["related"] = related
    return art


@router.post("/articles")
async def create_article(payload: Article, user=Depends(require_admin())):
    db = get_db()
    payload.slug = payload.slug or _slugify(payload.title)
    if await db.articles.find_one({"slug": payload.slug}):
        raise HTTPException(400, "Slug already exists")
    if payload.status == "published" and not payload.published_at:
        payload.published_at = now_iso()
    await db.articles.insert_one(payload.model_dump())
    return payload.model_dump()


@router.put("/articles/{aid}")
async def update_article(aid: str, payload: Article, user=Depends(require_admin())):
    db = get_db()
    data = payload.model_dump()
    data["id"] = aid
    data["updated_at"] = now_iso()
    if data.get("status") == "published" and not data.get("published_at"):
        data["published_at"] = now_iso()
    await db.articles.update_one({"id": aid}, {"$set": data})
    return data


@router.delete("/articles/{aid}")
async def delete_article(aid: str, user=Depends(require_admin())):
    db = get_db()
    await db.articles.delete_one({"id": aid})
    return {"ok": True}
