# Judges

Composable evaluation modules. Two types:

- **Prompt judges** (`.md`) — A markdown rubric sent to an LLM. Just write a prompt.
- **Code judges** (`.py`) — Python code for deterministic checks. Implement `judge(ctx) -> dict`.

Prompt judges take priority: if both `foo.md` and `foo.py` exist, the prompt wins.

## Adding a prompt judge

Create `judges/<name>.md` with:
1. Scoring dimensions
2. What to look for
3. Output format (must end with a JSON template containing `"pass": true/false`)

That's it. The runner injects the agent's source code and spec automatically.

## Adding a code judge

Create `judges/<name>.py` with:

```python
def judge(ctx: dict) -> dict:
    return {"pass": True, "summary": "...", ...}
```

## Configuring per scenario

In `scenario.yaml`:

```yaml
judges:
  - correctness           # code judge (CSV comparison)
  - code_quality          # prompt judge (LLM scores structure, errors, readability)
  - kg_compliance         # prompt judge (checks KG principles)
  - name: code_quality    # with config override
    config:
      judge_model: opus
```

## Available judges

| Judge | Type | What it checks |
|-------|------|---------------|
| `correctness` | code (.py) | Output CSVs vs ground truth |
| `code_quality` | prompt (.md) | Structure, error handling, readability, docs |
| `kg_compliance` | prompt (.md) | Tier 1/2/3 principle adherence |
