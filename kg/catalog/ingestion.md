# Solution Catalog: Data Ingestion

## Ingestion Frameworks

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **dlt** | Strong Default | Python-native ELT. 100+ connectors. Schema inference, incremental loading, state management. No separate runtime. |
| **Custom Python** | Acceptable | When no dlt connector exists, source API is exotic, or requires websockets/streaming. |
| **Airbyte (self-hosted)** | Acceptable | When team prefers UI-based connector management. Must be self-hosted — Airbyte Cloud violates Tier 1. |
| **Fivetran** | Reject | Proprietary SaaS, data transits US infrastructure. Violates Tier 1. |
| **Stitch** | Reject | Same as Fivetran. |
| **Meltano** | Acceptable | When Singer ecosystem connectors are needed. More operational overhead than dlt. |

## Choosing an Ingestion Approach

Decision heuristic (in order):

1. Does dlt have a verified connector for this source? → Use dlt
2. Does dlt have a community connector? → Try it, fall back to custom if quality is insufficient
3. Is the source a standard REST API with pagination? → Use dlt's REST API generic source
4. Is the source exotic (websockets, binary protocols, complex auth)? → Custom Python
5. Does the team already run Airbyte and want to add a connector there? → Airbyte is acceptable

## Loading Strategies

| Strategy | When to use |
|----------|------------|
| **Full refresh** | Small datasets (< 100k rows), no reliable cursor, data mutates retroactively, getting started quickly |
| **Incremental (append)** | Source has timestamps/sequence IDs, event data, append-only patterns |
| **Incremental (merge)** | Source has timestamps AND records get updated, need to maintain current state |

Default to full refresh when starting. Graduate to incremental when volume demands it or when the source naturally supports cursors.

## Quality Bar for Pipelines

- Every pipeline must be idempotent (safe to re-run without duplicating data)
- Must write to raw/landing zone first, never directly to marts
- Credentials in `.env`, never hardcoded
- Must log enough to debug failures (source, row counts, timestamps)
- Pipeline failure must not corrupt existing data
