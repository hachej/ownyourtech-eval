# CLAUDE.md - OwnYourTech Eval

Best practices and conventions for working on OwnYourTech Eval.

---

## Overview

OwnYourTech Eval is the **lab that fine-tunes the OwnYourTech knowledge base**. It runs AI agents through realistic technology scenarios, scores the results, and reveals where the KB's principles produce good outcomes and where they need to be sharper. Scope goes beyond data engineering — OwnYourTech covers all tech.

**Target users:** KB developers (ourselves), agent developers, teams adopting OwnYourTech

**Key concept:** "Run real scenarios, measure outcomes, sharpen principles — the KB gets better with every eval run."

**How it works:** Spin up sources (Docker) -> Give agent SPEC.md + CLAUDE.md -> Agent builds using `oyt kg evaluate` -> Judges score output (correctness, quality, KB compliance) -> Feed results back into KB improvements

For the full vision, see [VISION.md](./VISION.md). For the development workflow, see [HOW_WE_WORK.md](./HOW_WE_WORK.md).

---

## Tech Stack

- **Eval runner:** Bash (`eval.sh`)
- **Judges:** Python (deterministic) + Markdown (LLM rubrics)
- **Sources:** Docker Compose (Postgres, MongoDB, LocalStack S3, Flask REST API)
- **Data:** CSV files (source data + ground truth)
- **Scenarios:** YAML config + Markdown specs
- **Agent:** Claude Code CLI
- **KB CLI:** `oyt` (PyPI package)

---

## Development

```bash
# Start source services
docker compose -f src/data-sources/docker-compose.yaml up -d --wait

# Run an eval
src/eval/eval.sh github --model claude-sonnet-4-6 --budget 5.00

# Run judges on existing output
python src/judges/base.py src/scenarios/github /tmp/workdir results/run sonnet

# Check ground truth manually
python src/judges/check.py src/scenarios/github /path/to/csvs

# Stop source services
docker compose -f src/data-sources/docker-compose.yaml down
```

---

## Development Workflow

This project uses Beads (`bd`) for task tracking and Claude Code sub-agents for autonomous execution. The product layer (Missions -> Epics -> Stories) feeds into an automated pipeline.

```
+-----------------------------------------------------------------------+
|  Product Layer (TOML files)                                            |
|                                                                        |
|   product/missions/ -> product/epics/ -> product/stories/              |
|                                                                        |
+-----------------------------------------------------------------------+
|  Execution (Claude Code sub-agents)                                    |
|                                                                        |
|   /execute-mission M001                                                |
|     Phase 1: Breakdown + LLM triage -> Beads tasks                     |
|     Phase 2: Epic sub-agents (parallel, worktree) -> PRs               |
|     Phase 3: /fix-pr-feedback -> address review comments               |
|     Phase 4: Report                                                    |
|                                                                        |
+-----------------------------------------------------------------------+
|  Post-Implementation                                                   |
|                                                                        |
|   /retro -> discover follow-up issues -> Beads tasks                   |
|                                                                        |
+-----------------------------------------------------------------------+
```

### Beads CLI Reference

```bash
# List tasks by label
bd list --label ready --json

# Show task details
bd show <id> --json

# Create task with label
bd create "Title" --labels plan -d "description" --silent

# Update status/labels
bd update <id> --status in_progress
bd update <id> --remove-label plan --add-label ready

# Close task
bd close <id>

# Check status
bd status
```

### Commands

| Command | Description |
|---------|-------------|
| `/execute-mission` | Full autopilot: breakdown -> triage -> implement -> PR feedback -> report |
| `/fix-pr-feedback` | Read PR review comments, fix actionable feedback (max 2 rounds) |
| `/retro` | Post-implementation retrospective, discover follow-up issues |

---

## Product Thinking

The full development workflow (vision -> value ladder -> missions -> epics -> stories -> execution) is documented in [HOW_WE_WORK.md](./HOW_WE_WORK.md). That document is the primary reference for how ideas become shipped features.

### Quick Reference

```
VISION.md              <- "What transformation?" (rarely)
    |
VALUES.md              <- "What value?" (when levels change)
    |
product/missions/      <- Outcome-oriented work packages
    |
/execute-mission       <- Autonomous: breakdown -> triage -> implement -> PR
    |
/retro                 <- Discover follow-up issues
```

### The Flow

1. **Direction:** Refine vision and value ladder as needed
2. **Mission:** Define the mission TOML
3. **Execute:** `/execute-mission M001` — everything from breakdown to PRs, autonomous
4. **Review:** Review and merge epic PRs
5. **Retro:** `/retro` — discover follow-up issues

---

## Testing

Judges are the test system. Two types:

**Code judges (`.py`)** — deterministic Python logic. Must export `def judge(ctx: dict) -> dict`.

**Prompt judges (`.md`)** — LLM rubric. Framework auto-injects SPEC.md + agent code.

**Commands:**
```bash
# Run judges on agent output
python src/judges/base.py src/scenarios/<name> <workdir> <results-dir> <model>

# Quick ground truth check
python src/judges/check.py src/scenarios/<name> /path/to/csvs
```

**Key patterns:**
- Code judges return `{"pass": bool, "summary": str, ...}`
- Prompt judges must include a JSON output template with `"pass": true/false`
- Correctness judge: CSV column-by-column comparison, 1% numeric tolerance, case-insensitive columns
- Ground truth CSVs sorted by columns 1 and 2

---

## Critical Rules

**Ground truth must be deterministic**
- Sorted by columns 1 and 2 (judge does `ORDER BY 1,2`)
- Numeric precision must match expected SQL rounding
- Empty string for nulls

**Init scripts must be idempotent**
- Always `DROP DATABASE IF EXISTS` then `CREATE DATABASE`
- Always `client.drop_database()` before inserting
- Data loaded from CSVs in `src/data-sources/<name>/data/`

**Scenarios are self-contained**
- `scenario.yaml` connects everything: source -> credentials -> spec -> judges -> ground truth
- `SPEC.md` is what the agent sees — must include all connection details and column specs
- Credentials are `KEY=VALUE` pairs that become env vars in the agent's shell

---

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/eval/` | Eval runner (`eval.sh`) and agent instructions (`CLAUDE.md`) |
| `src/judges/` | Judge framework (`base.py`), deterministic judges (`.py`), LLM judges (`.md`) |
| `src/scenarios/` | Scenario configs (`scenario.yaml`) and task specs (`SPEC.md`) |
| `src/data-sources/` | Docker Compose, init scripts, source CSVs, ground truth CSVs |
| `product/` | Mission/epic/story TOML files for product planning |
| `results/` | (gitignored) Eval run outputs |

---

## Huginn Memory (Project-Scoped)

This project is registered in Huginn Memory as `project="ownyourtech-eval"`.

When using MCP tools (`mcp__huginn-memory__*`), **always pass `project="ownyourtech-eval"`** on these scoped tools:
- **Memory:** remember, recall, decide, forget, summarize
- **Tasks:** create_task, update_task, list_tasks, get_task, dismiss_task, surface_daily_candidates
- **Agents:** get_agent_profile, update_agent_profile, log_agent_execution, get_agent_metrics, log_feedback, get_feedback_summary, get_content_calendar, update_content_calendar

Global tools (daily entries, cashflow, time tracking, brainstorm, web distillation) do **not** take a project parameter.
