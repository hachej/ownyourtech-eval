# ownyourtech-eval

Evaluate technology proposals against an opinionated knowledge base for **EU-sovereign, open-source, local-first data stacks**.

This is the open-source evaluation engine behind [`oyt kg evaluate`](https://github.com/hachej/ownyourtech-cli). Use it to check whether a proposed technology stack aligns with the OwnYourTech principles — or fork the KB and encode your own.

## How it works

The evaluator matches proposal text against a catalog of data tools, each with a recommendation level:

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

## Quick start

```bash
git clone https://github.com/hachej/ownyourtech-eval.git
cd ownyourtech-eval

# Run tests
make test

# Build and try it
make build
./oyt-eval "Use Snowflake for the data warehouse"
# → REJECTED (exit code 2)

./oyt-eval "Deploy dlt + DuckDB on Hetzner"
# → Approved (exit code 0)
```

## Usage

```bash
# Evaluate a proposal (finds kg/ automatically)
./oyt-eval "Use dlt for ingestion and DuckDB for analytics"

# Point to a custom KB
OYT_KB_PATH=/path/to/your/kg ./oyt-eval "Use Fivetran"

# Run all examples
make run-examples
```

### Output

```json
{
  "approved": false,
  "tier": 1,
  "conflicts": [
    {
      "tier": 1,
      "source": "catalog/storage",
      "message": "Snowflake: Rejected. Proprietary, US company, vendor lock-in on storage format. Violates Tier 1.",
      "alternatives": ["DuckDB", "PostgreSQL"]
    }
  ],
  "recommendation": "REJECTED (Tier 1 violation). Snowflake: Rejected. ... Use instead: DuckDB, PostgreSQL.",
  "matched_items": [...]
}
```

Exit codes: `0` = approved, `2` = rejected.

## As a Go library

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

## The Knowledge Base

The `kg/` directory contains the full evaluation corpus:

```
kg/
├── principles/          # Tiered constraints (non-negotiable → preferences)
│   ├── tier-1-core.md       # EU sovereignty, open source, local-first
│   ├── tier-2-defaults.md   # Hetzner, dlt, DuckDB, dbt-core, cron
│   └── tier-3-preferences.md # Monorepo, naming, Parquet
├── catalog/             # Solution recommendations by category
│   ├── ingestion.md         # dlt, Airbyte, Fivetran, Meltano...
│   ├── storage.md           # DuckDB, PostgreSQL, Snowflake, S3...
│   ├── transformation.md   # dbt-core, dbt Cloud, SQLMesh...
│   ├── orchestration.md    # Cron, Dagster, Airflow...
│   ├── compute.md          # Hetzner, OVH, AWS, GCP, Azure...
│   └── collection.md       # Buz, Snowplow, Segment, GA...
├── patterns/            # Reference architectures
│   ├── early-stage-stack.md
│   ├── growth-stage-stack.md
│   ├── data-modeling.md
│   └── project-structure.md
└── anti-patterns/       # What to avoid
    ├── over-engineering.md
    └── vendor-traps.md
```

## Fork & customize

The KB is just markdown. Fork this repo and edit the catalog tables to encode your own stack opinions:

```markdown
| Solution | Recommendation | Context |
|----------|---------------|---------|
| **YourTool** | Strong Default | Why it's your default choice |
| **BadTool** | Reject | Why it violates your principles |
```

The evaluator parses markdown tables with a `Recommendation` column and matches solution names against proposal text.

## Test cases

`testcases/proposals.json` contains example proposals with expected outcomes. Use it to validate your KB modifications or to understand the evaluation logic.

## License

MIT
