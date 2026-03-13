# Contributing to OwnYourTech Eval

Thanks for your interest in contributing. OwnYourTech Eval is an eval framework for data engineering agents — the more scenarios, judges, and source types exist, the more useful it becomes.

The easiest way to contribute is to **add a new scenario**. If you can prepare source data, write a task spec, and generate ground truth CSVs, you can contribute a scenario.

## Development setup

```bash
git clone https://github.com/hachej/ownyourtech-eval.git
cd ownyourtech-eval

# Start source services
docker compose -f src/data-sources/docker-compose.yaml up -d --wait

# Run the github scenario eval
src/eval/eval.sh github --model claude-sonnet-4-6 --budget 5.00
```

## Prerequisites

- Docker (for source databases)
- [Claude Code](https://claude.com/claude-code) CLI (for running agents and LLM judges)
- Python 3.10+ with `pyyaml`, `pymongo`
- [`yq`](https://github.com/mikefarah/yq) (YAML processor)
- [`duckdb`](https://duckdb.org/) CLI (correctness judge)
- AWS CLI (for LocalStack S3 init)
- [`oyt` CLI](https://pypi.org/project/oyt/) (agent uses this for KB evaluation)

## Adding a scenario

A scenario ties source data to a task spec and scoring config. See [AGENTS.md](AGENTS.md) for the detailed step-by-step guide.

### Quick overview

1. **Prepare source data** — create `src/data-sources/<name>/` with CSVs and init scripts:

```
src/data-sources/<name>/
  data/<name>/             # One CSV per source table
  gt/<name>/               # One CSV per expected output model
  postgres_init.sh         # Optional: load tables into Postgres
  mongo_init.py            # Optional: load collections into MongoDB
  s3_init.sh               # Optional: upload files to S3
  api_server.py            # Optional: Flask REST API
```

2. **Create the scenario** — `src/scenarios/<name>/scenario.yaml` + `SPEC.md`:

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
judges:
  - correctness
  - code_quality
expected_models:
  - name: output_model_a
    ground_truth: ../../data-sources/mydata/gt/mydata/output_model_a.csv
```

3. **Write SPEC.md** — the task the agent sees. Must include: objective, source data (connection details, tables, columns), expected output models (column specs), deliverable format, constraints.

4. **Run it:**

```bash
src/eval/eval.sh mydata --model claude-sonnet-4-6 --budget 5.00
```

### Ground truth guidelines

- Header row with exact column names the correctness judge expects
- Sorted by columns 1 and 2 (judge does `ORDER BY 1,2` when exporting)
- Empty string for nulls
- Numeric values compared with 1% tolerance
- Row count must match exactly

### Scenario contribution ideas

These are data domains the community can add scenarios for:

- **E-commerce** — orders, products, customers, inventory across sources
- **IoT / sensor data** — time-series from multiple device types
- **Financial** — transactions, accounts, exchange rates
- **SaaS metrics** — events, subscriptions, usage data
- **Log analytics** — application logs, error aggregation

## Adding a judge

### Prompt judge (easiest)

Create `src/judges/<name>.md` with an LLM rubric. The framework automatically injects the agent's spec and code. Must include a JSON output template with `"pass": true/false`.

### Code judge

Create `src/judges/<name>.py` with:

```python
def judge(ctx: dict) -> dict:
    workdir = Path(ctx["workdir"])
    # ... your logic ...
    return {
        "pass": True,
        "summary": "...",
    }
```

### Register it

Add to `judges` list in your scenario.yaml.

See [src/judges/README.md](src/judges/README.md) for details.

## Other contributions

- **Bug fixes** — open an issue first, then submit a PR with a test or repro
- **Eval runner improvements** — improvements to `eval.sh` reliability and features
- **Documentation** — improvements to AGENTS.md, README.md, or judge docs

## PR process

1. Fork the repository and create a branch from `main`
2. Make your changes
3. Test: run at least one eval to verify nothing breaks
4. Submit a pull request with a clear description

PRs are reviewed within a few days. Small, focused PRs are easier to review and merge.

## Code style

- Shell scripts: `set -euo pipefail`, quote variables
- Python: standard formatting, type hints where helpful
- Markdown specs: clear structure with connection details and column descriptions
- YAML configs: comments for non-obvious fields

## Getting help

- **GitHub Issues** — for bugs and feature requests
- **GitHub Discussions** — for questions, ideas, and general conversation
