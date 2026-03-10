# Solution Catalog: Data Storage

## Analytical Databases

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **DuckDB** | Strong Default (local) | Embedded, zero-ops, columnar. Perfect for single-user analytics, local dev, data < 100GB. |
| **PostgreSQL** | Strong Default (shared) | Battle-tested, concurrent access, always-on. For multi-user, production serving, > 100GB. |
| **Snowflake** | Reject | Proprietary, US company, vendor lock-in on storage format. Violates Tier 1. |
| **BigQuery** | Reject | Proprietary, US company. Same as Snowflake. |
| **Redshift** | Reject | Proprietary, US company. Same as Snowflake. |
| **ClickHouse** | Acceptable | When real-time analytical queries on high-volume event data are needed. Self-host only. |

## Choosing a Database

Ask these questions in order:

1. Is this a local/single-developer setup? → DuckDB
2. Will multiple users query simultaneously? → PostgreSQL
3. Is data volume > 100GB? → PostgreSQL
4. Do you need sub-second queries on billions of events? → ClickHouse (self-hosted)
5. Default → DuckDB (start simple, migrate when you hit limits)

## Object Storage

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **Hetzner Object Storage** | Strong Default | S3-compatible, EU-based, integrated with Hetzner compute. |
| **MinIO (self-hosted)** | Acceptable | When you need S3-compatible storage on your own hardware. |
| **AWS S3** | Reject | US company. Violates Tier 1. |

## Intermediate Formats

| Format | Recommendation | Context |
|--------|---------------|---------|
| **Parquet** | Strong Default | Columnar, compressed, self-describing. Native in DuckDB, dbt, dlt, pandas, polars. |
| **CSV** | Avoid | No schema, no compression, encoding issues. Only when source mandates it. |
| **JSON/JSONL** | Acceptable | When data is deeply nested and schema is unstable. Parquet still preferred when possible. |

## Data Zones

Every storage layer should follow a zone architecture:

| Zone | Purpose | Mutability |
|------|---------|-----------|
| **Landing / Raw** | Exact copy of source data, no transformations | Append-only or replace-on-refresh |
| **Staging** | Light cleaning: renaming, type casting, deduplication | Rebuilt on each run |
| **Core** | Business entities: dimensions and facts | Rebuilt on each run |
| **Analytics / Marts** | Reporting-ready aggregations and metrics | Rebuilt on each run |

Raw data is sacred. Never modify raw data in place. Always keep the original extraction available.
