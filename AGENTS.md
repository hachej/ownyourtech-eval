# AGENTS.md — LLM contributor guide

This file explains the codebase to AI coding agents. Read this before making changes.

## What this repo is

An open-source eval framework for data engineering agents. It tests whether an AI agent can build a correct ELT pipeline from a spec while following technology principles enforced by the `oyt` CLI.

The knowledge base and `oyt` CLI live in the **private** ownyourtech-cli repo. This repo contains only the eval harness: sources, scenarios, judges, and the runner.

## Architecture

```
src/eval/eval.sh <scenario-name> [--model <model>] [--budget <usd>]
  │
  ├── docker compose up ─── eval-postgres (5433)
  │                     ├── eval-mongodb  (27017)
  │                     ├── eval-localstack (4566, S3)
  │                     └── eval-api (5055, Flask REST)
  │
  ├── init scripts ─── postgres_init.sh (psql \COPY from CSVs)
  │                ├── mongo_init.py     (pymongo insert_many)
  │                ├── s3_init.sh        (aws s3 cp to LocalStack)
  │                └── api_server.py     (Flask reads from CSVs)
  │
  ├── prepare workdir ─── /tmp/eval-<scenario>-XXXXXX/
  │                   ├── SPEC.md    (task for agent)
  │                   ├── CLAUDE.md  (agent instructions)
  │                   └── data/      (flat files)
  │
  ├── run agent ─── claude -p --model <model> --max-budget-usd <budget>
  │            ├── OYT_KB_PATH set so agent can use `oyt kg evaluate`
  │            └── output: agent.jsonl, agent.log
  │
  └── run judges ─── correctness.py  (CSV diff vs ground truth)
                 ├── code_quality.md (LLM rubric, 4 dimensions)
                 └── kg_compliance.md (LLM rubric, tier checks)
                 └── output: verdicts.json
```

## File-by-file reference

### Eval runner

| File | What it does |
|------|-------------|
| `src/eval/eval.sh` | Orchestrator. Parses flags, starts Docker, loads data, creates workdir, runs agent, runs judges, writes metadata. Generic — auto-detects init scripts per scenario. |
| `src/eval/docker-compose.yaml` | 4 services: `eval-postgres` (:5433), `eval-mongodb` (:27017), `eval-localstack` (:4566), `eval-api` (:5055). |
| `src/eval/CLAUDE.md` | Injected into agent context. Tells agent: plan first, evaluate tech with `oyt kg evaluate`, then execute. Two-phase workflow. |
| `src/eval/system-prompt.md` | Alternative system prompt. Describes mandatory workflow and output structure (`stack/` + `report.md`). |

### Data sources

A "source" is a dataset loaded into Docker services. Each source has init scripts and CSV data.

| File | What it does |
|------|-------------|
| `src/data-sources/github/source.yaml` | Declares 14 tables across 5 source types: postgres (4), mongodb (4), rest_api (3), s3 (1), flat_files (2). |
| `src/data-sources/github/postgres_init.sh` | Creates `github` database. Creates tables: `issue`, `issue_closed_history`, `pull_request`, `users`. Loads via `\COPY` from CSVs. Takes data dir as `$1`. |
| `src/data-sources/github/mongo_init.py` | Drops+recreates `github` db. Loads 4 collections: `issue_comment`, `label`, `pull_request_review`, `team`. Reads `MONGO_URI` from env. |
| `src/data-sources/github/s3_init.sh` | Creates `github-bucket` in LocalStack, uploads `repo_team.jsonl`. Uses `aws` CLI with `--endpoint-url`. |
| `src/data-sources/github/api_server.py` | Flask app on port 5055. Three routes: `GET /github/issue_assignee`, `GET /github/issue_merged`, `GET /github/repository`. Each reads from CSV, returns JSON array. |
| `src/data-sources/github/data/github/*.csv` | 14 source CSV files (~200KB total). Committed to git. |
| `src/data-sources/github/gt/github/*.csv` | 6 ground truth CSVs. Column names must match exactly (case-insensitive). Rows sorted by first two columns. |

**To understand the source data**, read `source.yaml` for the schema overview, then look at the CSV headers for exact column names.

### Scenarios

A scenario ties a source dataset to a task spec and scoring config.

| File | What it does |
|------|-------------|
| `src/scenarios/github/scenario.yaml` | Defines: name, credentials (as `KEY=VALUE` list), which judges to run, expected models with ground truth paths. |
| `src/scenarios/github/SPEC.md` | The task the agent sees. Describes all sources (connection strings, tables, columns), all 6 expected output models (column-level specs), deliverable format, constraints. |

