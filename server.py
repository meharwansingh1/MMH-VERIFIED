"""Musafir Media Publications — FastAPI entrypoint.

All routes are mounted under /api. See app/routers/*.py for the individual modules.
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

from app.database import get_db, close_client  # noqa: E402
from app.seed import seed_all  # noqa: E402
from app.routers.auth import router as auth_router  # noqa: E402
from app.routers.users import router as users_router  # noqa: E402
from app.routers.content import router as content_router  # noqa: E402
from app.routers.verticals import router as verticals_router  # noqa: E402
from app.routers.ads import router as ads_router  # noqa: E402
from app.routers.newsletter import router as newsletter_router  # noqa: E402
from app.routers.media import router as media_router  # noqa: E402
from app.routers.admin import router as admin_router  # noqa: E402
from app.routers.ai import router as ai_router  # noqa: E402


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("musafir")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm DB and seed initial data
    try:
        db = get_db()
        # index hints (not strict)
        await db.users.create_index("email", unique=True)
        await db.articles.create_index("slug", unique=True)
        await db.categories.create_index("slug", unique=True)
        await db.authors.create_index("slug", unique=True)
        await db.magazine_issues.create_index("slug", unique=True)
        await db.podcast_episodes.create_index("slug", unique=True)
        await db.events.create_index("slug", unique=True)
        await db.subscribers.create_index("email", unique=True)
        await db.integration_settings.create_index("provider", unique=True)
        await seed_all()
        logger.info("Musafir Media Publications API ready.")
    except Exception as exc:
        logger.exception("Startup error: %s", exc)
    yield
    await close_client()


app = FastAPI(title="Musafir Media Publications API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/")
async def root():
    return {"message": "Musafir Media Publications API", "status": "ok"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Include all routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(content_router)
app.include_router(verticals_router)
app.include_router(ads_router)
app.include_router(newsletter_router)
app.include_router(media_router)
app.include_router(admin_router)
app.include_router(ai_router)
