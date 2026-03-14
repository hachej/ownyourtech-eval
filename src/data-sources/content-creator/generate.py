#!/usr/bin/env python3
"""Generate synthetic data for the content-creator eval scenario.

Produces 7 source datasets with deterministic seed, realistic distributions,
and controlled email overlap across sources. Also produces 3 ground truth CSVs.

Usage:
    python generate.py
"""

import csv
import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path

SEED = 42
DATA_DIR = Path(__file__).parent / "data" / "content-creator"
GT_DIR = Path(__file__).parent / "gt" / "content-creator"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

random.seed(SEED)

FIRST_NAMES = [
    "Alice", "Bob", "Carol", "Dan", "Eva", "Frank", "Grace", "Hank", "Iris",
    "Jack", "Karen", "Leo", "Mia", "Noah", "Olivia", "Paul", "Quinn", "Rosa",
    "Sam", "Tina", "Uma", "Vic", "Wendy", "Xander", "Yara", "Zach",
    "Aiden", "Bella", "Caleb", "Diana", "Ethan", "Fiona", "George", "Holly",
    "Ivan", "Julia", "Kyle", "Lena", "Marcus", "Nina", "Oscar", "Petra",
    "Reed", "Sasha", "Tyler", "Ursula", "Vera", "Wade", "Ximena", "Yuri",
]

LAST_NAMES = [
    "Smith", "Jones", "Lee", "Garcia", "Kim", "Nguyen", "Brown", "Davis",
    "Wilson", "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore",
    "Jackson", "Martin", "Thompson", "White", "Lopez", "Harris", "Clark",
    "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott",
    "Green", "Baker", "Adams", "Nelson", "Hill", "Ramirez", "Campbell",
    "Mitchell", "Roberts", "Carter", "Phillips", "Evans", "Turner", "Torres",
    "Parker", "Collins", "Edwards", "Stewart", "Flores", "Morris",
]

PERSONAL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com", "icloud.com"]
BUSINESS_DOMAINS = [
    "acme.io", "techcorp.com", "dataflow.dev", "brightside.co", "novalabs.ai",
    "cloudhub.net", "greenleaf.org", "streamline.io", "pixelcraft.design",
    "fusionworks.com", "bluewave.tech", "ironclad.dev", "sparkline.co",
]

LINKEDIN_TOPICS = [
    "Just shipped a new feature that reduced query time by 80%.",
    "Hot take: most data pipelines are over-engineered.",
    "Learned something surprising about DuckDB performance today.",
    "Why I switched from Airflow to Dagster — a thread.",
    "Hiring is broken in data engineering. Here's what I'd change.",
    "The best dashboards tell a story, not just show numbers.",
    "5 things I wish I knew before building my first data warehouse.",
    "Open source tools have completely transformed how I work.",
    "Spent the weekend refactoring our ETL and cut costs by 40%.",
    "Controversial opinion: you don't need a data lake yet.",
    "My productivity hack: write the SQL query before the schema.",
    "Just gave a talk on modern data stacks at the local meetup.",
    "The future of analytics is local-first. Change my mind.",
    "Reflecting on 10 years in tech — still love building things.",
    "Data quality is everyone's responsibility, not just the DE team.",
    "Automated testing for data pipelines saved us from a major outage.",
    "Reading 'Designing Data-Intensive Applications' for the third time.",
    "Why event-driven architectures are worth the complexity.",
    "Wrote a blog post on incremental materialization patterns.",
    "The gap between a prototype and production is always larger than expected.",
    "Newsletter engagement metrics are fascinating to analyze.",
    "Building in public: our analytics stack journey.",
    "Sometimes the simplest solution is a cron job and a shell script.",
    "Pair programming with an AI agent — surprisingly effective.",
    "Grateful for the data community — always learning from you all.",
]

