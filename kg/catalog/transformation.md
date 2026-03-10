# Solution Catalog: Data Transformation

## Transformation Frameworks

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **dbt-core** | Strong Default | SQL-based, open source, testing + docs built in. Runs locally. |
| **dbt Cloud** | Reject | Proprietary SaaS. Violates self-hosted principle. Use dbt-core. |
| **SQLMesh** | Acceptable | When team needs native column-level lineage or virtual environments. More complex than dbt. |
| **Plain SQL scripts** | Acceptable | When transformations are trivial (< 5 models) and dbt overhead isn't justified. |

## dbt Model Layers

| Layer | Purpose | Naming | Materialization |
|-------|---------|--------|----------------|
| **Staging** | 1:1 with source tables. Rename, cast, deduplicate. | `stg_<source>__<entity>` | View (default) |
| **Intermediate** | Joins, business logic that serves multiple marts. | `int_<entity>_<verb>` | View or ephemeral |
| **Marts** | Business-facing metrics and entities. | `fct_<event>` for event facts, `dim_<entity>` for dimensions, or **business name for metric models** (e.g. `daily_repo_metrics`). See `patterns/data-modeling.md`. | Table |

## dbt Adapter Selection

| Adapter | When |
|---------|------|
| **dbt-duckdb** | Local analytics, single-user, file-based warehouse |
| **dbt-postgres** | Shared warehouse, production serving, multi-user |

## Quality Bar for Transformations

- Every staging model has a `unique` and `not_null` test on its primary key
- Marts have documentation (description in schema.yml)
- Models must compile and pass tests before being considered done
- Use `ref()` for all model references — never hardcode table names
- Use `source()` for all raw data references

## When to Add an Intermediate Layer

The intermediate layer is optional. Add it when:
- The same join or filter appears in 3+ mart models (DRY)
- A business concept (e.g., "active user") needs a consistent definition
- Mart queries become too complex to read

Don't add it preemptively. Start with staging → marts. Refactor to intermediate when duplication appears.
