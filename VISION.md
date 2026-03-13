# OWNYOURTECH EVAL
## Product Vision Document v1

*The lab that makes the OwnYourTech knowledge base better*

**March 2026 | deepskydata**

---

## Vision Statement

> *A knowledge base is only as good as the outcomes it produces.*
> *OwnYourTech Eval is the lab where we run real-world scenarios, measure results, and discover where our principles need to be sharper.*

OwnYourTech Eval is an **open-source evaluation lab** for the OwnYourTech knowledge base. It runs AI agents through realistic technology scenarios — data pipelines, email servers, infrastructure setups — scores the results, and reveals where the KB's principles produce good outcomes and where they fall short.

The eval doesn't just test agents. It **fine-tunes the knowledge base**. Every scenario run is a signal: did the principles guide the agent to the right technology choices? Did the agent achieve a correct, compliant result? Where did the KB fail to provide enough guidance?

Over time, the lab also reveals which models and agent frameworks work best for which kinds of tasks — turning OwnYourTech into not just "what tech to use" but "what agent to use to build it."

---

## The Problem We Solve

### The Surface Problem

The OwnYourTech knowledge base defines technology principles — EU-sovereign, open-source, local-first — but **we have no systematic way to know if those principles actually produce good outcomes** when agents follow them.

### The Deeper Problem

A knowledge base without a feedback loop is just opinions. Principles that sound right in theory might be too vague for an agent to act on, might conflict in practice, or might miss edge cases that only show up in real scenarios. Without running real tasks and measuring results, the KB stays static while the world moves.

### Why This Persists

Building a proper eval lab is hard work:
- You need realistic scenarios across diverse tech domains (not just data engineering)
- You need deterministic ground truth for every expected output
- You need judges that check both correctness and principle adherence
- You need to run multiple models and agents to compare results
- You need it to be reproducible — Docker, fixed data, no external dependencies
- You need a feedback loop from results back into KB improvements

### What Changes Everything

**What if every KB change could be validated against a suite of real scenarios?**

```
KB change → Run scenarios → Score results → Compare with baseline → Accept or iterate
```

The eval lab closes the loop. The KB gets measurably better with every iteration because we can see exactly where principles produce good results and where they need refinement.

---

## The Core Loop

```
+-----------------------------------------------------------------------+
|                         THE FINE-TUNING LOOP                           |
|                                                                        |
|   1. Define scenario (task spec, sources, ground truth)                |
|   2. Run agent(s) with KB principles                                   |
|   3. Score results (correctness, quality, compliance)                  |
|   4. Identify KB gaps ("principle X was too vague for scenario Y")     |
|   5. Improve KB (sharper principles, better defaults, new entries)     |
|   6. Re-run → measure improvement                                     |
|                                                                        |
|   Side output: model/agent recommendations per scenario type           |
|                                                                        |
+-----------------------------------------------------------------------+
```

This is the fundamental insight: **the eval is not the product — the improved KB is the product.** The eval is the lab that produces it.

---

## Core Belief System

### The Keystone Belief

> **"Our knowledge base needs a feedback loop — we need to run real scenarios, measure outcomes, and discover where our principles need to be sharper, so the KB gets measurably better over time."**

### The Belief Chain

| # | Belief | Type |
|---|--------|------|
| 1 | AI agents can now build working tech infrastructure from specs | Observable reality |
| 2 | Whether the result is principled depends on the guidance the agent receives | The reframe |
| 3 | The OwnYourTech KB is that guidance — but we don't know how good it is | Gap recognition |
| 4 | We need real scenarios to stress-test the KB across diverse tech domains | Mechanism |
| **5** | **We need a reproducible lab that reveals where the KB produces good outcomes and where it falls short** | **KEYSTONE** |
| 6 | Different models and agents may handle KB guidance differently | Extension |
| 7 | If we can measure that, we can recommend the right agent for the right task | Model recommendations |
| 8 | The KB improves with every scenario run — it's a flywheel | End state |

---

## How OwnYourTech Eval Works

### Step 1: Define a Scenario

A scenario is a real-world technology task: build an ELT pipeline, set up an email server, deploy a monitoring stack. Each scenario has source materials, a task spec, and ground truth.

```
src/scenarios/github/
  scenario.yaml    # Config: sources, credentials, judges, expected models
  SPEC.md          # What the agent sees
src/data-sources/github/
  data/github/     # Source data
  gt/github/       # Ground truth
  postgres_init.sh # Load into Postgres
  mongo_init.py    # Load into MongoDB
```

Scenarios span tech domains:
- **Data engineering:** ELT pipelines, data warehousing, analytics
- **Infrastructure:** email servers, DNS, reverse proxies, monitoring
- **Application:** web apps, APIs, databases, caching
- **DevOps:** CI/CD, deployment, container orchestration

### Step 2: Run the Eval

```bash
src/eval/eval.sh github --model claude-sonnet-4-6 --budget 5.00
```

