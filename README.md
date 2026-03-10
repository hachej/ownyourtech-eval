# ownyourtech-eval

Open-source evaluation framework for data engineering agents.

Tests whether an AI agent can build a **correct ELT pipeline** from a spec while following **EU-sovereign, open-source, local-first** technology principles.

Inspired by the [ELT-Bench paper](https://arxiv.org/abs/2501.12206) ([code](https://github.com/uiuc-kang-lab/ELT-Bench)) — same data, same ground truth, extensible framework.

## How it works

```
src/eval/eval.sh <scenario>
  │
  ├── 1. Spin up sources (Postgres, MongoDB, S3, REST API)
  ├── 2. Load deterministic data into each source
  ├── 3. Give the agent SPEC.md + CLAUDE.md in an isolated workdir
  ├── 4. Agent builds the pipeline (using oyt CLI to check tech choices)
  └── 5. Judges score the output
         ├── correctness  — CSV diff against ground truth (deterministic)
         ├── code_quality — LLM scores structure, errors, readability
         └── kg_compliance — LLM checks principle adherence
```

## Quick start

### Prerequisites

- Docker (for source databases)
- [Claude Code](https://claude.com/claude-code) CLI (for running agents and LLM judges)
- Python 3.10+ with `pyyaml`, `pymongo`, `flask`
- [`oyt` CLI](https://pypi.org/project/oyt/) — the agent uses this to consult the knowledge base

```bash
# Install oyt CLI
pip install oyt

# Or for development (from the private ownyourtech-cli repo):
# cd /path/to/ownyourtech-cli && uv pip install -e .
```

### Run an eval

```bash
git clone https://github.com/hachej/ownyourtech-eval.git
cd ownyourtech-eval

# Run eval (starts Docker, loads data, runs agent, scores output)
src/eval/eval.sh github --model claude-sonnet-4-6 --budget 5.00

# View results
cat results/github/*/verdicts.json
```

### Run judges on existing output

```bash
python src/judges/base.py src/scenarios/github /path/to/agent/workdir results/my-run sonnet
```

### Check ground truth manually

```bash
python src/judges/check.py src/scenarios/github /path/to/output/csvs
```

## The `github` scenario

The included scenario is a multi-source ELT challenge:

**14 source tables** across 5 source types:

| Source | Tables | Port |
|--------|--------|------|
| Postgres | issue, issue_closed_history, pull_request, users | 5433 |
| MongoDB | issue_comment, label, pull_request_review, team | 27017 |
| REST API | issue_assignee, issue_merged, repository | 5055 |
| S3 (LocalStack) | repo_team (JSONL) | 4566 |
| Flat files | requested_reviewer_history, issue_label | local |

**6 expected output models:**

| Model | Description |
|-------|------------|
| `github__issues` | Enriched issues with reopen counts, comments, repo names, creator info |
| `github__pull_requests` | Enriched PRs with reviews, merge timing, reviewer names |
| `github__daily_metrics` | Issues/PRs opened/closed/merged per repo per day |
| `github__weekly_metrics` | Same, aggregated by week |
| `github__monthly_metrics` | Same, aggregated by month |
| `github__quarterly_metrics` | Same, aggregated by quarter |

## Repository structure

```
ownyourtech-eval/
├── src/
│   ├── eval/
│   │   ├── eval.sh                  # Main eval runner
│   │   └── CLAUDE.md                # Agent instructions (plan → evaluate → execute)
│   ├── judges/
│   │   ├── base.py                  # Judge framework + CLI runner
│   │   ├── correctness.py           # CSV comparison judge (deterministic)
│   │   ├── code_quality.md          # LLM rubric: structure, errors, readability, docs
│   │   ├── kg_compliance.md         # LLM rubric: tier 1/2/3 principle checks
│   │   ├── check.py                 # Standalone ground truth comparison
│   │   └── README.md                # How to add judges
│   ├── scenarios/
│   │   └── github/
│   │       ├── scenario.yaml        # Credentials, judges, expected models
│   │       └── SPEC.md              # Task spec (what the agent sees)
│   └── data-sources/
│       ├── docker-compose.yaml      # Source databases (Postgres, Mongo, S3, API)
│       └── github/
│           ├── postgres_init.sh     # Loads tables into Postgres
│           ├── mongo_init.py        # Loads collections into MongoDB
│           ├── s3_init.sh           # Uploads files to LocalStack S3
│           ├── api_server.py        # Flask REST API (3 endpoints)
│           ├── data/github/         # 14 source CSVs (~200KB)
│           └── gt/github/           # 6 ground truth CSVs
├── results/                         # (gitignored) eval run outputs
├── AGENTS.md                        # LLM contributor guide
├── README.md
└── LICENSE
```

## Adding a scenario

See [AGENTS.md](AGENTS.md) for the full step-by-step guide. In short:

1. Add source data and init scripts to `src/data-sources/<name>/`
2. Create `src/scenarios/<name>/scenario.yaml` (credentials, judges, expected models)
3. Write `src/scenarios/<name>/SPEC.md` (the task the agent sees)
4. Add ground truth CSVs to `src/data-sources/<name>/gt/<name>/`
5. Run `src/eval/eval.sh <name>`

## Adding a judge

**Prompt judge** — create `src/judges/<name>.md` with a rubric ending in a JSON template. The framework injects the agent's code and spec automatically.

**Code judge** — create `src/judges/<name>.py` with `def judge(ctx: dict) -> dict`.

See [src/judges/README.md](src/judges/README.md) for details.

## The `oyt` CLI and Knowledge Base

The agent uses the `oyt` CLI during eval runs to consult the OwnYourTech knowledge base:

```bash
oyt kg list                              # Browse KB sections
oyt kg get principles/tier-1-core        # Read core principles
oyt kg evaluate "Use Snowflake"          # Check if a tech choice is approved
```

The knowledge base lives in the private [ownyourtech-cli](https://github.com/hachej/ownyourtech-cli) repo. Install the CLI:

```bash
pip install oyt                          # from PyPI
# or
uv pip install -e /path/to/ownyourtech-cli  # for local development
```

## Contributors

- [Timo Dechau](https://github.com/hachej)

## License

MIT
