# Judges

Composable evaluation modules. Two types:

- **Prompt judges** (`.md`) — A markdown rubric sent to an LLM. Write a rubric, get structured scores.
- **Code judges** (`.py`) — Python code for deterministic checks. Implement `judge(ctx) -> dict`.

Prompt judges take priority: if both `foo.md` and `foo.py` exist, the `.md` wins.

## How prompt judges work

The framework does the heavy lifting. Your `.md` file only needs to define the rubric.

When a prompt judge runs, `base.py` automatically:
1. Reads `SPEC.md` from the agent's workdir
2. Collects all source files (`.py`, `.sql`, `.sh`, `.yaml`, `.yml`, `.toml`, `.md`) up to 3000 lines
3. Builds the full prompt: `## Spec` + `## Rubric` (your file) + `## Agent's Source Code`
4. Calls `claude -p --model <judge_model>` (default: sonnet, configurable per scenario)
5. Parses JSON from the response (handles ```json blocks and inline JSON)
6. Saves raw LLM output to `results/<run>/judge_<name>.md`

## Adding a prompt judge

Create `judges/<name>.md`:

```markdown
# My Judge Name

What to evaluate and why.

## Dimensions

### Dimension A (0-10)
Specific criteria...

### Dimension B (0-10)
Specific criteria...

## Output

Respond with ONLY a JSON object:

\```json
{
  "dimension_a": {"score": 0, "max": 10, "evidence": "..."},
  "dimension_b": {"score": 0, "max": 10, "evidence": "..."},
  "total": 0,
  "max_total": 20,
  "pass": true,
  "summary": "one line summary"
}
\```

Set `pass` to `true` if total >= 12 (60% threshold).
```

The JSON template must include `"pass": true/false`. The `total`/`max_total` fields are optional but enable nice output formatting. Dimension sub-objects with `score`/`max` keys get printed in the verdict summary.

## Adding a code judge

Create `judges/<name>.py`:

```python
from pathlib import Path

def judge(ctx: dict) -> dict:
    """
    ctx keys:
      workdir      - str, path to agent's working directory
      agent_log    - str, path to agent.log
      scenario_dir - str, path to scenario directory
      scenario     - dict, parsed scenario.yaml
      results_dir  - str, where to write outputs
      model        - str, which LLM was used
      judge_config - dict, optional per-judge config from scenario.yaml
    """
    workdir = Path(ctx["workdir"])

    # Example: check that run.sh exists
    run_sh = workdir / "stack" / "run.sh"
    if not run_sh.exists():
        return {"pass": False, "summary": "no run.sh found"}

    return {"pass": True, "summary": "run.sh exists"}
```

The returned dict must include `"pass": bool`. Everything else is optional and goes into `verdicts.json`.

## Configuring per scenario

In `scenario.yaml`:

```yaml
judges:
  - correctness           # code judge — CSV comparison
  - code_quality          # prompt judge — LLM scores code
  - kg_compliance         # prompt judge — checks KB principles
  - name: code_quality    # with config override:
    config:
      judge_model: opus   # use Opus instead of Sonnet for this judge
```

Judge configs are passed as `ctx["judge_config"]` to both code and prompt judges.

## Available judges

| Judge | Type | What it checks | Pass condition |
|-------|------|---------------|----------------|
| `correctness` | code | Exports tables from agent's DuckDB/SQLite, compares column-by-column against ground truth CSVs | All models pass (every column matches within 1% numeric tolerance) |
| `code_quality` | prompt | Structure, error handling, readability, documentation (4 x 0-10) | Total >= 24/40 |
| `kg_compliance` | prompt | Tier 1 violations (EU sovereignty, OSS, local-first), Tier 2 deviations, anti-patterns | No Tier 1 violations |

## How the correctness judge works

The `correctness.py` judge is the primary deterministic check:

1. **Find the database** — searches agent's workdir for `*.duckdb` files (recursively). Falls back to `*.sqlite` / `*.db`.
2. **Export models** — for each expected model in `scenario.yaml`, runs `SELECT * FROM <name> ORDER BY 1,2` via CLI. Searches all schemas if the default schema doesn't have the table.
3. **Compare** — for each column in ground truth:
   - Finds matching column in output (case-insensitive)
   - Compares value-by-value: nulls, numerics (1% tolerance), strings (exact after strip)
4. **Verdict** — a model passes if zero missing columns and zero mismatched columns. Overall pass requires all models to pass.

## Debugging a failed correctness check

```bash
# Run standalone check
python src/judges/check.py src/scenarios/github /path/to/agent/workdir/_judge_output

# Or export manually and inspect
duckdb /path/to/agent/warehouse.duckdb -csv "SELECT * FROM github__issues ORDER BY 1,2 LIMIT 5;"

# Compare specific columns
diff <(cut -d, -f1 gt/github/github__issues.csv | sort) \
     <(cut -d, -f1 output/github__issues.csv | sort)
```
