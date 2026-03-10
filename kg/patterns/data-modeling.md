# Pattern: Data Modeling for Analytics

## Model Types — Use the Right Name

The `fct_` and `dim_` prefixes have specific meanings. Don't use them loosely.

**Facts (`fct_`)** record business events at their natural grain. One row = one event that happened.
- `fct_commits` — one row per commit
- `fct_page_views` — one row per page view
- `fct_orders` — one row per order

**Dimensions (`dim_`)** describe entities that facts reference. Slowly changing or mostly static.
- `dim_repositories` — one row per repo
- `dim_users` — one row per user
- `dim_products` — one row per product

**Metric models** aggregate facts into business-meaningful summaries. They are NOT fact tables. Name them for what they describe, not with `fct_` prefix.
- `daily_repo_metrics` — one row per repo per day, all activity metrics
- `repo_health_snapshot` — one row per repo, latest health indicators
- `monthly_revenue` — one row per month, revenue aggregations

## One Mart Model at the Right Grain, Not Many Narrow Ones

A common anti-pattern is splitting metrics across many mart tables by topic (one for activity, one for responsiveness, one for health). This creates:
- Unnecessary joins for consumers who need multiple metrics
- Redundant date spines and repo dimensions
- Maintenance overhead when the grain changes

**The better approach:** identify the grain, then put all metrics at that grain into one model.

Ask: "What is the natural reporting grain?" Usually it's:
- **Per entity per time period** (e.g., per repo per day)
- **Per entity snapshot** (e.g., per repo, latest values)

If all your metrics share the same grain (repo × day), they belong in one model. If some metrics have a different grain (e.g., per contributor), that's a separate model.

### Example: Repository Analytics

Instead of:
```
fct_daily_activity.sql      — repo × day, activity counts
fct_rolling_activity.sql    — repo × day, 30-day rolling counts
fct_responsiveness.sql      — repo × day, cohort response times
fct_health_indicators.sql   — repo × day, bus factor + Gini
```

Build:
```
daily_repo_metrics.sql      — repo × day, ALL metrics in one model
```

One model, one grain, all metrics. Window functions and cohort calculations happen inside the model via CTEs. The consumer gets one table to query.

If some metrics are expensive to compute and have a different refresh cadence, consider a separate snapshot model:
```
daily_repo_metrics.sql      — repo × day, activity + rolling + responsiveness
repo_health_snapshot.sql    — repo, latest health indicators (bus factor, Gini)
```

But only split when there's a real reason (different grain, different refresh needs, different consumers).

## Staging Models Are Not Optional

Even when the source data is clean, staging models serve as a contract between raw data and your metrics:
- Rename columns to your conventions (no `_dlt_id` leaking into marts)
- Cast timestamps consistently
- Document the schema in YAML
- Add primary key tests

A metric model should only reference `ref('stg_...')`, never `source(...)` directly.

## Aggregation Patterns

### Rolling Windows
Use DuckDB's `RANGE BETWEEN INTERVAL` for true calendar-based windows:
```sql
SUM(commits) OVER (
    PARTITION BY repo
    ORDER BY activity_date
    RANGE BETWEEN INTERVAL '29 days' PRECEDING AND CURRENT ROW
)
```
This gives correct 30-day windows regardless of missing dates.

### Cohort Analysis
Define the cohort, then measure outcomes:
```sql
-- Cohort: PRs created in trailing 30 days
-- Metric: time to merge, resolution rate
```
The cohort window and the measurement are separate concerns. Don't conflate them.

### Concentration Metrics (Gini, HHI)
These measure inequality of distribution. Compute them over a fixed trailing window (e.g., 90 days) to smooth noise. A single week can have extreme concentration that doesn't reflect the real pattern.

## When to Add Intermediate Models

Add an intermediate layer only when:
- The same CTE appears in 3+ mart models (DRY violation)
- A business concept needs a consistent definition across models (e.g., "active contributor")
- The mart model SQL exceeds ~150 lines and readability suffers

For a typical analytics pipeline with 1-2 mart models, you don't need intermediate models. Start without them.