YOUTUBE_TITLES = [
    "Building a Local Analytics Stack from Scratch",
    "DuckDB vs PostgreSQL: When to Use What",
    "Data Pipeline Patterns for Small Teams",
    "How I Track Newsletter Metrics with Python",
    "Content Creator Analytics Dashboard Tutorial",
    "Identity Resolution Explained Simply",
    "ETL Best Practices for Solo Developers",
    "My Favorite Open Source BI Tools",
    "Data Modeling for Content Creators",
    "Monthly Metrics Review: What I Track and Why",
    "Setting Up Event Tracking with Walker.js",
    "Link Click Analytics with Short.io",
    "Ghost CMS Analytics Deep Dive",
    "MailerLite vs ConvertKit: Data Comparison",
    "Building Ground Truth Datasets",
    "SQL Window Functions for Content Analytics",
    "Automating Reports with Python and DuckDB",
    "Content Performance Tiers: How I Categorize",
    "From Raw Data to Insights: Full Walkthrough",
    "Data Engineering Side Projects That Matter",
]

GHOST_POST_TITLES = [
    "The Case for Local-First Analytics",
    "Understanding Your Newsletter Metrics",
    "Building a Data Stack on a Budget",
    "Identity Resolution Without a CDP",
    "Monthly Content Review: Lessons Learned",
    "Why I Self-Host My Analytics",
    "Data Quality Checklist for Creators",
    "ETL Patterns for Newsletter Data",
    "Choosing the Right BI Tool",
    "Content Performance: Beyond Vanity Metrics",
    "How to Track Cross-Platform Engagement",
    "The Modern Creator's Data Toolkit",
    "From Spreadsheets to SQL: A Migration Guide",
    "Event Tracking Best Practices",
    "Link Analytics: What Clicks Tell You",
    "Email Open Rates: Myths and Reality",
    "Building Dashboards That Drive Decisions",
    "Data Modeling for Content Businesses",
    "Automating Your Monthly Metrics Report",
    "The Future of Creator Analytics",
]

UTM_SOURCES = ["linkedin", "twitter", "newsletter", "youtube", "blog", "direct"]
UTM_MEDIUMS = ["social", "email", "referral", "video", "organic"]
UTM_CAMPAIGNS = [
    "spring-launch", "weekly-digest", "product-update", "case-study",
    "webinar-promo", "ebook-download", "survey-2025", "holiday-special",
    "q1-review", "new-feature", "community-event", "partner-collab",
]

PAGE_PATHS = [
    "/", "/about", "/blog", "/blog/local-analytics", "/blog/duckdb-guide",
    "/blog/newsletter-metrics", "/blog/identity-resolution", "/pricing",
    "/contact", "/docs", "/docs/getting-started", "/docs/api-reference",
    "/case-studies", "/newsletter", "/tools", "/changelog",
]

EVENT_NAMES = ["page_view", "scroll", "click", "form_submit", "newsletter_signup", "download"]
MAILERLITE_GROUPS = ["newsletter", "blog-updates", "product-news", "webinar-attendees", "beta-testers"]


def _rand_date(start: datetime, end: datetime) -> datetime:
    delta = (end - start).total_seconds()
    return start + timedelta(seconds=random.random() * delta)


def _make_slug(title: str) -> str:
    return title.lower().replace(" ", "-").replace(":", "").replace(",", "")[:60]


def _rand_name():
    return random.choice(FIRST_NAMES), random.choice(LAST_NAMES)


# ---------------------------------------------------------------------------
# Step 1: Generate email pool with overlap control
# ---------------------------------------------------------------------------

