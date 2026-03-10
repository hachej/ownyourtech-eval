# Pattern: Early-Stage Data Stack (Pre-revenue / < $1M ARR)

## Design Intent

Minimal, local-first setup for a solo analyst or small team. Everything runs on one machine or one small VM. No distributed systems, no containers, no orchestration platforms. Cost near zero.

## Reference Architecture

```
Source APIs ──→ dlt (Python) ──→ Parquet/DuckDB ──→ dbt-core ──→ DuckDB (analytics)
                                                                        │
                                                              SQL queries / exports
```

## Key Characteristics

- **Compute:** Local machine or single Hetzner cx22 (~€4/mo)
- **Ingestion:** dlt writing to local files or DuckDB directly
- **Storage:** DuckDB (single file, zero ops)
- **Transformation:** dbt-core with dbt-duckdb adapter
- **Orchestration:** `run.sh` executed manually or via cron
- **Monitoring:** Validation queries in the run script. If they fail, the script fails.

## Project Structure

```
project-root/
├── pipelines/              # dlt pipelines, one directory per source
│   └── <source_name>/
├── transform/              # dbt project
│   ├── models/
│   │   ├── staging/        # 1:1 with source tables
│   │   └── marts/          # Business metrics
│   ├── tests/
│   └── dbt_project.yml
├── warehouse/              # DuckDB database file lives here
├── .env                    # Secrets (never committed)
├── .env.example            # Reference for required secrets
├── .gitignore
├── requirements.txt        # Python dependencies
└── run.sh                  # Single entry point: extract → transform → validate
```

## What's Intentionally Missing

- No Docker — unnecessary complexity for local tooling
- No CI/CD — deploy by running the script
- No orchestration platform — cron or manual execution
- No dashboarding tool — SQL queries are sufficient at this stage
- No separate staging/production environments — one environment is enough
- No infrastructure as code — no infrastructure to manage (it's local)

## When to Outgrow This Pattern

Signals that you need the growth-stage pattern:
- A second person needs to run queries against the same data
- Data volume exceeds what fits in memory (~8-16GB on a typical machine)
- You need always-on access to the data (not just when your laptop is open)
- Pipelines need to run reliably without human intervention
