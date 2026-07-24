"""Pydantic models for all Musafir Media Publications collections."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


def uid() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------- RBAC ----------
ROLES = [
    "super_admin",
    "director",
    "editor_in_chief",
    "editor",
    "journalist",
    "author",
    "podcast_manager",
    "awards_manager",
    "advertisement_manager",
    "sales_manager",
    "finance",
    "customer_support",
    "client",
    "subscriber",
    "guest",
]

# Default permission matrix — editable via /api/roles
DEFAULT_ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "super_admin": ["*"],
    "director": ["*"],
    "editor_in_chief": [
        "article:*", "category:*", "author:*", "magazine:*",
        "homepage:*", "media:*", "newsletter:*", "seo:*", "analytics:read",
    ],
    "editor": ["article:*", "category:read", "author:read", "media:*", "seo:*"],
    "journalist": ["article:create", "article:update:own", "article:read", "media:upload"],
    "author": ["article:create", "article:update:own", "article:read", "media:upload"],
    "podcast_manager": ["podcast:*", "media:*"],
    "awards_manager": ["award:*", "media:*"],
    "advertisement_manager": ["ad:*", "sponsor:*", "media:*"],
    "sales_manager": ["ad:read", "client:*", "enquiry:*", "analytics:read"],
    "finance": ["ad:read", "client:read", "invoice:*", "analytics:read"],
    "customer_support": ["enquiry:*", "subscriber:*", "user:read"],
    "client": ["client:self", "campaign:self", "ad:self"],
    "subscriber": ["profile:self"],
    "guest": [],
}


# ---------- Base ----------
class TSModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


# ---------- Users ----------
class User(TSModel):
    id: str = Field(default_factory=uid)
    email: EmailStr
    password_hash: Optional[str] = None
    full_name: str
    role: str = "subscriber"
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    provider: str = "local"  # local | google
    is_active: bool = True
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)


class UserPublic(TSModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None


class UserRegister(TSModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    role: Optional[str] = "subscriber"


class UserLogin(TSModel):
    email: EmailStr
    password: str


class GoogleAuthPayload(TSModel):
    id_token: str


# ---------- Content ----------
class Category(TSModel):
    id: str = Field(default_factory=uid)
    name: str
    slug: str
    description: Optional[str] = None
    order: int = 0
    created_at: str = Field(default_factory=now_iso)


class Author(TSModel):
    id: str = Field(default_factory=uid)
    name: str
    slug: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    designation: Optional[str] = None
    social: Dict[str, str] = Field(default_factory=dict)  # {twitter, instagram, linkedin}
    created_at: str = Field(default_factory=now_iso)


class SeoMeta(TSModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    canonical: Optional[str] = None
    og_image: Optional[str] = None
    twitter_card: str = "summary_large_image"
    schema_extras: Dict[str, Any] = Field(default_factory=dict)


class Article(TSModel):
    id: str = Field(default_factory=uid)
    title: str
    slug: str
    subtitle: Optional[str] = None
    excerpt: Optional[str] = None
    body: str = ""  # rich HTML
    cover_image: Optional[str] = None
    gallery: List[str] = Field(default_factory=list)
    category_id: Optional[str] = None
    author_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    status: str = "draft"  # draft | scheduled | published | archived
    is_featured: bool = False
    is_hero: bool = False
    reading_time_min: int = 5
    published_at: Optional[str] = None
    scheduled_at: Optional[str] = None
    views: int = 0
    seo: SeoMeta = Field(default_factory=SeoMeta)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)


# ---------- Magazine ----------
class MagazineIssue(TSModel):
    id: str = Field(default_factory=uid)
    title: str
    slug: str
    issue_number: str  # e.g., "Vol 6, Issue 2"
    month: str  # e.g., "January 2026"
    cover_image: Optional[str] = None
    pdf_url: Optional[str] = None
    description: Optional[str] = None
    is_current: bool = False
    is_published: bool = True
    published_at: str = Field(default_factory=now_iso)
    seo: SeoMeta = Field(default_factory=SeoMeta)


# ---------- Podcast ----------
class PodcastEpisode(TSModel):
    id: str = Field(default_factory=uid)
    title: str
    slug: str
    episode_number: int = 1
    season: int = 1
    description: str = ""
    show_notes: Optional[str] = None
    cover_image: Optional[str] = None
    audio_url: Optional[str] = None
    youtube_url: Optional[str] = None
    spotify_url: Optional[str] = None
    apple_url: Optional[str] = None
    duration_seconds: int = 0
    guest_name: Optional[str] = None
    guest_bio: Optional[str] = None
    guest_avatar: Optional[str] = None
    is_published: bool = True
    published_at: str = Field(default_factory=now_iso)
    seo: SeoMeta = Field(default_factory=SeoMeta)


# ---------- Awards ----------
class AwardCategory(TSModel):
    id: str = Field(default_factory=uid)
    name: str
    slug: str
    description: Optional[str] = None
    year: int = 2026
    edition: str = "IMAA 2026"
    icon: Optional[str] = None


class AwardWinner(TSModel):
    id: str = Field(default_factory=uid)
    category_id: str
    year: int
    name: str
    designation: Optional[str] = None
    organization: Optional[str] = None
    photo_url: Optional[str] = None
    citation: Optional[str] = None
    rank: int = 1  # 1 = winner, 2 = runner up


class AwardNomination(TSModel):
    id: str = Field(default_factory=uid)
    category_id: str
    year: int
    nominee_name: str
    nominee_email: EmailStr
    organization: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    citation: str = ""
    supporting_link: Optional[str] = None
    status: str = "pending"  # pending | shortlisted | rejected | winner
    created_at: str = Field(default_factory=now_iso)


# ---------- Events ----------
class Event(TSModel):
    id: str = Field(default_factory=uid)
    title: str
    slug: str
    description: str = ""
    cover_image: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "India"
    start_at: str = Field(default_factory=now_iso)
    end_at: Optional[str] = None
    is_virtual: bool = False
    registration_url: Optional[str] = None
    ticket_price: Optional[float] = None
    status: str = "upcoming"  # upcoming | past | cancelled
    is_featured: bool = False
    seo: SeoMeta = Field(default_factory=SeoMeta)


class EventRSVP(TSModel):
    id: str = Field(default_factory=uid)
    event_id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    organization: Optional[str] = None
    guests: int = 1
    created_at: str = Field(default_factory=now_iso)


# ---------- Advertisements ----------
class AdSlot(TSModel):
    id: str = Field(default_factory=uid)
    name: str  # e.g., "Homepage Leaderboard"
    location: str  # e.g., "home:top", "article:sidebar", "magazine:mid"
    size: str  # e.g., "970x250"
    description: Optional[str] = None
    monthly_price_inr: float = 0
    is_active: bool = True


class AdCampaign(TSModel):
    id: str = Field(default_factory=uid)
    client_id: str  # user with role=client
    slot_id: str
    name: str
    creative_url: Optional[str] = None
    click_url: Optional[str] = None
    start_date: str
    end_date: str
    status: str = "pending"  # pending | approved | active | paused | completed | rejected
    impressions: int = 0
    clicks: int = 0
    total_cost_inr: float = 0
    created_at: str = Field(default_factory=now_iso)


class Sponsor(TSModel):
    id: str = Field(default_factory=uid)
    name: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    tier: str = "silver"  # platinum | gold | silver | bronze | partner
    order: int = 0
    is_active: bool = True


# ---------- Newsletter ----------
class NewsletterIssue(TSModel):
    id: str = Field(default_factory=uid)
    subject: str
    slug: str
    preview_text: Optional[str] = None
    body_html: str = ""
    cover_image: Optional[str] = None
    status: str = "draft"  # draft | scheduled | sent
    scheduled_at: Optional[str] = None
    sent_at: Optional[str] = None
    recipients_count: int = 0
    created_at: str = Field(default_factory=now_iso)


class Subscriber(TSModel):
    id: str = Field(default_factory=uid)
    email: EmailStr
    name: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: str = "website"
    is_active: bool = True
    created_at: str = Field(default_factory=now_iso)


# ---------- Media Library ----------
class MediaFolder(TSModel):
    id: str = Field(default_factory=uid)
    name: str
    parent_id: Optional[str] = None
    created_at: str = Field(default_factory=now_iso)


class MediaAsset(TSModel):
    id: str = Field(default_factory=uid)
    filename: str
    url: str
    mime_type: str
    size_bytes: int = 0
    width: Optional[int] = None
    height: Optional[int] = None
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    folder_id: Optional[str] = None
    uploader_id: Optional[str] = None
    created_at: str = Field(default_factory=now_iso)


# ---------- Menus & Navigation ----------
class MenuItem(TSModel):
    id: str = Field(default_factory=uid)
    location: str  # header | footer | mobile
    label: str
    url: str
    order: int = 0
    parent_id: Optional[str] = None
    is_external: bool = False
    is_active: bool = True


# ---------- Homepage Builder ----------
class HomepageSection(TSModel):
    id: str = Field(default_factory=uid)
    key: str  # e.g., "hero", "featured_grid", "verticals", "podcast", "awards", "events", "brands", "newsletter"
    title: Optional[str] = None
    subtitle: Optional[str] = None
    order: int = 0
    is_active: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


# ---------- Pages (CMS) ----------
class Page(TSModel):
    id: str = Field(default_factory=uid)
    slug: str
    title: str
    body: str = ""
    hero_image: Optional[str] = None
    is_published: bool = True
    seo: SeoMeta = Field(default_factory=SeoMeta)
    updated_at: str = Field(default_factory=now_iso)


# ---------- Forms & Enquiries ----------
class Enquiry(TSModel):
    id: str = Field(default_factory=uid)
    kind: str = "contact"  # contact | advertise | partnership | media | podcast_guest
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    subject: Optional[str] = None
    message: str = ""
    source_page: Optional[str] = None
    status: str = "new"  # new | contacted | qualified | closed
    assigned_to: Optional[str] = None
    created_at: str = Field(default_factory=now_iso)


# ---------- Integration Settings ----------
class IntegrationSetting(TSModel):
    id: str = Field(default_factory=uid)
    provider: str  # resend | cloudinary | stripe | whatsapp | google_analytics | search_console | meta_pixel | linkedin | google_oauth | openai | emergent_llm | emergent_storage
    label: str
    is_enabled: bool = False
    config: Dict[str, str] = Field(default_factory=dict)  # api_key / client_id etc
    notes: Optional[str] = None
    updated_at: str = Field(default_factory=now_iso)


# ---------- Site Settings ----------
class SiteSettings(TSModel):
    id: str = "site_settings"
    site_name: str = "Musafir Media Publications"
    tagline: str = "Three Paths, One Bold Journey"
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None
    favicon_url: Optional[str] = None
    contact_email: EmailStr = "dimple@musafirmediahub.com"
    contact_phone: str = "+91 96508 05752"
    address: str = "61 Basement, Defence Enclave, Preet Vihar, New Delhi - 110092"
    social: Dict[str, str] = Field(default_factory=lambda: {
        "instagram": "https://www.instagram.com/",
        "facebook": "https://www.facebook.com/",
        "twitter": "https://www.twitter.com/",
        "linkedin": "https://www.linkedin.com/",
        "youtube": "https://www.youtube.com/",
    })
    about: str = ""
    mission: str = ""
    vision: str = ""
    footer_note: str = "© 2026 Musafir Media Publications Pvt Ltd. All rights reserved."
    default_seo: SeoMeta = Field(default_factory=SeoMeta)


# ---------- Analytics ----------
class AnalyticsEvent(TSModel):
    id: str = Field(default_factory=uid)
    kind: str  # page_view | article_view | podcast_play | ad_impression | ad_click | newsletter_signup
    entity_id: Optional[str] = None
    path: Optional[str] = None
    referrer: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: str = Field(default_factory=now_iso)


# ---------- Audit Log ----------
class AuditLog(TSModel):
    id: str = Field(default_factory=uid)
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    entity: Optional[str] = None
    entity_id: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=now_iso)
