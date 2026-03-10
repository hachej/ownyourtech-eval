# Pattern: Project Structure & Conventions

## Directory Layout Principles

- One repository for the entire data stack (monorepo)
- Clear separation: pipelines / transformations / infrastructure / orchestration
- Each data source gets its own directory under `pipelines/`
- dbt project lives in `transform/` (not root-level)
- Infrastructure code in `terraform/` (when applicable)

## File Hygiene

### Always present:
- `run.sh` — single entry point, idempotent, chains all steps
- `.env.example` — documents required environment variables
- `.gitignore` — covers secrets, database files, cache directories
- `requirements.txt` or `pyproject.toml` — pinned Python dependencies

### .gitignore essentials:
```
.env
*.duckdb
*.duckdb.wal
terraform.tfstate*
terraform.tfvars
__pycache__/
.dlt/pipeline_data/
target/          # dbt build artifacts
dbt_packages/    # dbt dependencies
logs/
```

## dbt Project Conventions

### Model organization:
```
transform/models/
├── staging/
│   ├── <source_a>/
│   │   ├── stg_<source_a>__<entity_1>.sql
│   │   ├── stg_<source_a>__<entity_2>.sql
│   │   └── _<source_a>__sources.yml
│   └── <source_b>/
│       └── ...
├── intermediate/           # Optional layer
│   └── int_<entity>_<verb>.sql
└── marts/
    ├── fct_<entity>.sql
    ├── dim_<entity>.sql
    └── _marts__models.yml
```

### Schema files:
- One `_<source>__sources.yml` per source in staging (defines source tables)
- One `_<directory>__models.yml` per directory (documents models and tests)
- Prefix with underscore so they sort to top

### Materialization defaults:
- Staging: `view` (lightweight, always fresh)
- Intermediate: `view` or `ephemeral` (no physical table unless performance demands)
- Marts: `table` (materialized for query performance)

## Pipeline Conventions

### One pipeline, one directory:
```
pipelines/
├── github/
│   ├── __init__.py
│   ├── pipeline.py         # dlt pipeline definition
│   └── README.md           # Source-specific notes (optional)
├── stripe/
│   └── pipeline.py
└── hubspot/
    └── pipeline.py
```

### Pipeline contract:
- Each pipeline is callable as a Python module or function
- Pipeline handles its own authentication (reads from env)
- Pipeline writes to the designated landing zone
- Pipeline is idempotent — running it twice doesn't duplicate data
- `run.sh` calls each pipeline in sequence

## run.sh Contract

```
#!/usr/bin/env bash
set -euo pipefail      # Fail fast on any error

# Extract
python -m pipelines.source_a.pipeline
python -m pipelines.source_b.pipeline

# Transform
cd transform && dbt run && dbt test && cd ..

# Validate (optional additional checks)
# python validate.py
```

- Must be executable (`chmod +x run.sh`)
- Must fail loudly (set -e)
- Must be idempotent
- This is the only thing cron needs to know about
