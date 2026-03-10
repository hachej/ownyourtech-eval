# Solution Catalog: Orchestration & Scheduling

## Orchestration Tools

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **Cron** | Strong Default | Zero dependencies, available everywhere. Sufficient for daily/hourly batch. |
| **Shell script (run.sh)** | Strong Default | Single entry point that chains extract → transform → validate. Cron calls this. |
| **Dagster (self-hosted)** | Acceptable | When DAG complexity exceeds cron: multi-step dependencies, backfills, retries, observability. |
| **Prefect (self-hosted)** | Acceptable | Similar to Dagster. Team preference drives the choice between them. |
| **Airflow** | Avoid | Operationally heavy, complex deployment. Usually overkill for data teams < 10 people. |
| **Managed orchestrators** | Reject | Cloud-hosted orchestration violates self-hosted principle. |

## When to Graduate From Cron

Stay with cron until you experience at least 2 of these:
- Jobs have complex inter-dependencies (A must finish before B starts)
- You need automated retries with backoff on failure
- Multiple teams own different pipelines and need coordination
- You need historical backfill capabilities
- Pipeline observability (run history, duration trends, alerting) becomes critical

If you're asking "do I need Dagster?" — you don't. When you need it, you'll know.

## Run Script Pattern

Every project should have a single `run.sh` entry point that:
1. Runs extraction (dlt pipelines)
2. Runs transformation (dbt run)
3. Runs validation (dbt test or custom queries)
4. Exits with non-zero status on any failure

This script is what cron invokes. It's also what a developer runs manually. One entry point, same behavior everywhere.

## Scheduling Guidance

| Frequency | When |
|-----------|------|
| **Daily (early morning)** | Most analytics workloads. Run before the team's workday starts. |
| **Hourly** | When near-real-time freshness matters but true streaming isn't needed. |
| **On-demand (manual)** | Development, ad-hoc analysis, initial loads. |
| **More than hourly** | Probably need streaming, not batch. Re-evaluate architecture. |
