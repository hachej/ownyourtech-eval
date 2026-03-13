# OwnYourTech Eval Value Ladder

> The lab that makes the knowledge base better — from a single scenario to a multi-domain, multi-agent KB fine-tuning system.

**Last Updated:** March 2026

---

## How to Read This

OwnYourTech Eval's value story is an ordered progression of **12 levels**. Each level is independently valuable and compounds toward the end state: a comprehensive eval lab that continuously improves the OwnYourTech knowledge base across all tech domains and agent frameworks.

Levels build on each other. Lower levels are prerequisites for higher ones.

**Status key:**
- **shipped** — Working in the current codebase
- **building** — Active development
- **designed** — Architecture defined, not yet built
- **planned** — Scope understood, design pending
- **future** — Requires capabilities not yet in place

---

## Status Summary

| Level | Name | Tier | Status |
|-------|------|------|--------|
| L01 | Single Scenario | Core Lab | shipped |
| L02 | Deterministic Correctness | Core Lab | shipped |
| L03 | LLM Quality Judges | Core Lab | shipped |
| L04 | KB Compliance Judge | Core Lab | shipped |
| L05 | Multi-Scenario (Data Engineering) | Scenario Breadth | designed |
| L06 | Cross-Domain Scenarios | Scenario Breadth | planned |
| L07 | Multi-Agent Runner | Agent Coverage | planned |
| L08 | Model Comparison & Recommendations | Agent Coverage | planned |
| L09 | KB Feedback Loop | KB Fine-Tuning | future |
| L10 | Eval Dashboard | Reporting | future |
| L11 | Community Scenarios | Community | future |
| L12 | Continuous Eval & Regression | Operations | future |

---

## Tier 1: Core Lab (L01-L04)

*One scenario, fully scored. Proves the lab works.*

These levels deliver value the moment someone runs `eval.sh github`. The output is a complete verdict: correctness, code quality, and KB compliance — the three dimensions that tell us whether the KB guided the agent well.

---

### L01: Single Scenario
> "A realistic multi-source ELT challenge with deterministic data."

**Status:** shipped

**What it delivers:** The `github` scenario — 14 source tables across 5 source types (Postgres, MongoDB, S3, REST API, flat files), 6 expected output models, Docker-based reproducibility.

**Why it matters:** The lab needs at least one real scenario to produce signals. The github scenario has the complexity of real data engineering: multiple source types, joins across systems, time-based aggregations. It exercises the KB's data engineering principles end-to-end.

---

### L02: Deterministic Correctness
> "CSV diff against ground truth — every column, every row, 1% tolerance."

**Status:** shipped

**What it delivers:** The `correctness` judge — finds the agent's database (DuckDB or SQLite), exports each model with `ORDER BY 1,2`, compares column-by-column against ground truth. Numeric tolerance: 1%. Case-insensitive column matching.

**Why it matters:** Correctness is the foundation. If the KB's principles guide the agent to the right tech but the agent produces wrong data, we need to know. Deterministic comparison means no flaky signals — it either matches or it doesn't.

---

### L03: LLM Quality Judges
> "Structure, error handling, readability, documentation — scored by an LLM against a rubric."

**Status:** shipped

**What it delivers:** The `code_quality` judge — scores 4 dimensions (0-10 each), pass threshold 60%. The framework auto-injects the spec and agent's code into the LLM prompt.

**Why it matters:** The KB should guide agents toward good code, not just correct code. If agents following the KB produce spaghetti code with no error handling, that's a signal the KB needs implementation patterns, not just technology choices.

---

### L04: KB Compliance Judge
> "Tier 1 violations auto-fail. Tier 2 deviations need justification. Anti-patterns flagged."

**Status:** shipped

**What it delivers:** The `kg_compliance` judge — checks technology choices against OwnYourTech principles. Tier 1 (EU sovereignty, open source, local-first) violations are automatic failures. Checks for over-engineering, vendor lock-in, hardcoded credentials.

**Why it matters:** This is the primary signal for KB fine-tuning. When agents fail compliance, we ask: was the principle clear enough? Was the default tech obvious? Did the KB entry exist? Every compliance failure is a potential KB improvement.

---

## Tier 2: Scenario Breadth (L05-L06)

*More scenarios, more domains. The KB gets tested more broadly.*

---

### L05: Multi-Scenario (Data Engineering)
> "Five data engineering scenarios covering different complexity levels and source combinations."

**Status:** designed

**What it delivers:** Additional data engineering scenarios beyond github — e-commerce analytics, IoT time-series, financial reporting, SaaS metrics. Graduated difficulty: simple (2 sources, 2 models) to complex (5+ sources, 10+ models). Each exercises different KB principles.

**Why it matters:** A single scenario tells us about the KB's guidance for one specific task. Five scenarios reveal patterns: which principles consistently produce good results, which are too vague for agents to act on, which are missing entirely. The KB coverage map starts to take shape.

---

### L06: Cross-Domain Scenarios
> "Beyond data engineering — email servers, infrastructure, application hosting, DevOps."

**Status:** planned

**What it delivers:** Scenarios in entirely new tech domains. An email server scenario (Postfix + Dovecot + DNS). An infrastructure scenario (reverse proxy + TLS + monitoring). A deployment scenario (container orchestration + CI/CD). Each domain exercises a different section of the KB.

**Why it matters:** OwnYourTech covers all of tech, not just data engineering. The KB has principles for networking, hosting, security, deployment — but without scenarios in those domains, those principles are untested. Cross-domain scenarios ensure the entire KB gets validated, not just the data engineering corner.

