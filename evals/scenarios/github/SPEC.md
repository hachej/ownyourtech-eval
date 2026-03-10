# GitHub ELT Pipeline

## Objective

Build an ELT pipeline that extracts GitHub data from multiple sources,
loads it into a destination database, and transforms it into analytics models.

## Source Data

Data is spread across 5 source types. All sources are local.

### Postgres (`localhost:5433`, database `github`, user `postgres`, password `testelt`)

| Table | Description |
|-------|-------------|
| `issue` | GitHub issues: id, body, state, timestamps, user_id, repository_id |
| `issue_closed_history` | History of issue close/reopen events |
| `pull_request` | Pull request metadata: head/base refs, merge commit |
| `users` | GitHub users: login, name, company, type |

### MongoDB (`mongodb://localhost:27017`, database `github`)

| Collection | Description |
|------------|-------------|
| `issue_comment` | Comments on issues |
| `label` | Label definitions (name, color, description) |
| `pull_request_review` | PR reviews (state, submitted_at, user_id) |
| `team` | Team definitions (name, description, privacy) |

### REST API (`http://localhost:5055`)

| Endpoint | Description |
|----------|-------------|
| `GET /github/issue_assignee` | Issue-to-user assignments |
| `GET /github/issue_merged` | Merge events (issue_id, merged_at) |
| `GET /github/repository` | Repository metadata (name, created_at, private) |

### S3 (`http://localhost:4566`, bucket `github-bucket`)

| Object | Description |
|--------|-------------|
| `repo_team.jsonl` | Repository-to-team mappings |

S3 credentials: `AWS_ACCESS_KEY_ID=test`, `AWS_SECRET_ACCESS_KEY=test`, region `us-west-2`.

### Flat Files (in `data/github/` directory)

| File | Description |
|------|-------------|
| `requested_reviewer_history.csv` | PR reviewer request history |
| `issue_label.csv` | Issue-to-label mappings |

## Expected Output Models

Transform the source data into these 6 models. Store in a queryable database (Snowflake, DuckDB, Postgres — your choice).

### `github__issues`

Enriched issue view with computed fields.

| Column | Description |
|--------|-------------|
| `issue_id` | Unique issue ID |
| `body` | Issue description text |
| `closed_at` | When closed (null if open) |
| `created_at` | When created |
| `is_locked` | Boolean: is the issue locked |
| `issue_number` | Number within repository |
| `is_pull_request` | Boolean: is this a PR |
| `repository_id` | FK to repository |
| `state` | open/closed |
| `title` | Issue title |
| `updated_at` | Last update timestamp |
| `user_id` | FK to creating user |
| `number_of_times_reopened` | Count of reopen events from issue_closed_history |
| `number_of_comments` | Count of comments from issue_comment |
| `repository` | Repository full name (joined from repository table) |
| `repository_team_names` | Aggregated team names for the repository |
| `creator_login_name` | User login (joined from users) |
| `creator_name` | User name (joined from users) |
| `creator_company` | User company (joined from users) |

### `github__pull_requests`

Enriched PR view with review info and merge timing.

| Column | Description |
|--------|-------------|
| `issue_id` | Unique issue ID (PRs are issues) |
| `body` | PR description text |
| `closed_at` | When closed (null if open) |
| `created_at` | When created |
| `is_locked` | Boolean |
| `issue_number` | Number within repository |
| `is_pull_request` | Boolean (always true) |
| `repository_id` | FK to repository |
| `state` | open/closed |
| `title` | PR title |
| `updated_at` | Last update timestamp |
| `user_id` | FK to creating user |
| `number_of_times_reopened` | Count of reopen events |
| `number_of_comments` | Count of comments |
| `repository` | Repository full name |
| `repository_team_names` | Aggregated team names |
| `creator_login_name` | User login |
| `creator_name` | User name |
| `creator_company` | User company |
| `merged_at` | When merged (null if not merged) |
| `reviewers` | List of reviewer login names |
| `number_of_reviews` | Count of reviews |

### `github__daily_metrics`

One row per repository per day. Counts set to 0 when no activity.

| Column | Description |
|--------|-------------|
| `day` | The reporting day |
| `repository` | Repository full name |
| `number_issues_opened` | Issues created this day (0 if none) |
| `number_issues_closed` | Issues closed this day (0 if none) |
| `number_prs_opened` | PRs created this day (0 if none) |
| `number_prs_merged` | PRs merged this day (0 if none) |
| `number_prs_closed_without_merge` | PRs closed without merge (0 if none) |

### `github__weekly_metrics`

Same structure, aggregated by week.

| Column | Description |
|--------|-------------|
| `week` | The reporting week |
| `repository` | Repository full name |
| `total_number_issues_opened` | Issues created this week (0 if none) |
| `total_number_issues_closed` | Issues closed this week (0 if none) |
| `total_number_prs_opened` | PRs created this week (0 if none) |
| `total_number_prs_merged` | PRs merged this week (0 if none) |
| `number_prs_closed_without_merge` | PRs closed without merge (0 if none) |

### `github__monthly_metrics`

Same structure, aggregated by month.

### `github__quarterly_metrics`

Same structure, aggregated by quarter.

## Deliverable

1. All code in a `stack/` directory
2. A runnable pipeline that extracts from all 5 source types, transforms into the 6 models above, loads into a queryable destination, and exits 0 on success
3. A `report.md` documenting your architecture, technology choices, and entry point

## Constraints

- Everything runs locally
- Keep it simple — no Docker, no orchestration
- All pipeline code goes in `stack/`
- Flat files are at `data/github/` relative to the working directory
