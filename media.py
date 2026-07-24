"""Media Library — folders + assets. Local storage under /app/backend/uploads,
served via /api/media/file/{asset_id}. Ready to swap for Emergent Object Storage / Cloudinary."""
import os
import mimetypes
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import MediaAsset, MediaFolder, uid, now_iso

router = APIRouter(prefix="/api/media", tags=["media"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/folders")
async def list_folders(parent_id: Optional[str] = None, _u=Depends(require_admin())):
    db = get_db()
    q: dict = {"parent_id": parent_id}
    return await db.media_folders.find(q, {"_id": 0}).sort("created_at", -1).to_list(500)


@router.post("/folders")
async def create_folder(payload: MediaFolder, _u=Depends(require_admin())):
    db = get_db()
    await db.media_folders.insert_one(payload.model_dump())
    return payload.model_dump()


@router.delete("/folders/{fid}")
async def delete_folder(fid: str, _u=Depends(require_admin())):
    db = get_db()
    await db.media_folders.delete_one({"id": fid})
    await db.media_assets.update_many({"folder_id": fid}, {"$set": {"folder_id": None}})
    return {"ok": True}


@router.get("/assets")
async def list_assets(folder_id: Optional[str] = None, q: Optional[str] = None, limit: int = 100, skip: int = 0):
    db = get_db()
    query: dict = {}
    if folder_id:
        query["folder_id"] = folder_id
    if q:
        query["filename"] = {"$regex": q, "$options": "i"}
    total = await db.media_assets.count_documents(query)
    items = await db.media_assets.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"total": total, "items": items}


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    folder_id: Optional[str] = None,
    alt_text: Optional[str] = None,
    caption: Optional[str] = None,
    user=Depends(get_current_user),
):
    db = get_db()
    asset_id = uid()
    ext = Path(file.filename or "").suffix.lower()
    safe_name = f"{asset_id}{ext}"
    dest = UPLOAD_DIR / safe_name
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    size = dest.stat().st_size
    mime = file.content_type or mimetypes.guess_type(file.filename or "")[0] or "application/octet-stream"
    asset = MediaAsset(
        id=asset_id,
        filename=file.filename or safe_name,
        url=f"/api/media/file/{asset_id}",
        mime_type=mime,
        size_bytes=size,
        folder_id=folder_id,
        uploader_id=user.get("id"),
        alt_text=alt_text,
        caption=caption,
    )
    # store storage_key so we can find the file
    doc = asset.model_dump()
    doc["storage_key"] = safe_name
    await db.media_assets.insert_one(doc)
    return asset.model_dump()


@router.get("/file/{asset_id}")
async def serve_file(asset_id: str):
    db = get_db()
    asset = await db.media_assets.find_one({"id": asset_id}, {"_id": 0})
    if not asset:
        raise HTTPException(404, "Asset not found")
    path = UPLOAD_DIR / asset["storage_key"]
    if not path.exists():
        raise HTTPException(404, "File missing")
    return FileResponse(str(path), media_type=asset.get("mime_type"))


@router.put("/assets/{aid}")
async def update_asset(aid: str, alt_text: Optional[str] = None, caption: Optional[str] = None, _u=Depends(require_admin())):
    db = get_db()
    patch = {}
    if alt_text is not None:
        patch["alt_text"] = alt_text
    if caption is not None:
        patch["caption"] = caption
    if patch:
        await db.media_assets.update_one({"id": aid}, {"$set": patch})
    return {"ok": True}


@router.delete("/assets/{aid}")
async def delete_asset(aid: str, _u=Depends(require_admin())):
    db = get_db()
    asset = await db.media_assets.find_one({"id": aid}, {"_id": 0})
    if asset:
        p = UPLOAD_DIR / asset.get("storage_key", "")
        if p.exists():
            p.unlink()
        await db.media_assets.delete_one({"id": aid})
    return {"ok": True}
