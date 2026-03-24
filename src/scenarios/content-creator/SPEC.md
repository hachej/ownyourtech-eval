# Content Creator Analytics

## Objective

Help a solo content creator understand their audience and content performance.
Read `persona.yaml` to learn who they are and what tools they use, then build
a local analytics stack that extracts data from their platforms, resolves
identities, and produces models they can explore.

## Discovery

Start by reading `persona.yaml`. It tells you which platforms the creator uses
and how data is accessed. Your environment has API credentials for each platform
(check your environment variables). Connect to each API, extract the data, and
build the models below.

## Expected Output Models

Build these 3 models from the extracted data. Store in a local queryable
database (choose one using `oyt kg evaluate`).

### `creator__accounts`

One row per unique person, identity resolved across sources via email.

| Column | Description |
|--------|-------------|
| `email` | Unique email address (the identity key) |
| `name` | Name if available from any source (null otherwise) |
| `email_domain` | Domain part of email |
| `is_personal_email` | Boolean: true for gmail, yahoo, hotmail, outlook, etc. |
| `is_ghost_member` | Boolean: appears in Ghost members |
| `is_mailerlite_subscriber` | Boolean: appears in MailerLite subscribers |
| `email_count` | Emails sent (from Ghost, 0 if not a member) |
| `email_opened_count` | Emails opened (from Ghost, 0 if not a member) |
| `email_open_rate` | Open rate (from Ghost, 0.0 if not a member) |
| `mailerlite_status` | Subscriber status from MailerLite (null if not a subscriber) |
| `mailerlite_subscribed_at` | When they subscribed in MailerLite (null if not a subscriber) |
| `first_seen` | Earliest date this person appears across all sources |

### `creator__content_performance`

One row per content piece across platforms.

| Column | Description |
|--------|-------------|
| `content_id` | Unique ID of the content piece |
| `platform` | `linkedin` or `newsletter` |
| `title_or_text` | Title (newsletter) or text (linkedin) |
| `published_at` | Publication timestamp |
| `published_month` | YYYY-MM format |
| `impressions_or_delivered` | Impressions (linkedin) or emails delivered (newsletter) |
| `engagements` | reactions+comments+shares (linkedin) or emails opened (newsletter) |
| `engagement_rate` | engagements / impressions_or_delivered |
| `performance_tier` | `viral` / `high` / `medium` / `low` based on engagement or reach |
| `content_length_bucket` | For linkedin: `short` / `medium` / `long` based on text length. Null for newsletter |

### `creator__monthly_metrics`

One row per month.

| Column | Description |
|--------|-------------|
| `month` | YYYY-MM format |
| `linkedin_posts_count` | Posts published that month |
| `linkedin_impressions` | Sum of impressions |
| `linkedin_engagements` | Sum of reactions+comments+shares |
| `newsletter_posts_count` | Newsletter issues sent that month |
| `newsletter_delivered` | Sum of emails delivered |
| `newsletter_opened` | Sum of emails opened |
| `new_ghost_members` | Ghost members with created_at in that month |
| `new_mailerlite_subscribers` | MailerLite subscribers with subscribed_at in that month |

## BI Tool

Connect a BI tool so the creator can explore these models interactively.
The tool must run locally. Choose the tool using `oyt kg evaluate`.

## Deliverable

1. All code in a `stack/` directory
2. A runnable pipeline that extracts from the creator's platforms, transforms into the 3 models above, loads into a queryable destination, and exits 0 on success
3. A `report.md` documenting your architecture, technology choices, and entry point
4. A locally accessible BI tool connected to the output models

## Constraints

- Everything runs locally
- Keep it simple — no Docker, no orchestration
- All pipeline code goes in `stack/`