def generate_email_pool(n=250):
    """Create a pool of unique emails with name associations."""
    emails = []
    used = set()
    for _ in range(n):
        first, last = _rand_name()
        is_personal = random.random() < 0.6
        domain = random.choice(PERSONAL_DOMAINS) if is_personal else random.choice(BUSINESS_DOMAINS)
        # Create email variants
        variant = random.choice([
            f"{first.lower()}.{last.lower()}",
            f"{first.lower()}{last.lower()}",
            f"{first[0].lower()}{last.lower()}",
            f"{first.lower()}.{last.lower()}{random.randint(1, 99)}",
        ])
        email = f"{variant}@{domain}"
        if email in used:
            email = f"{variant}{random.randint(100, 999)}@{domain}"
        if email in used:
            continue
        used.add(email)
        emails.append({
            "email": email,
            "first_name": first,
            "last_name": last,
            "name": f"{first} {last}",
            "domain": domain,
            "is_personal": is_personal,
        })
    return emails


def assign_overlap(pool):
    """Assign emails to sources with controlled overlap.

    ghost_member and mailerlite are the two big lists (~200 each).
    ~60% of ghost emails also in mailerlite.
    ~30% of ghost emails also in walker.
    ~10% of ghost emails also in shortio.
    """
    random.shuffle(pool)

    # Ghost members: first 200
    ghost_emails = pool[:200]
    # MailerLite: 60% overlap with ghost + some unique
    n_overlap_ml = int(200 * 0.60)  # 120 shared with ghost
    ml_from_ghost = random.sample(ghost_emails, n_overlap_ml)
    ml_unique_needed = 200 - n_overlap_ml  # 80 unique
    ml_unique = pool[200:200 + ml_unique_needed]
    mailerlite_emails = ml_from_ghost + ml_unique

    # Walker: 30% of ghost emails
    n_overlap_walker = int(200 * 0.30)  # 60 from ghost
    walker_from_ghost = random.sample(ghost_emails, n_overlap_walker)
    # Plus some from mailerlite and unique to reach ~300 events (not unique emails)
    walker_extra = random.sample(mailerlite_emails, 20) + pool[200 + ml_unique_needed:200 + ml_unique_needed + 30]
    walker_email_pool = list({e["email"]: e for e in (walker_from_ghost + walker_extra)}.values())

    # Short.io: 10% of ghost emails
    n_overlap_shortio = int(200 * 0.10)  # 20 from ghost
    shortio_from_ghost = random.sample(ghost_emails, n_overlap_shortio)
    shortio_extra = random.sample(pool[200:], min(15, len(pool[200:])))
    shortio_email_pool = list({e["email"]: e for e in (shortio_from_ghost + shortio_extra)}.values())

    return ghost_emails, mailerlite_emails, walker_email_pool, shortio_email_pool


# ---------------------------------------------------------------------------
# Step 2: Generate source datasets
# ---------------------------------------------------------------------------

DATE_START = datetime(2024, 1, 1)
DATE_END = datetime(2025, 6, 30)


def gen_linkedin_posts(n=120):
    """Generate authoredup_posts.csv — LinkedIn posts."""
    rows = []
    for i in range(n):
        pub = _rand_date(DATE_START, DATE_END)
        impressions = int(random.lognormvariate(7, 1.2))  # median ~1100
        reactions = int(impressions * random.uniform(0.01, 0.08))
        comments = int(impressions * random.uniform(0.002, 0.02))
        shares = int(impressions * random.uniform(0.001, 0.01))
        rows.append({
            "post_id": f"li_{i+1:04d}",
            "text": random.choice(LINKEDIN_TOPICS),
            "impressions": impressions,
            "reactions": reactions,
            "comments": comments,
            "shares": shares,
            "published_at": pub.strftime("%Y-%m-%d %H:%M:%S"),
        })
    rows.sort(key=lambda r: r["post_id"])
    return rows


