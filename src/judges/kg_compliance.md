# Knowledge Graph Compliance Judge

Check whether the agent's solution follows the OwnYourTech knowledge graph principles.

## Tier 1 — Core (violations = automatic fail)

- **EU Data Sovereignty**: All data stays under EU jurisdiction. No US-only cloud services for storage/processing.
- **Self-Hosted & Open Source**: Core infra must be OSS and self-hostable. No proprietary SaaS for data pipeline.
- **Local-First**: Don't distribute what doesn't need distributing.

## Tier 2 — Strong Defaults (deviations should be justified)

- Storage: DuckDB (local) or PostgreSQL (shared) — not Snowflake, BigQuery, Redshift
- Ingestion: dlt preferred, custom Python acceptable
- Transformation: dbt-core preferred (not dbt Cloud)
- IaC: Terraform if infra is involved
- Secrets: env vars, never hardcoded

## Tier 3 — Preferences (nice to have)

- Monorepo structure
- dbt naming: stg_, int_, dim_, fct_
- Incremental over full refresh
- Parquet for intermediates

## Anti-Patterns to Flag

- Over-engineering (Kubernetes, Airflow, Docker for simple local tasks)
- Vendor lock-in (proprietary formats, cloud-specific APIs)
- Hardcoded credentials

## Output

Respond with ONLY a JSON object:

```json
{
  "tier1_violations": [],
  "tier2_deviations": [{"default": "...", "actual": "...", "justified": true}],
  "tier3_followed": ["..."],
  "anti_patterns": [],
  "pass": true,
  "summary": "..."
}
```

Set `pass` to `false` if any Tier 1 violation exists.
