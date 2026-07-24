"""Seed initial data for Musafir Media Publications.
Idempotent — safe to run repeatedly. Only inserts if collections are empty.
"""
from datetime import datetime, timedelta, timezone

from .database import get_db
from .models import (
    User, Category, Author, Article, MagazineIssue, PodcastEpisode,
    AwardCategory, AwardWinner, Event, AdSlot, Sponsor,
    HomepageSection, MenuItem, IntegrationSetting, SiteSettings, now_iso,
)
from .security import hash_password

# High-quality luxury travel / editorial image URLs from design guidelines
IMG = {
    "hero1": "https://images.unsplash.com/photo-1782835576404-f5eaddd63ac3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NTYxODl8MHwxfHNlYXJjaHw0fHxsdXh1cnklMjB0cmF2ZWwlMjBsaWZlc3R5bGV8ZW58MHx8fHwxNzg0MTI4MjIwfDA&ixlib=rb-4.1.0&q=85",
    "hero2": "https://images.pexels.com/photos/15713593/pexels-photo-15713593.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "mag1": "https://images.unsplash.com/photo-1724405095085-06d4246a2af8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2MjJ8MHwxfHNlYXJjaHwyfHxtYWdhemluZSUyMGVkaXRvcmlhbCUyMG1vZGVsfGVufDB8fHx8MTc4NDEyODIyMXww&ixlib=rb-4.1.0&q=85",
    "mag2": "https://images.unsplash.com/photo-1549298222-1c31e8915347?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2MjJ8MHwxfHNlYXJjaHwxfHxtYWdhemluZSUyMGVkaXRvcmlhbCUyMG1vZGVsfGVufDB8fHx8MTc4NDEyODIyMXww&ixlib=rb-4.1.0&q=85",
    "pod1": "https://images.pexels.com/photos/31213674/pexels-photo-31213674.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "pod2": "https://images.unsplash.com/photo-1478737270239-2f02b77fc618?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxwb2RjYXN0JTIwc3R1ZGlvJTIwbWljcm9waG9uZXxlbnwwfHx8fDE3ODQxMjgyMjF8MA&ixlib=rb-4.1.0&q=85",
    "award": "https://images.unsplash.com/photo-1650240852447-46505dba4726?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMzJ8MHwxfHNlYXJjaHwyfHxnb2xkJTIwdHJvcGh5JTIwYXdhcmQlMjBjZXJlbW9ueXxlbnwwfHx8fDE3ODQxMjgyMjF8MA&ixlib=rb-4.1.0&q=85",
    "arch": "https://images.unsplash.com/photo-1483366774565-c783b9f70e2c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2MDV8MHwxfHNlYXJjaHwyfHxtb2Rlcm4lMjBtaW5pbWFsJTIwaG90ZWwlMjBhcmNoaXRlY3R1cmV8ZW58MHx8fHwxNzg0MTI4MjIxfDA&ixlib=rb-4.1.0&q=85",
    "avatar1": "https://i.pravatar.cc/300?img=32",
    "avatar2": "https://i.pravatar.cc/300?img=47",
    "avatar3": "https://i.pravatar.cc/300?img=12",
}