def gen_youtube_videos(n=50):
    """Generate youtube_videos.csv."""
    rows = []
    titles_pool = YOUTUBE_TITLES * 3  # allow repeats with suffix
    for i in range(n):
        pub = _rand_date(DATE_START, DATE_END)
        views = int(random.lognormvariate(7.5, 1.5))
        likes = int(views * random.uniform(0.02, 0.08))
        comments = int(views * random.uniform(0.005, 0.02))
        title = YOUTUBE_TITLES[i % len(YOUTUBE_TITLES)]
        if i >= len(YOUTUBE_TITLES):
            title = f"{title} (Part {i // len(YOUTUBE_TITLES) + 1})"
        rows.append({
            "video_id": f"yt_{i+1:04d}",
            "title": title,
            "view_count": views,
            "like_count": likes,
            "comment_count": comments,
            "published_at": pub.strftime("%Y-%m-%d %H:%M:%S"),
        })
    rows.sort(key=lambda r: r["video_id"])
    return rows


def gen_ghost_members(ghost_emails):
    """Generate ghost_member.csv."""
    rows = []
    for person in ghost_emails:
        created = _rand_date(DATE_START, DATE_END)
        status = random.choices(["free", "paid", "comped"], weights=[70, 20, 10])[0]
        email_count = random.randint(5, 80)
        opened = int(email_count * random.uniform(0.1, 0.9))
        rate = round(opened / email_count * 100, 1) if email_count > 0 else 0.0
        rows.append({
            "email": person["email"],
            "name": person["name"],
            "status": status,
            "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
            "email_count": email_count,
            "email_opened_count": opened,
            "email_open_rate": rate,
        })
    rows.sort(key=lambda r: r["email"])
    return rows


def gen_ghost_posts(n=60):
    """Generate ghost_post.csv."""
    rows = []
    for i in range(n):
        pub = _rand_date(DATE_START, DATE_END)
        title = GHOST_POST_TITLES[i % len(GHOST_POST_TITLES)]
        if i >= len(GHOST_POST_TITLES):
            title = f"{title} — Part {i // len(GHOST_POST_TITLES) + 1}"
        word_count = random.randint(300, 3000)
        delivered = random.randint(100, 500)
        opened = int(delivered * random.uniform(0.2, 0.7))
        rows.append({
            "post_id": f"gp_{i+1:04d}",
            "title": title,
            "slug": _make_slug(title),
            "published_at": pub.strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": word_count,
            "email_delivered_count": delivered,
            "email_opened_count": opened,
        })
    rows.sort(key=lambda r: r["post_id"])
    return rows


def gen_mailerlite(mailerlite_emails):
    """Generate mailerlite_subscriber.csv."""
    rows = []
    for person in mailerlite_emails:
        sub_date = _rand_date(DATE_START, DATE_END)
        status = random.choices(["active", "unsubscribed", "bounced"], weights=[80, 15, 5])[0]
        n_groups = random.randint(1, 3)
        groups = ";".join(random.sample(MAILERLITE_GROUPS, n_groups))
        rows.append({
            "email": person["email"],
            "status": status,
            "groups": groups,
            "subscribed_at": sub_date.strftime("%Y-%m-%d %H:%M:%S"),
        })
    rows.sort(key=lambda r: r["email"])
    return rows


def gen_shortio_clicks(shortio_pool, n=150):
    """Generate shortio_clicks.jsonl."""
    rows = []
    for i in range(n):
        person = random.choice(shortio_pool)
        clicked = _rand_date(DATE_START, DATE_END)
        rows.append({
            "clicked_at": clicked.strftime("%Y-%m-%d %H:%M:%S"),
            "utm_source": random.choice(UTM_SOURCES),
            "utm_medium": random.choice(UTM_MEDIUMS),
            "utm_campaign": random.choice(UTM_CAMPAIGNS),
            "email": person["email"],
        })
    rows.sort(key=lambda r: r["clicked_at"])
    return rows


def gen_walker_events(walker_pool, n=300):
    """Generate walker_events.jsonl."""
    rows = []
    for i in range(n):
        person = random.choice(walker_pool)
        ts = _rand_date(DATE_START, DATE_END)
        event = random.choices(EVENT_NAMES, weights=[50, 15, 15, 5, 10, 5])[0]
        rows.append({
            "session_id": f"sess_{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}",
            "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event_name": event,
            "page_path": random.choice(PAGE_PATHS),
            "email": person["email"],
        })
    rows.sort(key=lambda r: r["timestamp"])
    return rows