**`scenario.yaml` is the central config.** It connects everything: source → credentials → spec → judges → ground truth.

### Judges

Judges score agent output. Two types:

**Code judges (`.py`)** — deterministic, run Python logic. Must export `def judge(ctx: dict) -> dict`.

**Prompt judges (`.md`)** — a markdown rubric sent to an LLM. The framework auto-injects SPEC.md + agent source code. Must include a JSON output template with `"pass": true/false`.

Prompt judges take priority: if both `foo.md` and `foo.py` exist, the `.md` wins.

| File | Type | What it checks |
|------|------|---------------|
| `src/judges/base.py` | Framework | Resolves judges by name (`<name>.md` or `<name>.py`). `run_prompt_judge()` sends rubric + agent code to Claude. `run_code_judge()` imports and calls `judge()`. `collect_source_files()` gathers agent's code (up to 3000 lines). `parse_json_from_text()` extracts JSON from LLM output. |
| `src/judges/correctness.py` | Code | Finds agent's database files (DuckDB `.duckdb` or SQLite `.db`/`.sqlite`). Exports each expected model to CSV via CLI. Compares column-by-column against ground truth. Numeric tolerance: 1%. Case-insensitive column matching. |
| `src/judges/code_quality.md` | Prompt | Scores 4 dimensions (0-10 each): structure & modularity, error handling, readability, documentation. Pass threshold: 24/40 (60%). |
| `src/judges/kg_compliance.md` | Prompt | Checks Tier 1 violations (auto-fail), Tier 2 deviations (should be justified), Tier 3 preferences, anti-patterns (over-engineering, vendor lock-in, hardcoded creds). |
| `src/judges/run_judges.py` | Runner | CLI that reads scenario.yaml, builds judge context dict, runs all judges, prints verdicts, saves `verdicts.json`. |
| `src/judges/check.py` | Standalone | Same correctness logic as the judge. CLI: `python src/judges/check.py <scenario-dir> <output-dir>`. |

**Judge context dict** (passed to all judges):

```python
ctx = {
    "workdir": str,        # path to agent's working directory
    "agent_log": str,      # path to agent.log
    "scenario_dir": str,   # path to scenario directory
    "scenario": dict,      # parsed scenario.yaml
    "results_dir": str,    # where to write judge outputs
    "model": str,          # which LLM model was used
    "judge_config": dict,  # optional per-judge config from scenario.yaml
}
```

## How to add a new scenario

### Step 1: Prepare source data

Create `src/data-sources/<name>/` with:

```
src/data-sources/<name>/
├── source.yaml              # Schema declaration
├── data/<name>/             # One CSV per source table
├── gt/<name>/               # One CSV per expected output model
├── postgres_init.sh         # Optional: load tables into Postgres
├── mongo_init.py            # Optional: load collections into MongoDB
├── s3_init.sh               # Optional: upload files to S3
└── api_server.py            # Optional: Flask REST API
```

Only create init scripts for the source types your scenario uses. A Postgres-only scenario doesn't need mongo_init.py.

**`source.yaml` format** — declare which tables live where:

```yaml
name: mydata
description: Short description

postgres:
  host: eval-postgres          # Docker service name
  port: 5432                   # Internal Docker port
  database: mydata
  user: postgres
  password: testelt
  tables:
    - customers
    - orders

# Only include sections for source types you actually use:
# mongodb:
#   host: eval-mongodb
#   port: 27017
#   database: mydata
#   tables:
#     - events

# rest_api:
#   host: eval-api
#   port: 5005
#   tables:
#     - products

# s3:
#   endpoint: http://eval-localstack:4566
#   bucket: mydata-bucket
#   tables:
#     - logs    # stored as logs.jsonl

# flat_files:
#   tables:
#     - config_data

expected_models:
  - output_model_a
  - output_model_b
```

**Init script templates** — copy and adapt from `src/data-sources/github/`:

`postgres_init.sh` pattern:
```bash
#!/bin/bash
set -e
DATA_DIR="${1:-.}/data/mydata"
PGPASSWORD=testelt psql -h localhost -U postgres -p 5433 -c "DROP DATABASE IF EXISTS mydata;"
PGPASSWORD=testelt psql -h localhost -U postgres -p 5433 -c "CREATE DATABASE mydata;"
PGPASSWORD=testelt psql -h localhost -U postgres -p 5433 -d mydata -c "
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT);
"
PGPASSWORD=testelt psql -h localhost -U postgres -p 5433 -d mydata -c "\COPY customers FROM '$DATA_DIR/customers.csv' DELIMITER ',' CSV HEADER;"
```

