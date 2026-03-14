# Content Creator Analytics Pipeline

## Objective

Build an ELT pipeline that extracts data from 7 sources describing a solo content creator's
online presence — newsletter (Ghost), email marketing (MailerLite), LinkedIn posts,
YouTube videos, website analytics (Walker.js), and link tracking (Short.io).

Resolve identities across sources using email, normalize content metrics across platforms,
aggregate monthly KPIs, and connect a local BI tool so the creator can explore the models
interactively.

## Source Data

Data is spread across 5 source types. All sources are local.

### Postgres (`localhost:5433`, database `content_creator`, user `postgres`, password `testelt`)

| Table | Description |
|-------|-------------|
| `ghost_member` | Newsletter subscribers: email, name, status, created_at, email_count, email_opened_count, email_open_rate |
| `ghost_post` | Newsletter posts: post_id, title, slug, published_at, word_count, email_delivered_count, email_opened_count |

### MongoDB (`mongodb://localhost:27017`, database `content_creator`)

| Collection | Description |
|------------|-------------|
| `mailerlite_subscriber` | Email marketing subscribers: email, status, groups, subscribed_at |

### REST API (`http://localhost:5055`)

| Endpoint | Description |
|----------|-------------|
| `GET /content-creator/youtube_videos` | YouTube video stats: video_id, title, view_count, like_count, comment_count, published_at |

### S3 (`http://localhost:4566`, bucket `content-creator-bucket`)

| Object | Description |
|--------|-------------|
| `shortio_clicks.jsonl` | Link click tracking: clicked_at, utm_source, utm_medium, utm_campaign, email |
| `walker_events.jsonl` | Website analytics events: session_id, timestamp, event_name, page_path, email |

S3 credentials: `AWS_ACCESS_KEY_ID=test`, `AWS_SECRET_ACCESS_KEY=test`, region `us-west-2`.

### Flat Files (in `data/content-creator/` directory)

| File | Description |
|------|-------------|
| `authoredup_posts.csv` | LinkedIn posts from AuthoredUp: post_id, text, impressions, reactions, comments, shares, published_at |

## Expected Output Models

Transform the source data into these 3 models. Store in a queryable database (DuckDB, Postgres — your choice).

### `creator__accounts`

One row per unique person, identity resolved across sources via email.

| Column | Description |
|--------|-------------|
| `email` | Unique email address (the identity key) |
| `name` | From ghost_member (null if only in other sources) |
| `email_domain` | Domain part of email (e.g. `gmail.com`) |
| `is_personal_email` | Boolean: true for gmail, yahoo, hotmail, outlook, etc. |
| `is_ghost_member` | Boolean: appears in ghost_member |
| `is_mailerlite_subscriber` | Boolean: appears in mailerlite_subscriber |
| `is_walker_visitor` | Boolean: appears in walker_events |
| `email_count` | From ghost_member (0 if not a member) |
| `email_opened_count` | From ghost_member (0 if not a member) |
| `email_open_rate` | From ghost_member (0.0 if not a member) |
| `mailerlite_status` | From mailerlite_subscriber (null if not a subscriber) |
| `mailerlite_subscribed_at` | From mailerlite_subscriber (null if not a subscriber) |
| `first_seen` | Earliest date this person appears across all sources |

### `creator__content_performance`

One row per content piece across platforms.

| Column | Description |
|--------|-------------|
| `content_id` | post_id or video_id |
| `platform` | `linkedin`, `youtube`, or `ghost` |
| `title_or_text` | Title (ghost, youtube) or text (linkedin) of the content |
| `published_at` | Publication timestamp |
| `published_month` | YYYY-MM format |
| `impressions_or_views_or_delivered` | Impressions (linkedin), views (youtube), or email_delivered (ghost) |
| `engagements` | reactions+comments+shares (linkedin), likes+comments (youtube), email_opened (ghost) |
| `engagement_rate` | engagements / impressions_or_views_or_delivered, as a percentage |
| `performance_tier` | `viral` / `high` / `medium` / `low` based on engagement_rate |
| `content_length_bucket` | For linkedin: `short` / `medium` / `long` based on text length. Null for others |

### `creator__monthly_metrics`

One row per month.

| Column | Description |
|--------|-------------|
| `month` | YYYY-MM format |
| `linkedin_posts_count` | Count of linkedin posts published that month |
| `linkedin_impressions` | Sum of impressions |
| `linkedin_engagements` | Sum of reactions+comments+shares |
| `youtube_videos_count` | Count of youtube videos published that month |
| `youtube_views` | Sum of views |
| `newsletter_posts_count` | Count of ghost posts published that month |
| `newsletter_delivered` | Sum of email_delivered_count |
| `newsletter_opened` | Sum of email_opened_count |
| `new_ghost_members` | Ghost members with created_at in that month |
| `new_mailerlite_subscribers` | MailerLite subscribers with subscribed_at in that month |
| `total_website_sessions` | Count of unique session_ids from walker_events in that month |
| `total_link_clicks` | Count of shortio_clicks in that month |

## BI Tool

Connect a BI tool so the creator can explore these models interactively.
The tool must run locally. Choose the tool using `oyt kg evaluate`.

## Deliverable

1. All code in a `stack/` directory
2. A runnable pipeline that extracts from all 5 source types, transforms into the 3 models above, loads into a queryable destination, and exits 0 on success
3. A `report.md` documenting your architecture, technology choices, and entry point
4. A locally accessible BI tool connected to the output models

## Constraints

- Everything runs locally
- Keep it simple — no Docker, no orchestration
- All pipeline code goes in `stack/`
- Flat files are at `data/content-creator/` relative to the working directory