# ---------------------------------------------------------------------------
# Step 3: Generate ground truth
# ---------------------------------------------------------------------------

def gen_gt_accounts(ghost_members, mailerlite_subs, walker_events, shortio_clicks):
    """creator__accounts.csv: one row per unique email."""
    # Collect all emails
    all_emails = set()
    ghost_by_email = {}
    for r in ghost_members:
        all_emails.add(r["email"])
        ghost_by_email[r["email"]] = r

    ml_by_email = {}
    for r in mailerlite_subs:
        all_emails.add(r["email"])
        ml_by_email[r["email"]] = r

    walker_emails = set()
    for r in walker_events:
        all_emails.add(r["email"])
        walker_emails.add(r["email"])

    shortio_emails = set()
    for r in shortio_clicks:
        all_emails.add(r["email"])
        shortio_emails.add(r["email"])

    rows = []
    for email in sorted(all_emails):
        gm = ghost_by_email.get(email)
        ml = ml_by_email.get(email)
        is_walker = email in walker_emails
        is_shortio = email in shortio_emails

        domain = email.split("@")[1]
        is_personal = domain in PERSONAL_DOMAINS

        # Name: prefer ghost, else blank
        name = gm["name"] if gm else ""

        # first_seen: earliest date across all sources
        dates = []
        if gm:
            dates.append(gm["created_at"])
        if ml:
            dates.append(ml["subscribed_at"])
        # walker and shortio don't have a single "created" date; use earliest event
        if is_walker:
            walker_dates = [e["timestamp"].replace("T", " ").replace("Z", "") for e in walker_events if e["email"] == email]
            if walker_dates:
                dates.append(min(walker_dates))
        if is_shortio:
            shortio_dates = [e["clicked_at"] for e in shortio_clicks if e["email"] == email]
            if shortio_dates:
                dates.append(min(shortio_dates))

        first_seen = min(dates) if dates else ""

        rows.append({
            "email": email,
            "name": name,
            "email_domain": domain,
            "is_personal_email": is_personal,
            "is_ghost_member": gm is not None,
            "is_mailerlite_subscriber": ml is not None,
            "is_walker_visitor": is_walker,
            "email_count": gm["email_count"] if gm else 0,
            "email_opened_count": gm["email_opened_count"] if gm else 0,
            "email_open_rate": gm["email_open_rate"] if gm else 0.0,
            "mailerlite_status": ml["status"] if ml else "",
            "mailerlite_subscribed_at": ml["subscribed_at"] if ml else "",
            "first_seen": first_seen,
        })

    rows.sort(key=lambda r: r["email"])
    return rows