`mongo_init.py` pattern:
```python
import csv, os
from pathlib import Path
from pymongo import MongoClient
DATA_DIR = Path(__file__).parent / "data" / "mydata"
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/?directConnection=true"))
client.drop_database("mydata")
db = client["mydata"]
for table in ["events"]:
    with open(DATA_DIR / f"{table}.csv") as f:
        rows = [row for row in csv.DictReader(f)]
    if rows:
        db[table].insert_many(rows)
```

`api_server.py` pattern:
```python
import csv
from pathlib import Path
from flask import Flask, jsonify
app = Flask(__name__)
DATA_DIR = Path(__file__).parent / "data" / "mydata"
def load_csv(name):
    with open(DATA_DIR / f"{name}.csv") as f:
        return [{k: (None if v == "" else v) for k, v in row.items()} for row in csv.DictReader(f)]
@app.route("/mydata/products", methods=["GET"])
def get_products():
    return jsonify(load_csv("products"))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5055)
```

**Ground truth CSVs** — put at `gt/<name>/<model_name>.csv`:
- Header row with exact column names the correctness judge expects
- Sorted by columns 1 and 2 (judge does `ORDER BY 1,2` when exporting agent output)
- Empty string for nulls
- Numeric values compared with 1% tolerance

### Step 2: Create the scenario

```
src/scenarios/<name>/
├── scenario.yaml
└── SPEC.md
```

**`scenario.yaml`:**

```yaml
name: mydata
description: >
  What the agent must build.

spec: SPEC.md
source: mydata

credentials:
  - PG_HOST=localhost
  - PG_PORT=5433
  - PG_USER=postgres
  - PG_PASSWORD=testelt
  - PG_DATABASE=mydata
  # Add every credential the agent needs.
  # These become env vars in the agent's shell.

judges:
  - correctness              # always include
  - code_quality             # LLM judge (optional)
  # - kg_compliance          # LLM judge (optional)
  # - name: code_quality     # with config override:
  #   config:
  #     judge_model: opus

expected_models:
  - name: output_model_a
    ground_truth: ../../data-sources/mydata/gt/mydata/output_model_a.csv
  - name: output_model_b
    ground_truth: ../../data-sources/mydata/gt/mydata/output_model_b.csv
```

**`SPEC.md`** — the task the agent sees. Must include:

1. **Objective** — what to build (1-2 sentences)
2. **Source data** — for each source type: connection details, table names, column descriptions
3. **Expected output models** — for each model: column names with descriptions. Be precise — the correctness judge compares columns exactly (case-insensitive).
4. **Deliverable** — code in `stack/`, a `report.md`
5. **Constraints** — e.g. "everything runs locally", "no Docker"

Use `src/scenarios/github/SPEC.md` as the reference template.

### Step 3: Run it

```bash
src/eval/eval.sh mydata --model claude-sonnet-4-6 --budget 5.00
ls results/mydata/
```

`eval.sh` is generic — it auto-detects init scripts (`postgres_init.sh`, `mongo_init.py`, `s3_init.sh`) in `src/data-sources/<name>/` and runs them if present. No code changes needed.

## How to add a judge

### Prompt judge (easiest)

Create `src/judges/<name>.md`. The framework automatically:
1. Reads SPEC.md from the agent's workdir
2. Collects all agent source files (`.py`, `.sql`, `.sh`, `.yaml`, `.yml`, `.toml`, `.md` — up to 3000 lines)
3. Builds prompt: spec + your rubric + agent code
4. Sends to Claude (model configurable via `judge_config.judge_model`, default: sonnet)
5. Parses JSON from response

Your rubric must define:
- What to evaluate (dimensions, criteria)
- A JSON output template with `"pass": true/false`

```markdown
# My Judge Name

Score the agent's solution on <what you care about>.

## Dimensions

### Dimension A (0-10)
What to look for...

### Dimension B (0-10)
What to look for...

## Output

Respond with ONLY a JSON object:

\```json
{
  "dimension_a": {"score": 0, "max": 10, "evidence": "..."},
  "dimension_b": {"score": 0, "max": 10, "evidence": "..."},
  "total": 0,
  "max_total": 20,
  "pass": true,
  "summary": "..."
}
\```

Set `pass` to `true` if total >= 12 (60%).
```