---

## Tier 3: Agent Coverage (L07-L08)

*Multiple agents, multiple models. Discover what works best where.*

---

### L07: Multi-Agent Runner
> "Test any agent framework — Claude Code, Aider, Cursor, OpenHands, custom agents."

**Status:** planned

**What it delivers:** A runner abstraction that accepts different agent backends. Same scenarios, same judges, different agents. Standardized output format for cross-agent comparison. Configuration per agent (how to invoke, how to pass the spec, how to collect output).

**Why it matters:** Different agents interpret KB guidance differently. Some are better at consulting the `oyt` CLI, some follow tier-1 principles more strictly, some handle complex multi-source tasks better. Testing across agents reveals whether KB failures are agent-specific or universal — a critical distinction for KB improvement.

---

### L08: Model Comparison & Recommendations
> "Which model builds the best email server? Which handles data pipelines best? Measured, not guessed."

**Status:** planned

**What it delivers:** Systematic comparison of models (Claude Sonnet, Claude Opus, GPT-4o, Llama, etc.) across scenarios. Performance profiles per scenario type. Recommendations: "For data engineering, use X. For infrastructure, use Y." Evidence-based, updated as models improve.

**Why it matters:** OwnYourTech doesn't just say what tech to use — it can also say what agent to use. Model recommendations per domain are a unique value-add. "Use this model for infrastructure tasks because it scores 92% compliance vs. 67% for alternatives" is concrete, actionable guidance.

---

## Tier 4: KB Fine-Tuning (L09)

*The feedback loop. The reason the lab exists.*

---

### L09: KB Feedback Loop
> "Run scenarios, identify KB gaps, improve principles, measure improvement. Systematically."

**Status:** future

**What it delivers:** A structured workflow from eval results to KB changes. Gap reports: "Scenario X fails compliance because KB entry Y is too vague for agents to act on." Before/after comparisons: "After sharpening principle Z, compliance scores improved from 60% to 85% across 3 scenarios." KB coverage tracking: which entries are exercised by scenarios, which are untested.

**Why it matters:** This is the whole point. Everything before this level builds the infrastructure for the feedback loop. L09 is where the lab starts systematically making the KB better. Without it, eval results are interesting but not actionable. With it, every scenario run is an investment in KB quality.

---

## Tier 5: Reporting (L10)

*See what's happening across the lab.*

---

### L10: Eval Dashboard
> "Visual comparison of results — across models, scenarios, domains, and time."

**Status:** future

**What it delivers:** A dashboard showing eval results across all dimensions. Compare models side-by-side per scenario. Track compliance scores over time as the KB improves. Identify the weakest KB areas (lowest compliance scores). Drill into individual judge verdicts.

**Why it matters:** The lab generates a lot of data. A dashboard makes patterns visible: which domains need KB work, which models are improving, where the biggest gaps remain. It turns the eval from a command-line tool into an operational view of KB health.

---

## Tier 6: Community & Operations (L11-L12)

*Broader participation, continuous operation.*

---

### L11: Community Scenarios
> "Anyone can contribute a scenario — data, spec, ground truth, judges. More coverage for the KB."

**Status:** future

**What it delivers:** A contribution workflow for community scenarios. Templates, validation scripts, CI checks that verify ground truth consistency. Community members bring domain expertise that expands KB coverage.

**Why it matters:** No single team can cover every tech domain. Community scenarios bring real-world tasks from infrastructure engineers, DevOps teams, and data engineers. Every contributed scenario is another test for the KB — more coverage, more signals, better principles.

---

### L12: Continuous Eval & Regression
> "Run the full suite on every KB change. Catch regressions. Track improvement."

**Status:** future

**What it delivers:** CI/CD integration that runs the eval suite on KB updates. Regression alerts when compliance scores drop. Automated before/after reports. A quality gate for KB changes: "This KB update improves data engineering compliance by 8% but regresses infrastructure compliance by 3%."

**Why it matters:** The feedback loop (L09) is manual — someone runs evals and analyzes results. Continuous eval automates it. Every KB change is validated against the full scenario suite before it ships. The KB never gets worse, only better.

---

## The End State

The 12 levels build toward a **KB fine-tuning system**: a comprehensive lab that runs real-world scenarios across all tech domains, compares models and agents, and feeds results back into the OwnYourTech knowledge base.

```
+-----------------------------------------------------------------------+
|                     KB FINE-TUNING SYSTEM                               |
|                                                                        |
|   Every scenario x every agent x every model                           |
|   Scored by: correctness, quality, compliance                          |
|   Fed back into: KB improvements, model recommendations               |
|                                                                        |
|   Built progressively:                                                 |
|   L01-L04  ->  The lab (scenario, judges, compliance)                  |
|   L05-L06  ->  The coverage (data eng + cross-domain scenarios)        |
|   L07-L08  ->  The reach (multi-agent, model comparison)               |
|   L09      ->  The loop (KB feedback, gap analysis)                    |
|   L10      ->  The visibility (dashboard)                              |
|   L11-L12  ->  The scale (community scenarios, continuous eval)        |
|                                                                        |
+-----------------------------------------------------------------------+
```

Each level is independently valuable. L01-L04 alone ("run one scenario, see where the KB falls short") is useful. But the compounding value makes each next level dramatically more powerful — until the entire KB is continuously validated and improved through real-world evidence.
