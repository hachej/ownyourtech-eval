# Tier 3: Preferences

Recommendations based on experience. The agent suggests these but doesn't push back if the user wants something different. Mention them as "we typically do X" rather than "you must do X."

---

## Project Layout: Monorepo

Keep pipelines, transformations, infrastructure, and orchestration in a single repository.

**Why it works well:**
- Single PR for end-to-end changes (new source + staging model + schedule)
- Shared CI/CD pipeline
- Easier onboarding — one repo to clone, one README to read

---

## Naming Conventions

**dbt models:**
- Staging: `stg_<source>__<entity>` (double underscore separates source from entity)
- Intermediate: `int_<entity>_<verb>` (e.g., `int_orders_joined`)
- Marts: `dim_<entity>`, `fct_<entity>`, or business-name (e.g., `monthly_revenue`)

**Pipeline directories:**
- `pipelines/<source_name>/` — one directory per data source

**Database schemas/zones:**
- `raw_*` or `landing` — untransformed source data
- `staging` — light cleaning, renaming, type casting
- `core` — business entities (dims and facts)
- `analytics` — final reporting models

**Environment prefixes (when applicable):**
- `dev_`, `stg_`, `prod_` for environment-specific resources

---

## Incremental Over Full Refresh

Prefer incremental loading when the source supports reliable cursors (timestamps, sequence IDs).

**Use full refresh when:**
- No reliable cursor exists
- Data mutates unpredictably (e.g., retroactive edits)
- Dataset is small enough that full refresh completes quickly (< 100k rows)

---

## Intermediate Format: Parquet

When an intermediate file format is needed between extraction and loading, use Parquet.

**Why:**
- Columnar, compressed, self-describing schema
- Native support in DuckDB, dbt, pandas, polars, dlt
- Efficient for analytical query patterns

---

## Git Workflow

- Private repositories by default
- Branch protection on main
- `.gitignore` covers: `.env`, `*.duckdb`, `*.duckdb.wal`, `terraform.tfstate*`, `terraform.tfvars`, `__pycache__/`, `.dlt/pipeline_data/`

---

## Event Collection: Buz

When behavioral/event data collection is needed, use Buz (open-source event collector).

**When it's relevant:**
- Product analytics, clickstream, or custom event tracking
- Need schema validation on incoming events
- Want to own the collection infrastructure

**When it's not needed:**
- Pure API-based data extraction (use dlt instead)
- No behavioral data requirements