async def seed_all():
    db = get_db()

    # ---------- Super Admin ----------
    if not await db.users.find_one({"email": "admin@musafirmedia.com"}):
        await db.users.insert_one(User(
            email="admin@musafirmedia.com",
            full_name="Musafir Super Admin",
            role="super_admin",
            password_hash=hash_password("Admin@12345"),
        ).model_dump())

    if not await db.users.find_one({"email": "editor@musafirmedia.com"}):
        await db.users.insert_one(User(
            email="editor@musafirmedia.com",
            full_name="Priya Editor",
            role="editor_in_chief",
            password_hash=hash_password("Editor@12345"),
        ).model_dump())

    if not await db.users.find_one({"email": "client@musafirmedia.com"}):
        await db.users.insert_one(User(
            email="client@musafirmedia.com",
            full_name="Aarav Sharma",
            role="client",
            company="Wanderlust Retreats",
            password_hash=hash_password("Client@12345"),
        ).model_dump())

    # ---------- Site Settings ----------
    if not await db.site_settings.find_one({"id": "site_settings"}):
        s = SiteSettings(
            about=(
                "We are driven by the spirit of exploration. Just like a Musafir — a traveller who never stops "
                "discovering the world — we're on a mission to redefine travel media. Launched in November 2018, "
                "Musafir Media Hub is a B2B travel media platform, available in both print and digital formats, that "
                "showcases India to the world as a role model for respect, sustainability, and exploration."
            ),
            mission=(
                "To be the most trusted voice in luxury travel, hospitality and tourism media — inspiring "
                "readers, empowering brands, and celebrating excellence across the industry."
            ),
            vision=(
                "A world where every traveller's story matters, every destination is honoured, and every "
                "brand finds a bold platform to reach discerning audiences."
            ),
        )
        await db.site_settings.insert_one(s.model_dump())

    # ---------- Categories ----------
    if await db.categories.count_documents({}) == 0:
        cats = [
            ("Travel", "travel", "Destinations, itineraries and journeys.", 1),
            ("Hospitality", "hospitality", "Hotels, resorts and hospitality trends.", 2),
            ("Tourism Boards", "tourism-boards", "Government initiatives and national tourism.", 3),
            ("Culture", "culture", "Heritage, art, and cultural stories.", 4),
            ("Lifestyle", "lifestyle", "Food, luxury living and modern lifestyle.", 5),
            ("Business", "business", "Industry news and business of travel.", 6),
        ]
        for name, slug, desc, order in cats:
            await db.categories.insert_one(Category(name=name, slug=slug, description=desc, order=order).model_dump())

    cat_docs = await db.categories.find({}, {"_id": 0}).to_list(50)
    cat_by_slug = {c["slug"]: c for c in cat_docs}

    # ---------- Authors ----------
    if await db.authors.count_documents({}) == 0:
        authors = [
            ("Dimple Verma", "dimple-verma", "Founder & Editor-in-Chief", IMG["avatar1"], "Founder of Musafir Media Publications, storyteller and travel industry veteran."),
            ("Rohan Bakshi", "rohan-bakshi", "Senior Travel Correspondent", IMG["avatar3"], "Award-winning journalist covering luxury travel across Asia."),
            ("Anaïs Kapoor", "anais-kapoor", "Contributing Editor, Culture", IMG["avatar2"], "Writes on heritage, art and the intersection of culture and travel."),
        ]
        for name, slug, desig, avatar, bio in authors:
            await db.authors.insert_one(Author(name=name, slug=slug, designation=desig, avatar_url=avatar, bio=bio).model_dump())

    author_docs = await db.authors.find({}, {"_id": 0}).to_list(50)
    author_by_slug = {a["slug"]: a for a in author_docs}

    # ---------- Articles ----------
    if await db.articles.count_documents({}) == 0:
        arts = [
            {
                "title": "The Slow Return of the Grand Indian Rail Journey",
                "subtitle": "Palace-on-wheels reimagined for a new era of conscious luxury",
                "excerpt": "From the Deccan Odyssey to the Maharajas' Express, India's iconic luxury rail experiences are being quietly reinvented.",
                "cover_image": IMG["hero1"],
                "category": "travel",
                "author": "dimple-verma",
                "is_hero": True,
                "is_featured": True,
                "tags": ["luxury", "rail", "india"],
                "body": _long_body("The Slow Return of the Grand Indian Rail Journey"),
            },
            {
                "title": "Inside the Rise of Micro-Boutique Hotels in the Himalayas",
                "subtitle": "Where fifteen rooms feel more like a private residence than a resort",
                "excerpt": "A new generation of hoteliers is proving that smaller footprints deliver larger stories.",
                "cover_image": IMG["arch"],
                "category": "hospitality",
                "author": "rohan-bakshi",
                "is_featured": True,
                "tags": ["hospitality", "himalayas", "boutique"],
                "body": _long_body("Inside the Rise of Micro-Boutique Hotels in the Himalayas"),
            },
            {
                "title": "Madhya Pradesh Tourism's Bold Bet on Regenerative Travel",
                "subtitle": "The heart of India rewrites the rules of responsible tourism",
                "excerpt": "State-led investment, community-first design, and a rare willingness to say no to mass tourism.",
                "cover_image": IMG["mag1"],
                "category": "tourism-boards",
                "author": "anais-kapoor",
                "is_featured": True,
                "tags": ["madhya pradesh", "regenerative", "government"],
                "body": _long_body("Madhya Pradesh Tourism's Bold Bet on Regenerative Travel"),
            },
            {
                "title": "The Craftsmen of Chanderi — A Weave Reborn",
                "subtitle": "How a single village kept a 700-year-old textile tradition alive",
                "excerpt": "Inside the fragile ecosystem of one of India's most celebrated hand-woven fabrics.",
                "cover_image": IMG["mag2"],
                "category": "culture",
                "author": "anais-kapoor",
                "tags": ["culture", "textile", "craft"],
                "body": _long_body("The Craftsmen of Chanderi"),
            },
            {
                "title": "The New Menu of Indian Luxury",
                "subtitle": "Chefs are quietly redrawing the map of fine dining",
                "excerpt": "From foraged Himalayan spices to eight-course Mughal reinterpretations, this is India's most exciting culinary decade.",
                "cover_image": IMG["hero2"],
                "category": "lifestyle",
                "author": "rohan-bakshi",
                "tags": ["food", "luxury", "dining"],
                "body": _long_body("The New Menu of Indian Luxury"),
            },
            {
                "title": "Business of Travel — Where the Next Trillion Rupees Will Come From",
                "subtitle": "A confidential forecast of Indian outbound and inbound flows to 2030",
                "excerpt": "Data, insight and outlook from industry leaders shaping the next chapter of Indian travel.",
                "cover_image": IMG["award"],
                "category": "business",
                "author": "dimple-verma",
                "tags": ["business", "forecast", "industry"],
                "body": _long_body("Business of Travel"),
            },
        ]
        now = datetime.now(timezone.utc)
        for i, a in enumerate(arts):
            cat = cat_by_slug.get(a["category"])
            au = author_by_slug.get(a["author"])
            article = Article(
                title=a["title"],
                slug="",
                subtitle=a.get("subtitle"),
                excerpt=a["excerpt"],
                body=a["body"],
                cover_image=a["cover_image"],
                category_id=cat["id"] if cat else None,
                author_id=au["id"] if au else None,
                tags=a.get("tags", []),
                is_featured=a.get("is_featured", False),
                is_hero=a.get("is_hero", False),
                status="published",
                reading_time_min=6 + i,
                published_at=(now - timedelta(days=i * 2)).isoformat(),
            )
            article.slug = _slug(article.title)
            await db.articles.insert_one(article.model_dump())

    # ---------- Magazine issues ----------
    if await db.magazine_issues.count_documents({}) == 0:
        issues = [
            ("The Regeneration Issue", "vol-6-issue-2", "Vol 6, Issue 2", "January 2026", IMG["mag1"], True,
             "The definitive issue on how India is redrawing the rules of responsible luxury travel."),
            ("The Heritage Issue", "vol-6-issue-1", "Vol 6, Issue 1", "November 2025", IMG["mag2"], False,
             "Craft, culture and the quiet economics behind India's living heritage."),
            ("The Hospitality Issue", "vol-5-issue-6", "Vol 5, Issue 6", "September 2025", IMG["arch"], False,
             "Sixty pages on the operators, architects and dreamers reshaping Indian hospitality."),
        ]
        for i, (title, slug, num, month, img, current, desc) in enumerate(issues):
            await db.magazine_issues.insert_one(MagazineIssue(
                title=title, slug=slug, issue_number=num, month=month,
                cover_image=img, is_current=current, description=desc,
                published_at=(datetime.now(timezone.utc) - timedelta(days=i * 30)).isoformat(),
            ).model_dump())

    # ---------- Podcast Episodes ----------
    if await db.podcast_episodes.count_documents({}) == 0:
        eps = [
            ("A Founder's Blueprint for Building an Indian Luxury Brand", 12, IMG["pod1"], "Radhika Rao", "Founder, Rasa Hospitality"),
            ("On Longevity in Hospitality — Fifty Years, One Family", 11, IMG["pod2"], "Vikram Oberoi", "Managing Director, The Oberoi Group"),
            ("The Traveller Who Refused to Post — A Philosopher's Case for Silence", 10, IMG["pod1"], "Ananya Iyer", "Writer & Philosopher"),
            ("Regenerative Tourism Isn't a Buzzword — Here's the Math", 9, IMG["pod2"], "Suresh Bhandari", "Founder, Nomadic Nature"),
        ]
        for i, (title, num, img, guest, guest_bio) in enumerate(eps):
            await db.podcast_episodes.insert_one(PodcastEpisode(
                title=title, slug=_slug(title), episode_number=num, season=2,
                description=f"In episode #{num} of The Musafir Podcast, we sit down with {guest} to unpack {title.lower()}.",
                cover_image=img,
                guest_name=guest, guest_bio=guest_bio, guest_avatar=IMG["avatar1"],
                duration_seconds=1800 + i * 200,
                youtube_url="https://www.youtube.com/",
                spotify_url="https://open.spotify.com/",
                apple_url="https://podcasts.apple.com/",
                published_at=(datetime.now(timezone.utc) - timedelta(days=i * 14)).isoformat(),
            ).model_dump())

    # ---------- Awards ----------
    if await db.award_categories.count_documents({}) == 0:
        cats = [
            ("Luxury Hotel of the Year", "luxury-hotel-2026"),
            ("Boutique Property of the Year", "boutique-property-2026"),
            ("Best Tourism Board — Domestic", "best-tourism-board-domestic-2026"),
            ("Sustainable Travel Company of the Year", "sustainable-travel-2026"),
            ("Rising Entrepreneur in Travel", "rising-entrepreneur-2026"),
            ("Editor's Choice — Contribution to Indian Tourism", "editors-choice-2026"),
        ]
        for name, slug in cats:
            await db.award_categories.insert_one(AwardCategory(name=name, slug=slug, description=f"Celebrating excellence in {name.lower()}.", year=2026, edition="IMAA 2026").model_dump())

    # ---------- Events ----------
    if await db.events.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        evs = [
            ("IMAA Awards Night 2026", "imaa-2026", "The 4th edition of India Musafir Awards, celebrating excellence across travel and hospitality.",
             IMG["award"], "Taj Palace, New Delhi", "New Delhi", (now + timedelta(days=90)).isoformat(), "upcoming", True),
            ("Musafir Roundtable — Hospitality 2030", "roundtable-hospitality-2030", "An invite-only closed-door roundtable with 30 senior hoteliers.",
             IMG["arch"], "The Leela, Mumbai", "Mumbai", (now + timedelta(days=45)).isoformat(), "upcoming", True),
            ("Travel Publishers' Meet 2025", "travel-publishers-meet-2025", "Annual publishers' meet held in November 2025 in New Delhi.",
             IMG["hero2"], "The Lalit, New Delhi", "New Delhi", (now - timedelta(days=90)).isoformat(), "past", False),
        ]
        for t, s, d, img, v, c, dt, st, feat in evs:
            await db.events.insert_one(Event(
                title=t, slug=s, description=d, cover_image=img, venue=v, city=c,
                start_at=dt, status=st, is_featured=feat,
            ).model_dump())

    # ---------- Ad Slots ----------
    if await db.ad_slots.count_documents({}) == 0:
        slots = [
            ("Homepage Leaderboard", "home:top", "970x250", "Above-the-fold homepage leaderboard.", 250000),
            ("Homepage Mid Banner", "home:mid", "728x300", "Between featured articles and podcast.", 180000),
            ("Article Sidebar", "article:sidebar", "300x600", "Right rail on every article page.", 120000),
            ("Magazine Cover Adjacency", "magazine:cover", "600x400", "Adjacent to the current issue cover.", 200000),
            ("Podcast Player Sponsor", "podcast:player", "600x120", "Sponsor slot on the podcast player.", 150000),
            ("Newsletter Header", "newsletter:top", "600x200", "Top of every editorial newsletter.", 90000),
        ]
        for name, loc, size, desc, price in slots:
            await db.ad_slots.insert_one(AdSlot(name=name, location=loc, size=size, description=desc, monthly_price_inr=price).model_dump())

    # ---------- Sponsors ----------
    if await db.sponsors.count_documents({}) == 0:
        sponsors = [
            ("Madhya Pradesh Tourism", "https://static.wixstatic.com/media/d1cc3a_6eafac695fa14146811a0ef356d06954~mv2.png/v1/fill/w_240,h_240,al_c,q_85/mp.png", "https://www.mptourism.com", "platinum", 1),
            ("Ease My Trip", "https://static.wixstatic.com/media/d1cc3a_309e0985e0784ca4870c79a909b1c9fe~mv2.jpeg/v1/fill/w_240,h_240,al_c,q_85/emt.jpg", "https://www.easemytrip.com", "gold", 2),
            ("India Tourism", "https://static.wixstatic.com/media/d1cc3a_db5c625d3f174ad6bcc5b2bd4b50d71e~mv2.png/v1/fill/w_240,h_240,al_c,q_85/it.png", "https://www.incredibleindia.org", "platinum", 3),
            ("ITB India", "https://static.wixstatic.com/media/d1cc3a_2c7d8b25c00043138a8b39614cf5fce6~mv2.jpg/v1/fill/w_240,h_240,al_c,q_85/itb.jpg", "https://www.itb-india.com", "gold", 4),
            ("IATO", "https://static.wixstatic.com/media/d1cc3a_cd81a9321a904ed48314954fdce9ca0b~mv2.png/v1/fill/w_240,h_240,al_c,q_85/iato.png", "https://www.iato.in", "silver", 5),
            ("FHTR", "https://static.wixstatic.com/media/d1cc3a_fc254f42e7cc4edd8dc529be841d3ef2~mv2.jpg/v1/fill/w_240,h_240,al_c,q_85/fhtr.jpg", "https://www.fhtr.in", "silver", 6),
            ("Melange 2025", "https://static.wixstatic.com/media/d1cc3a_6276b4053540452f85c8cab312c4fd7c~mv2.jpg/v1/fill/w_240,h_240,al_c,q_85/melange.jpg", "#", "partner", 7),
            ("OA DMC", "https://static.wixstatic.com/media/d1cc3a_e0b1dc48a8b84ce7beaeac0f390f067d~mv2.png/v1/fill/w_240,h_240,al_c,q_85/oadmc.png", "#", "partner", 8),
        ]
        for name, logo, site, tier, order in sponsors:
            await db.sponsors.insert_one(Sponsor(name=name, logo_url=logo, website=site, tier=tier, order=order).model_dump())

    # ---------- Homepage Sections ----------
    if await db.homepage_sections.count_documents({}) == 0:
        sections = [
            ("hero", "The Musafir Cover Story", "Editor's pick this fortnight", 0, {}),
            ("verticals", "Three Paths, One Bold Journey", "Magazine · Awards · Podcast", 1, {}),
            ("featured_grid", "The Editorial Grid", "This week's most-read stories", 2, {}),
            ("magazine", "The Current Issue", "Volume 6 · Issue 2 · The Regeneration Issue", 3, {}),
            ("podcast", "On The Musafir Podcast", "Conversations shaping the next decade of travel", 4, {}),
            ("awards", "IMAA 2026", "India Musafir Awards — nominations open", 5, {}),
            ("events", "Upcoming Convenings", "Roundtables, awards nights and closed briefings", 6, {}),
            ("brands", "Brands We've Worked With", "Trusted by the industry's most discerning names", 7, {}),
            ("newsletter", "Subscribe to the Musafir Brief", "Weekly editorial into your inbox — no noise, ever", 8, {}),
        ]
        for key, title, subtitle, order, config in sections:
            await db.homepage_sections.insert_one(HomepageSection(key=key, title=title, subtitle=subtitle, order=order, config=config).model_dump())

    # ---------- Menus ----------
    if await db.menus.count_documents({}) == 0:
        header = [
            ("Magazine", "/magazine", 1),
            ("News", "/news", 2),
            ("Podcast", "/podcast", 3),
            ("Awards", "/awards", 4),
            ("Events", "/events", 5),
            ("About", "/about", 6),
            ("Advertise", "/advertise", 7),
        ]
        for label, url, order in header:
            await db.menus.insert_one(MenuItem(location="header", label=label, url=url, order=order).model_dump())
        footer_columns = {
            "footer:explore": [("Magazine", "/magazine"), ("News", "/news"), ("Podcast", "/podcast"), ("Awards", "/awards"), ("Events", "/events")],
            "footer:company": [("About", "/about"), ("Contact", "/contact"), ("Advertise", "/advertise"), ("Newsletter", "/newsletter")],
            "footer:legal": [("Terms", "/legal/terms"), ("Privacy", "/legal/privacy"), ("Cookies", "/legal/cookies")],
        }
        for loc, items in footer_columns.items():
            for i, (label, url) in enumerate(items):
                await db.menus.insert_one(MenuItem(location=loc, label=label, url=url, order=i).model_dump())

    # ---------- Integrations placeholder rows ----------
    if await db.integration_settings.count_documents({}) == 0:
        providers = [
            ("emergent_llm", "Emergent Universal LLM", True, {"model": "claude-sonnet-4-5"}, "Powered by Emergent Universal Key — used by AI Assist in the editor."),
            ("emergent_storage", "Emergent Object Storage", False, {"bucket": "", "region": ""}, "Enable to store media on Emergent object storage instead of local disk."),
            ("google_oauth", "Google OAuth (Sign in with Google)", False, {"client_id": ""}, "Paste your Google OAuth Web Client ID to enable social sign-in."),
            ("resend", "Resend (Transactional Email)", False, {"api_key": "", "from_email": ""}, "For newsletters and transactional emails."),
            ("cloudinary", "Cloudinary (Media CDN)", False, {"cloud_name": "", "api_key": "", "api_secret": ""}, "Alternative CDN for media assets."),
            ("stripe", "Stripe (Payments)", False, {"publishable_key": "", "secret_key": ""}, "For subscriptions and ad marketplace billing."),
            ("whatsapp", "WhatsApp Business API", False, {"phone_number_id": "", "access_token": ""}, "For lead notifications and client comms."),
            ("google_analytics", "Google Analytics 4", False, {"measurement_id": ""}, "For pageview and conversion tracking."),
            ("search_console", "Google Search Console", False, {"verification_code": ""}, "For SEO monitoring."),
            ("meta_pixel", "Meta Pixel", False, {"pixel_id": ""}, "For Facebook/Instagram ad tracking."),
            ("linkedin", "LinkedIn Insight Tag", False, {"partner_id": ""}, "For B2B campaign tracking."),
        ]
        for provider, label, enabled, config, notes in providers:
            await db.integration_settings.insert_one(IntegrationSetting(
                provider=provider, label=label, is_enabled=enabled, config=config, notes=notes,
            ).model_dump())