def gen_gt_content_performance(linkedin_posts, youtube_videos, ghost_posts):
    """creator__content_performance.csv: one row per content piece."""
    rows = []

    for p in linkedin_posts:
        impressions = p["impressions"]
        engagements = p["reactions"] + p["comments"] + p["shares"]
        rate = round(engagements / impressions * 100, 2) if impressions > 0 else 0.0
        text_len = len(p["text"])
        rows.append({
            "content_id": p["post_id"],
            "platform": "linkedin",
            "title_or_text": p["text"],
            "published_at": p["published_at"],
            "published_month": p["published_at"][:7],
            "impressions_or_views_or_delivered": impressions,
            "engagements": engagements,
            "engagement_rate": rate,
            "performance_tier": _perf_tier(rate),
            "content_length_bucket": _length_bucket(text_len),
        })

    for v in youtube_videos:
        views = v["view_count"]
        engagements = v["like_count"] + v["comment_count"]
        rate = round(engagements / views * 100, 2) if views > 0 else 0.0
        title_len = len(v["title"])
        rows.append({
            "content_id": v["video_id"],
            "platform": "youtube",
            "title_or_text": v["title"],
            "published_at": v["published_at"],
            "published_month": v["published_at"][:7],
            "impressions_or_views_or_delivered": views,
            "engagements": engagements,
            "engagement_rate": rate,
            "performance_tier": _perf_tier(rate),
            "content_length_bucket": _length_bucket(title_len),
        })

    for gp in ghost_posts:
        delivered = gp["email_delivered_count"]
        opened = gp["email_opened_count"]
        rate = round(opened / delivered * 100, 2) if delivered > 0 else 0.0
        rows.append({
            "content_id": gp["post_id"],
            "platform": "ghost",
            "title_or_text": gp["title"],
            "published_at": gp["published_at"],
            "published_month": gp["published_at"][:7],
            "impressions_or_views_or_delivered": delivered,
            "engagements": opened,
            "engagement_rate": rate,
            "performance_tier": _perf_tier(rate),
            "content_length_bucket": _word_count_bucket(gp["word_count"]),
        })

    rows.sort(key=lambda r: (r["content_id"], r["platform"]))
    return rows


def _perf_tier(engagement_rate: float) -> str:
    if engagement_rate >= 8:
        return "viral"
    elif engagement_rate >= 5:
        return "high"
    elif engagement_rate >= 2:
        return "medium"
    else:
        return "low"


def _length_bucket(char_count: int) -> str:
    if char_count < 50:
        return "short"
    elif char_count < 150:
        return "medium"
    else:
        return "long"


def _word_count_bucket(word_count: int) -> str:
    if word_count < 500:
        return "short"
    elif word_count < 1500:
        return "medium"
    else:
        return "long"


