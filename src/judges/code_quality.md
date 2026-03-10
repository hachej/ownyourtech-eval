# Code Quality Judge

Score the agent's solution on code quality. Be concise and evidence-based.

## Dimensions

### Structure & Modularity (0-10)
Is the code organized into logical units? Are extract/transform/load separated?
Are there multiple files or one monolith?

### Error Handling (0-10)
Does the code handle failures? Retries, validation, cleanup?
Are errors logged with context or silently swallowed?

### Readability (0-10)
Meaningful names? Shallow nesting? Can a new engineer follow it?

### Documentation (0-10)
README with run instructions? Logging/progress output? Comments on non-obvious logic?

## Output

Respond with ONLY a JSON object:

```json
{
  "structure": {"score": 0, "max": 10, "evidence": "..."},
  "error_handling": {"score": 0, "max": 10, "evidence": "..."},
  "readability": {"score": 0, "max": 10, "evidence": "..."},
  "documentation": {"score": 0, "max": 10, "evidence": "..."},
  "total": 0,
  "max_total": 40,
  "pass": true
}
```

Set `pass` to `true` if total >= 24 (60% threshold).