The runner:
1. Starts Docker services (scenario-specific)
2. Loads deterministic data via init scripts
3. Creates an isolated workdir with SPEC.md + CLAUDE.md (includes KB access)
4. Runs the agent
5. Runs judges on the output

### Step 3: Score and Analyze

```
results/github/20260313-143022-claude-sonnet-4-6/
  verdicts.json    # Machine-readable judge results
  agent.log        # Readable agent transcript
  meta.yaml        # Run metadata
```

Three scoring dimensions:
- **Correctness** — did the agent produce the right output? (deterministic)
- **Code quality** — is the code well-structured? (LLM judge)
- **KB compliance** — did the agent follow OwnYourTech principles? (LLM judge)

### Step 4: Feed Back into the KB

This is the key step that makes the eval a lab, not just a benchmark:

- **Compliance failures** → KB principles too vague? Add specificity.
- **Compliance passes but correctness failures** → principles correct but agent needs better guidance on implementation patterns?
- **Model A passes, Model B fails** → document model recommendations for this scenario type.
- **Consistent pattern across scenarios** → promote to a KB best practice.

---

## Scenario Domains

OwnYourTech covers all of tech — the eval lab must too. The `github` data engineering scenario is the first, but the framework supports any domain:

| Domain | Example Scenarios |
|--------|------------------|
| **Data Engineering** | ELT pipelines, data warehouses, analytics dashboards |
| **Email / Communication** | Self-hosted email server, Matrix chat, notification systems |
| **Infrastructure** | Reverse proxy, DNS, TLS certificates, monitoring |
| **Application Hosting** | Web apps, APIs, databases, caching layers |
| **DevOps** | CI/CD pipelines, container orchestration, deployment |
| **Security** | Secrets management, access control, audit logging |

Each domain exercises different parts of the KB. A data engineering scenario tests database defaults and ingestion patterns. An email server scenario tests networking principles and service hosting. Together, they provide comprehensive KB coverage.

---

## Target Users

### Primary: Ourselves (KB Developers)

**The lab operators.** We run scenarios to find KB gaps, sharpen principles, and validate improvements. The eval is our internal quality system.

### Secondary: Agent Developers

**The builders.** They want to know if their agent handles OwnYourTech principles well — and which model works best for which scenario type.

### Expansion: Teams Adopting OwnYourTech

**The users.** Teams adopting OwnYourTech principles want to verify their agents produce compliant infrastructure. The eval gives them confidence.

---

## Key Product Decisions

### 1. The Lab Serves the KB

The eval exists to make the KB better. Every design decision optimizes for the feedback loop: scenario → results → KB improvement. It's not a standalone benchmark product.

### 2. Beyond Data Engineering

OwnYourTech covers all tech. The eval framework must support scenarios across every domain — data, infrastructure, applications, DevOps. The scenario architecture is domain-agnostic by design.

### 3. Multi-Agent from the Start

Different models handle KB guidance differently. Testing across Claude, GPT, Llama, and various agent frameworks (Claude Code, Aider, Cursor, custom) reveals which combinations work best for which tasks.

### 4. Deterministic + LLM Judges

Correctness is deterministic (CSV diff, config validation). Code quality and compliance use LLM judges with structured rubrics. Both are needed.

### 5. Docker for Reproducibility

All source services run in Docker. Fixed data, fixed ports, fixed credentials. Any machine, same results.

### 6. Open Source

The eval framework, scenarios, judges, and data are open source. The KB itself is distributed via `oyt` (public on PyPI). Transparency builds trust in the principles.

---

## Success Metrics

### For the KB (Primary)

- KB compliance scores improve across scenarios after KB updates
- Fewer "principle too vague" failures per scenario
- Coverage: percentage of KB entries exercised by at least one scenario

### For the Lab

| Metric | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| Scenarios | 1 (data eng) | 5 (multi-domain) | 15+ |
| Tech domains covered | 1 | 3 | 6+ |
| Models tested | 1 | 3 | 5+ |
| Agent frameworks | 1 | 3 | 5+ |
| KB iterations informed by eval | — | 5 | 20+ |

### For Users

- *"I can see exactly which principles my agent struggles with"*
- *"The eval told me which model works best for infrastructure scenarios"*
- *"After the KB update, my compliance score went from 60% to 90%"*

---

## Summary

| Element | Description |
|---------|-------------|
| **The Problem** | The OwnYourTech KB has no feedback loop — we don't know where principles work and where they fall short |
| **Why It Persists** | Building a multi-domain, multi-agent eval lab with a KB feedback loop is hard |
| **The Insight** | The eval is a lab that fine-tunes the KB — every scenario run makes the principles sharper |
| **The Mechanism** | Scenarios -> agents with KB -> judges -> identify gaps -> improve KB -> re-run |
| **The Extension** | Compare models/agents per scenario type -> recommend the right tool for the right job |
| **The Distribution** | Open source: framework, scenarios, judges. KB via `oyt` on PyPI. |

---

> **OwnYourTech Eval: The lab that makes the knowledge base better — run real scenarios, measure outcomes, sharpen principles.**

---

*Version 1.0*
*March 2026*
*deepskydata*