def _slug(title: str) -> str:
    import re
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s.strip("-")


def _long_body(title: str) -> str:
    p1 = (
        "There are stories that arrive quietly. They begin at a train platform in the small hours, or in the "
        "muted lobby of a hotel that has learned, with time, when not to speak. This is one of those stories."
    )
    p2 = (
        "In the last eighteen months, we have watched a small movement grow — one that refuses to describe "
        "itself as a movement. It has no manifesto, no hashtag, no keynote conference. It has, instead, a set "
        "of quiet convictions about how India should travel — and how India should be travelled through."
    )
    p3 = (
        "It is easy to romanticise this. Editors are prone to romantic sentences, and the Indian subcontinent "
        "has a way of making even the most disciplined writer reach for one. So let us try, for a moment, to "
        "resist the temptation, and instead look at the numbers."
    )
    p4 = (
        "By 2030, India is projected to move nearly three hundred million domestic travellers a year across its "
        "luxury and premium segments. That number is quietly staggering. And it is arriving at a moment when the "
        "operators most equipped to receive it are also the ones asking the hardest questions."
    )
    quote = (
        "We do not want to be Bali. We do not want to be the next anything. We want to be, precisely, "
        "the first version of this country the world has ever properly seen."
    )
    p5 = (
        f"That is a working thesis for many of the operators we spoke with while reporting on {title.lower()}. "
        "It is not, in the end, a story about hospitality. It is a story about restraint — and how restraint, "
        "counterintuitively, has become the most exportable asset Indian travel now has."
    )
    return (
        f"<p>{p1}</p><p>{p2}</p><p>{p3}</p>"
        f"<blockquote>{quote}</blockquote>"
        f"<p>{p4}</p><p>{p5}</p>"
    )