### Code judge

Create `src/judges/<name>.py`:

```python
def judge(ctx: dict) -> dict:
    """
    ctx keys: workdir, agent_log, scenario_dir, scenario, results_dir, model
    """
    workdir = Path(ctx["workdir"])
    # ... your logic ...
    return {
        "pass": True,        # required
        "summary": "...",    # shown in output
        # any other fields go into verdicts.json
    }
```

### Register it

Add to `judges` list in your scenario.yaml:

```yaml
judges:
  - correctness
  - my_custom_judge      # resolves to src/judges/my_custom_judge.md or .py
```

## Eval output

Each run produces:

```
results/<scenario>/<YYYYMMDD-HHMMSS-model>/
├── meta.yaml            # scenario, model, budget, duration, timestamp
├── agent.jsonl          # raw Claude Code stream (JSON lines)
├── agent.log            # readable transcript (text + [TOOL] + [RESULT])
├── agent.stderr.log     # stderr from agent process
├── judges.log           # judge runner stdout
├── verdicts.json        # machine-readable judge results
└── judge_<name>.md      # raw LLM output from each prompt judge
```

**`verdicts.json` example:**

```json
[
  {
    "judge": "correctness",
    "pass": true,
    "summary": "(6/6 models correct)",
    "model_results": {
      "github__issues": {"pass": true, "matched": 18, "unmatched": 0, "missing": 0},
      "github__pull_requests": {"pass": true, "matched": 21, "unmatched": 0, "missing": 0}
    }
  },
  {
    "judge": "code_quality",
    "pass": true,
    "total": 32,
    "max_total": 40,
    "structure": {"score": 8, "max": 10, "evidence": "..."},
    "error_handling": {"score": 7, "max": 10, "evidence": "..."},
    "readability": {"score": 9, "max": 10, "evidence": "..."},
    "documentation": {"score": 8, "max": 10, "evidence": "..."}
  }
]
```

## How the correctness judge works

This is the most important judge. Understanding it helps write good ground truth.

1. Searches agent's workdir for `*.duckdb` files (tries DuckDB first, then SQLite `.db`/`.sqlite`)
2. For each expected model, runs `SELECT * FROM <model_name> ORDER BY 1,2` to export CSV
3. Also searches non-default schemas (`information_schema.tables` lookup)
4. Compares column-by-column against ground truth:
   - Column names matched **case-insensitively**
   - Null handling: both empty = match, one empty = mismatch
   - Numeric: 1% relative tolerance (`abs(b-a)/abs(a) <= 0.01`)
   - String: exact match after `.strip()`
5. A model passes if all columns match and no columns are missing
6. Overall pass requires all models to pass

**Gotchas:**
- Column names in ground truth must match what the agent creates (case doesn't matter)
- Row count must match exactly
- Numeric precision matters — ground truth should use the same rounding as the expected SQL
- The judge exports with `ORDER BY 1,2` — ground truth must be sorted the same way

## The `oyt` CLI

The `oyt` CLI is installed separately (not part of this repo). The agent uses it during eval runs:

```bash
oyt kg list                              # Browse KB categories
oyt kg get principles/tier-1-core        # Read a KB entry
oyt kg search "ingestion"               # Search KB content
oyt kg evaluate "Use Snowflake"          # Check tech choice → REJECTED/APPROVED/WARNING
```

Install:
```bash
pip install oyt                          # from PyPI (public)
uv pip install -e /path/to/ownyourtech-cli  # for development (private repo)
```

`eval.sh` sets `OYT_KB_PATH` to point to the KB root so the agent can resolve it.

## Common tasks

| Task | Command |
|------|---------|
| Run an eval | `src/eval/eval.sh github --model claude-sonnet-4-6 --budget 5.00` |
| Run judges on existing output | `python src/judges/run_judges.py src/scenarios/github /tmp/workdir results/run sonnet` |
| Check CSVs against ground truth | `python src/judges/check.py src/scenarios/github /path/to/csvs` |
| Start source services only | `docker compose -f src/eval/docker-compose.yaml up -d --wait` |
| Stop source services | `docker compose -f src/eval/docker-compose.yaml down` |
| Load data manually | `bash src/data-sources/github/postgres_init.sh src/data-sources/github` |
| View an agent transcript | `cat results/github/*/agent.log` |
| View judge verdicts | `cat results/github/*/verdicts.json` |
