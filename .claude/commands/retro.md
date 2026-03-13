---
description: Post-implementation retrospective - discover issues and create Beads tasks
allowed-tools: Bash(git:*), Bash(bd:*), Bash(python:*), Bash(python3:*), Grep, Glob, Read, Edit
---

# Retrospective

Analyze recent implementation work and discover follow-up issues.

## Instructions

### 1. Identify the Scope of Recent Work

```bash
git diff --name-only $(git merge-base HEAD main)..HEAD
```

If no changes from main, check recent commits:
```bash
git log --oneline -10 --name-only
```

### 2. Run Full Verification Suite

Run all checks and capture any failures:

```bash
# Run an eval to verify nothing is broken
src/eval/eval.sh github --model claude-sonnet-4-6 --budget 2.00

# Or just check ground truth
python src/judges/check.py src/scenarios/github src/data-sources/github/gt/github
```

Capture all warnings and errors from these checks - they become findings.

### 2a. Analyze Recent Failures

**Check for tasks that failed (moved back to plan status with failure notes):**

```bash
bd list --label plan --json
```

Look for tasks with "## Implementation Failed" in their body.

**For each failure, analyze:**

1. **Read failure notes** - Look for "## Implementation Failed" section in task body
2. **Identify category** - plan-quality, test-failures, blockers, scope-creep, abandoned
3. **Extract lesson** - What should be done differently next time?

**Promote patterns to PROGRESS.md:**

If PROGRESS.md exists, add to "Failure Patterns" section (create section if missing):

```markdown
## Failure Patterns

### <category>: <brief description>
**From:** task <id> (YYYY-MM-DD)
**Why it failed:** <specific cause>
**Lesson:** <actionable guidance for future implementations>
```

**After analysis:**
- Update task to remove failure notes if resolved
- Commit PROGRESS.md if patterns were added

```bash
git add PROGRESS.md && git commit -m "docs: add failure pattern from task <id>"
```

### 3. For Each Changed File, Analyze

**Related files to check:**
- Other files in the same directory
- Files that reference the changed file (use Grep)
- Similar patterns across the codebase

**Patterns to grep for:**
- If you fixed a judge, search for similar issues in other judges
- If you fixed an init script, check other init scripts
- If you improved eval.sh, check for similar patterns

### 4. Categorize Findings

| Category | Label | Look For |
|----------|-------|----------|
| Bug | `bug` | Failing evals, wrong ground truth, broken init scripts |
| Tech debt | `tech-debt` | Hardcoded values, missing error handling, TODOs |
| Refactoring | `refactoring` | Code duplication, inconsistent patterns |
| Enhancement | `enhancement` | Missing features, new judge ideas, new scenario ideas |
| Documentation | `documentation` | Outdated docs, missing examples, stale comments |
| Testing | `testing` | Missing test coverage, edge cases not handled |

### 5. Assess Status for Each Finding

| Status | Criteria |
|--------|----------|
| `brainstorm` | Problem unclear, multiple approaches possible, needs design decisions |
| `plan` | Problem clear, solution known, but involves multiple files/steps |
| `ready` | Trivial fix - specific file/line known, mechanical change (RARE) |

**Default to `plan`** - only use `ready` for truly trivial fixes.

### 6. Assess Priority

| Priority | Criteria |
|----------|----------|
| High | Blocking other work, causing failures, security concern |
| Medium | Should fix soon, affects eval quality |
| Low | Nice to have, cleanup, minor improvement |

### 7. Present Findings

```
## Retro Findings

| # | Category | File | Issue | Priority | Status | Effort |
|---|----------|------|-------|----------|--------|--------|
| 1 | bug | src/judges/correctness.py | Edge case in numeric comparison | Medium | plan | Medium |
| 2 | enhancement | src/scenarios/ | Missing e-commerce scenario | Low | brainstorm | Large |
| 3 | documentation | AGENTS.md | Stale init script example | Low | ready | Quick win |

Create all N tasks? (y/n)
```

### 8. If Confirmed, Create Tasks

For each finding, create a Beads task:

```bash
bd create "<Task title>" --labels <status> -d "## Problem\n<description of issue>\n\n## Context\nDiscovered during retro after <recent work description>.\n\n## Solution\n<suggested fix if known>\n\n## Files\n- \`<file path>\`\n\n---\n*Priority: <priority> | Effort: <effort>*\n*Created via /retro*"
```

### 9. Summarize

```
Created N tasks:
- <id>: <title> (status: <status>)
- <id>: <title> (status: <status>)
```

### 10. Review PROGRESS.md for Pattern Promotion

After creating issues, analyze recent session entries for promotable patterns:

1. **Read recent entries** from PROGRESS.md Session Log

2. **Identify candidates** - patterns that are:
   - Transferable to other issues/contexts
   - Not obvious from documentation
   - You can articulate WHY in one sentence

3. **For each promotable pattern**, add to Reusable Patterns section:

```markdown
### [Pattern Name]
**From:** #<issue> (YYYY-MM-DD)
**Why:** <one sentence explaining transferability>
**Pattern:** <the actual pattern/approach>
```

4. **Commit if patterns promoted:**

```bash
git add PROGRESS.md
git commit -m "docs: promote patterns from recent implementation work"
```

**Promotion criteria:**
- Transferable: Would help with future similar work
- Non-obvious: Not in official docs or easy to discover
- Articulable: Can explain value in one sentence
