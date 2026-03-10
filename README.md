# ownyourtech-eval

Open-source evaluation framework for **EU-sovereign, open-source, local-first data stacks**.

Two things in one repo:

1. **Knowledge Base + Evaluator** — check if a technology proposal aligns with OwnYourTech principles (`oyt kg evaluate`)
2. **Agent Eval Framework** — give an AI agent a spec, measure whether it builds a correct ELT pipeline following those principles

Ported from [ELT-Bench](https://github.com/uiuc-kang-lab/ELT-Bench) — same data, same ground truth, extensible framework.

## Quick start

### 1. Stack evaluator

Check technology proposals against the knowledge base:

```bash
git clone https://github.com/hachej/ownyourtech-eval.git
cd ownyourtech-eval

make test    # run Go tests
make build   # build the CLI

./oyt-eval "Use Snowflake for the data warehouse"
# → REJECTED (exit code 2)

./oyt-eval "Deploy dlt + DuckDB on Hetzner"
# → Approved (exit code 0)
```

### 2. Agent eval

Run an AI agent against a scenario and score the output:

```bash
cd evals

# Start source databases (Postgres, MongoDB, S3, REST API)
docker compose up -d --wait

# Run the eval
./eval.sh github --model claude-sonnet-4-6 --budget 5.00

# Check results
ls results/github/
```

## How it works

### Stack evaluator

Matches proposal text against a catalog of data tools with recommendation levels:

| Level | Meaning | Effect |
|-------|---------|--------|
| **Strong Default** | The recommended choice | Approved (tier 0) |
| **Acceptable** | Fine with context | Approved (tier 0) |
| **Avoid** | Discouraged but not blocked | Warning (tier 2) |
| **Reject** | Violates core principles | Rejected (tier 1) |

Core principles (Tier 1) are non-negotiable:
- **EU data sovereignty** — no US cloud providers in the data path
- **Self-hosted & open source** — no proprietary SaaS for core infrastructure
- **Local-first** — don't distribute what doesn't need distributing

### Agent eval

1. **Sources** spin up (Postgres, MongoDB, S3, REST API) with deterministic data
2. **Agent** reads SPEC.md in an isolated workdir and builds the pipeline
3. **Judges** score the output:
   - `correctness` — compares agent output CSVs against ground truth (pass/fail per model, per column)
   - `code_quality` — LLM judge scores structure, error handling, readability, documentation
   - `kg_compliance` — LLM judge checks tier 1/2/3 principle adherence

## Repository structure

```
ownyourtech-eval/
├── kg/                          # Knowledge base (principles, catalog, patterns)
├── eval/                        # Go eval library
│   ├── eval.go
│   └── eval_test.go
├── cmd/oyt-eval/                # Standalone CLI
├── testcases/                   # Example proposals with expected outcomes
├── evals/                       # Agent eval framework
│   ├── eval.sh                  # Main runner
│   ├── docker-compose.yaml      # Source databases
│   ├── CLAUDE.md                # Agent instructions
│   ├── system-prompt.md         # System prompt
│   ├── bin/
│   │   ├── check.py             # Ground truth comparison
│   │   └── run_judges.py        # Judge runner
│   ├── judges/
│   │   ├── base.py              # Judge framework (prompt + code judges)
│   │   ├── correctness.py       # CSV comparison judge
│   │   ├── code_quality.md      # LLM rubric for code quality
│   │   └── kg_compliance.md     # LLM rubric for KB compliance
│   ├── scenarios/github/
│   │   ├── scenario.yaml        # Sources, credentials, expected models
│   │   └── SPEC.md              # What the agent sees
│   └── sources/github/
│       ├── data/github/         # Source CSVs (14 tables)
│       ├── gt/github/           # Ground truth CSVs (6 models)
│       ├── postgres_init.sh     # Loads tables into Postgres
│       ├── mongo_init.py        # Loads tables into MongoDB
│       ├── s3_init.sh           # Loads table into S3
│       └── api_server.py        # Serves tables via REST
├── go.mod
├── Makefile
└── README.md
```

## Go library

```go
import "github.com/hachej/ownyourtech-eval/eval"

kb := eval.New("./kg")
result, err := kb.Evaluate("Use Snowflake and Fivetran")

if !result.Approved {
    for _, c := range result.Conflicts {
        fmt.Printf("Tier %d: %s\n", c.Tier, c.Message)
    }
}
```

## Adding a scenario

1. Add source data under `evals/sources/<name>/`
2. Create `evals/scenarios/<name>/scenario.yaml` with credentials and expected models
3. Write `SPEC.md` — the agent's prompt
4. Add ground truth CSVs
5. Run `./evals/eval.sh <name>`

## Adding a judge

**Prompt judge** — create `evals/judges/<name>.md` with a rubric. The runner injects agent source code and spec automatically.

**Code judge** — create `evals/judges/<name>.py` with a `judge(ctx) -> dict` function.

See `evals/judges/README.md` for details.

## Fork & customize

The KB is just markdown. Fork this repo and edit the catalog tables to encode your own stack opinions:

```markdown
| Solution | Recommendation | Context |
|----------|---------------|---------|
| **YourTool** | Strong Default | Why it's your default choice |
| **BadTool** | Reject | Why it violates your principles |
```

## Prerequisites

- Go 1.22+ (for the eval library)
- Docker (for agent eval sources)
- [Claude Code](https://claude.com/claude-code) CLI (for running agents)
- Python 3.10+ with `pyyaml`, `pymongo`, `flask` (for source setup and judges)

## License

MIT
