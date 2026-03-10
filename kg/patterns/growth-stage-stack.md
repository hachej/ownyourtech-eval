# Pattern: Growth-Stage Data Stack ($1M-$10M ARR)

## Design Intent

Server-hosted, multi-user setup. Reliable daily pipelines, shared warehouse, infrastructure as code. Still simple — one server, one database, one orchestration method. Complexity budget stays low.

## Reference Architecture

```
Source APIs ──→ dlt ──→ Object Storage (Parquet) ──→ dbt-core ──→ PostgreSQL
                              │                                       │
                        Landing zone                          Shared queries
                        (archival)                            BI tool (Metabase)
```

## Key Characteristics

- **Compute:** Hetzner Cloud VM (cx22-cx42 depending on volume, ~€4-20/mo)
- **Ingestion:** dlt writing to Hetzner Object Storage (landing) and PostgreSQL
- **Storage:** PostgreSQL as shared warehouse, Object Storage as archive
- **Transformation:** dbt-core with dbt-postgres adapter
- **Orchestration:** Cron on the server, calling `run.sh`
- **Infrastructure:** Terraform-managed Hetzner resources
- **CI/CD:** GitHub Actions for Terraform plan/apply
- **Monitoring:** dbt tests, cron email on failure, basic alerting

## Project Structure

```
project-root/
├── terraform/              # Infrastructure as code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── pipelines/              # dlt pipelines
│   └── <source_name>/
├── transform/              # dbt project
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/   # Optional, add when needed
│   │   └── marts/
│   ├── tests/
│   └── dbt_project.yml
├── .github/
│   └── workflows/          # CI/CD for Terraform
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── run.sh
```

## What's Added From Early-Stage

- Infrastructure as code (Terraform + Hetzner)
- Object storage for raw data archival
- PostgreSQL replaces DuckDB for shared access
- CI/CD for infrastructure changes
- Git repository with branch protection

## What's Still Intentionally Missing

- No Kubernetes — a single VM is sufficient
- No orchestration platform — cron handles daily schedules
- No microservices — monorepo, monolith, one deploy target
- No data catalog — dbt docs serve this purpose
- No separate staging environment — add when team exceeds ~5 people

## When to Outgrow This Pattern

- Pipeline DAGs become complex (10+ interdependent jobs)
- Need for real-time data (streaming, not batch)
- Multiple teams owning different parts of the data platform
- Compliance requires environment separation (staging/production)
