---
name: eval-testing
description: Use when running or debugging eval scenarios - runs eval, checks ground truth, analyzes judge output
---

# Eval Testing Skill

Run and debug evaluation scenarios. Useful for verifying scenarios work end-to-end, checking ground truth accuracy, and debugging judge behavior.

## When to Use

- Testing changes to eval.sh, judges, or scenarios
- Verifying a new scenario works correctly
- Debugging why a judge produces unexpected results
- Checking ground truth CSVs against agent output

## Prerequisites

- Docker running (for source databases)
- `yq`, `duckdb`, `python3` installed
- `oyt` CLI installed (`pip install oyt`)

## Workflow

### 1. Start Source Services

```bash
docker compose -f src/data-sources/docker-compose.yaml up -d --wait
```

Verify services are healthy:
```bash
docker compose -f src/data-sources/docker-compose.yaml ps
```

### 2. Load Data (Manual)

If you need to reload data without running the full eval:

```bash
# Postgres
bash src/data-sources/github/postgres_init.sh src/data-sources/github

# MongoDB
MONGO_URI="mongodb://localhost:27017/?directConnection=true" python3 src/data-sources/github/mongo_init.py

# S3 (LocalStack)
bash src/data-sources/github/s3_init.sh src/data-sources/github

# REST API (runs in foreground)
python3 src/data-sources/github/api_server.py
```

### 3. Run Full Eval

```bash
src/eval/eval.sh github --model claude-sonnet-4-6 --budget 5.00
```

### 4. Check Ground Truth Only

If you just want to verify CSVs match:

```bash
python src/judges/check.py src/scenarios/github /path/to/output/csvs
```

### 5. Run Judges on Existing Output

```bash
python src/judges/base.py src/scenarios/github /path/to/workdir results/run sonnet
```

### 6. Analyze Results

```bash
# View verdicts
cat results/github/*/verdicts.json | python3 -m json.tool

# View agent log
cat results/github/*/agent.log

# View judge output
cat results/github/*/judges.log
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Docker services not starting | Port conflict | Check `docker ps`, stop conflicting containers |
| Ground truth mismatch | Wrong sort order | Ground truth must be sorted by columns 1 and 2 |
| Numeric comparison failure | Rounding difference | Ground truth uses 1% tolerance, check precision |
| Agent can't find `oyt` | Not installed or not in PATH | `pip install oyt`, check `which oyt` |
| Init script fails | Data directory path wrong | Init scripts take data dir as `$1` |

## Debugging Judge Logic

### Correctness Judge

The correctness judge (`src/judges/correctness.py`):
1. Finds `*.duckdb` files in the workdir
2. For each expected model, runs `SELECT * FROM <model> ORDER BY 1,2`
3. Compares columns against ground truth CSVs

To debug:
```bash
# Open the agent's DuckDB
duckdb /path/to/agent/output.duckdb
# List tables
SHOW TABLES;
# Check a model
SELECT * FROM github__issues ORDER BY 1,2 LIMIT 5;
```

### LLM Judges

LLM judges (`code_quality.md`, `kg_compliance.md`) output raw responses to `judge_<name>.md` in the results directory. Read these to understand scoring.