def gen_gt_monthly_metrics(linkedin_posts, youtube_videos, ghost_posts,
                           ghost_members, mailerlite_subs, walker_events, shortio_clicks):
    """creator__monthly_metrics.csv: one row per month."""
    # Collect all months
    all_months = set()

    def _month(dt_str):
        return dt_str[:7]

    for p in linkedin_posts:
        all_months.add(_month(p["published_at"]))
    for v in youtube_videos:
        all_months.add(_month(v["published_at"]))
    for gp in ghost_posts:
        all_months.add(_month(gp["published_at"]))
    for gm in ghost_members:
        all_months.add(_month(gm["created_at"]))
    for ml in mailerlite_subs:
        all_months.add(_month(ml["subscribed_at"]))
    for we in walker_events:
        all_months.add(_month(we["timestamp"].replace("T", " ")[:7]))
    for sc in shortio_clicks:
        all_months.add(_month(sc["clicked_at"]))

    rows = []
    for month in sorted(all_months):
        li_posts = [p for p in linkedin_posts if _month(p["published_at"]) == month]
        li_impressions = sum(p["impressions"] for p in li_posts)
        li_engagements = sum(p["reactions"] + p["comments"] + p["shares"] for p in li_posts)

        yt_vids = [v for v in youtube_videos if _month(v["published_at"]) == month]
        yt_views = sum(v["view_count"] for v in yt_vids)

        nl_posts = [gp for gp in ghost_posts if _month(gp["published_at"]) == month]
        nl_delivered = sum(gp["email_delivered_count"] for gp in nl_posts)
        nl_opened = sum(gp["email_opened_count"] for gp in nl_posts)

        new_ghost = len([gm for gm in ghost_members if _month(gm["created_at"]) == month])
        new_ml = len([ml for ml in mailerlite_subs if _month(ml["subscribed_at"]) == month])

        sessions = len(set(
            e["session_id"] for e in walker_events
            if _month(e["timestamp"].replace("T", " ")[:7]) == month
        ))
        clicks = len([sc for sc in shortio_clicks if _month(sc["clicked_at"]) == month])

        rows.append({
            "month": month,
            "linkedin_posts_count": len(li_posts),
            "linkedin_impressions": li_impressions,
            "linkedin_engagements": li_engagements,
            "youtube_videos_count": len(yt_vids),
            "youtube_views": yt_views,
            "newsletter_posts_count": len(nl_posts),
            "newsletter_delivered": nl_delivered,
            "newsletter_opened": nl_opened,
            "new_ghost_members": new_ghost,
            "new_mailerlite_subscribers": new_ml,
            "total_website_sessions": sessions,
            "total_link_clicks": clicks,
        })

    rows.sort(key=lambda r: r["month"])
    return rows


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def write_csv(path, rows, fieldnames=None):
    if not rows:
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {path.name}: {len(rows)} rows, columns={fieldnames}")


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(f"  {path.name}: {len(rows)} rows")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    random.seed(SEED)

    # Generate email pool and assign overlap
    pool = generate_email_pool(280)
    ghost_email_pool, ml_email_pool, walker_email_pool, shortio_email_pool = assign_overlap(pool)

    print("Generating source datasets...")
    linkedin_posts = gen_linkedin_posts(120)
    youtube_videos = gen_youtube_videos(50)
    ghost_members = gen_ghost_members(ghost_email_pool)
    ghost_posts = gen_ghost_posts(60)
    mailerlite_subs = gen_mailerlite(ml_email_pool)
    shortio_clicks = gen_shortio_clicks(shortio_email_pool, 150)
    walker_events = gen_walker_events(walker_email_pool, 300)

    write_csv(DATA_DIR / "authoredup_posts.csv", linkedin_posts)
    write_csv(DATA_DIR / "youtube_videos.csv", youtube_videos)
    write_csv(DATA_DIR / "ghost_member.csv", ghost_members)
    write_csv(DATA_DIR / "ghost_post.csv", ghost_posts)
    write_csv(DATA_DIR / "mailerlite_subscriber.csv", mailerlite_subs)
    write_jsonl(DATA_DIR / "shortio_clicks.jsonl", shortio_clicks)
    write_jsonl(DATA_DIR / "walker_events.jsonl", walker_events)

    # Verify overlap
    ghost_emails_set = {r["email"] for r in ghost_members}
    ml_emails_set = {r["email"] for r in mailerlite_subs}
    walker_emails_set = {r["email"] for r in walker_events}
    shortio_emails_set = {r["email"] for r in shortio_clicks}

    overlap_ml = len(ghost_emails_set & ml_emails_set)
    overlap_walker = len(ghost_emails_set & walker_emails_set)
    overlap_shortio = len(ghost_emails_set & shortio_emails_set)

    print(f"\nEmail overlap (ghost ∩ mailerlite): {overlap_ml}/{len(ghost_emails_set)} = {overlap_ml/len(ghost_emails_set)*100:.0f}%")
    print(f"Email overlap (ghost ∩ walker): {overlap_walker}/{len(ghost_emails_set)} = {overlap_walker/len(ghost_emails_set)*100:.0f}%")
    print(f"Email overlap (ghost ∩ shortio): {overlap_shortio}/{len(ghost_emails_set)} = {overlap_shortio/len(ghost_emails_set)*100:.0f}%")

    print("\nGenerating ground truth...")
    accounts = gen_gt_accounts(ghost_members, mailerlite_subs, walker_events, shortio_clicks)
    content_perf = gen_gt_content_performance(linkedin_posts, youtube_videos, ghost_posts)
    monthly = gen_gt_monthly_metrics(linkedin_posts, youtube_videos, ghost_posts,
                                      ghost_members, mailerlite_subs, walker_events, shortio_clicks)

    write_csv(GT_DIR / "creator__accounts.csv", accounts)
    write_csv(GT_DIR / "creator__content_performance.csv", content_perf)
    write_csv(GT_DIR / "creator__monthly_metrics.csv", monthly)

    print("\nDone!")


if __name__ == "__main__":
    main()
