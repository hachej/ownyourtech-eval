# Tier 2: Strong Defaults

These are the opinionated choices that define "boring data." The agent follows them unless the user has a specific, articulated reason to deviate. If the user wants to deviate, acknowledge the default, explain why it's preferred, and proceed only after the user confirms.

---

## Infrastructure: Hetzner

Default cloud provider is Hetzner (German company, Nuremberg HQ).

**Why over alternatives:**
- Native GDPR compliance (German jurisdiction, no CLOUD Act exposure)
- Dramatically lower cost than hyperscalers (~€4-8/mo for a capable VM vs ~$50+ on AWS)
- Simple, predictable pricing without the labyrinth of SKUs
- Sufficient for data workloads up to mid-stage companies

**When to consider alternatives:**
- OVH — when French jurisdiction is specifically required
- Scaleway — when GPU workloads are needed
- Never AWS/GCP/Azure (Tier 1 violation)

---

## Ingestion: dlt

Default ingestion framework is dlt (data load tool).

**Why over alternatives:**
- Python-native, no separate runtime or service to manage
- 100+ verified connectors covering most common SaaS sources
- Schema inference and evolution handled automatically
- Supports incremental loading with state management
- Can target multiple destinations (parquet files, databases, object storage)

**When to consider alternatives:**
- Custom Python scripts — when source has no dlt connector and API is exotic
- Airbyte (self-hosted) — when team strongly prefers UI-based connector management
- Never Fivetran/Stitch (Tier 1 violation)

---

## Storage: DuckDB for Local, PostgreSQL for Shared

Default analytical database depends on access patterns.

**DuckDB when:**
- Single user / single machine
- Local development and exploration
- Data volume under ~100GB
- No concurrent write access needed

**PostgreSQL when:**
- Multiple users need concurrent access
- Data serves a live application or API
- Persistent, always-on service is needed
- Data volume over 100GB

**Why these over alternatives:**
- Both are open source and self-hostable
- DuckDB is embedded (zero-ops) and columnar (fast analytics)
- PostgreSQL is the most battle-tested open-source database
- Never Snowflake/BigQuery/Redshift (Tier 1 violation)

---

## Transformation: dbt-core

Default transformation framework is dbt-core (not dbt Cloud).

**Why:**
- SQL-based transformations are accessible to analysts and engineers
- Built-in testing, documentation, and lineage
- dbt-core is fully open source and runs locally
- Mature ecosystem of packages and community patterns

**Never dbt Cloud** (violates self-hosted principle).

---

## Orchestration: Cron

Default scheduler is cron for early-stage setups.

**Why over alternatives:**
- Zero dependencies, available on every Unix system
- Sufficient for daily/hourly batch jobs
- No additional service to monitor, update, or debug
- When your orchestration needs grow beyond cron, you'll know — and it won't be now

**When to graduate from cron:**
- Complex DAG dependencies between jobs
- Need for backfills, retries with exponential backoff
- Multiple teams coordinating pipeline schedules
- At that point, consider Dagster or Prefect (self-hosted)

---

## Infrastructure as Code: Terraform

All infrastructure must be managed via Terraform.

**Why:**
- Reproducible, version-controlled infrastructure
- Plan before apply — review changes before they happen
- Team collaboration through shared state
- No click-ops, no snowflake servers

---

## Secrets: Never in Code

Secrets live in environment variables or `.env` files, never committed to version control.

**Pattern:**
- `.env` for local development (always in `.gitignore`)
- `.env.example` committed as reference (with placeholder values)
- CI/CD secrets managed through platform's secret store (e.g., GitHub Secrets)
