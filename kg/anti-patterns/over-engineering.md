# Anti-Pattern: Over-Engineering

The most common failure mode for data teams is building for scale they don't have. Every item below is a real pattern we've seen teams adopt prematurely, costing them weeks of setup and months of maintenance for zero benefit.

---

## "We need Kubernetes"

**You don't.** A single Hetzner VM handles more than most teams realize. K8s adds networking complexity, YAML sprawl, monitoring overhead, and a steep learning curve. Unless you're running 10+ services that need independent scaling, a VM with Docker Compose (or just bare processes) is simpler and more reliable.

**When you actually need it:** Multiple services with different scaling requirements, need for rolling deploys with zero downtime, team has dedicated platform engineering.

---

## "We need Airflow/Dagster for orchestration"

**You don't.** Cron + a shell script handles daily batch pipelines perfectly. Orchestration platforms add a web UI, a database, a scheduler service, and a metadata store — all for running the same `run.sh` that cron runs.

**When you actually need it:** Complex DAGs with 10+ interdependent steps, need for backfills across date ranges, multiple teams scheduling conflicting pipelines, need for retry policies with exponential backoff.

---

## "We need separate staging and production environments"

**You don't yet.** Environment parity matters when you have a team deploying changes that could break production. With 1-3 people, the overhead of maintaining two identical environments (double the infrastructure, double the data, double the config) isn't worth it.

**When you actually need it:** Team exceeds ~5 people, regulatory requirements mandate it, deployment frequency exceeds daily.

---

## "We need a data catalog"

**You don't.** dbt docs generate a searchable, explorable catalog from your schema YAML files. It includes lineage, descriptions, and test status. If you're writing good dbt documentation, you already have a data catalog.

**When you actually need it:** Multiple teams consuming data with no shared context, 100+ models where discoverability becomes hard, need for access control metadata.

---

## "We need real-time data"

**You almost certainly don't.** If your dashboards refresh daily and your stakeholders check them in the morning, hourly is overkill and streaming is absurd. Real-time data requires streaming infrastructure (Kafka, Flink, or similar) which is an order of magnitude more complex than batch.

**When you actually need it:** User-facing features that depend on event data within seconds, fraud detection, real-time personalization. If the consumer is a human looking at a dashboard, batch is fine.

---

## "We should use a semantic layer"

**Not yet.** Semantic layers (Cube, BSL, dbt metrics) add value when multiple BI tools or consumers need consistent metric definitions. If you have one BI tool and a small team, the metric definitions live in your dbt marts. That's your semantic layer.

**When you actually need it:** Multiple consumers (BI tool + API + embedded analytics) querying the same metrics, metric definitions drifting between tools, non-technical users self-serving analytics.

---

## "We need Docker for local development"

**You don't.** Python virtual environments + DuckDB + dbt-core run natively on any developer machine. Docker adds build times, volume mount issues, and "works in Docker but not locally" debugging. Save Docker for deployment to servers, not local dev.

---

## The General Rule

If you're asking "should we add X?", the answer is probably no. When you genuinely need X, you won't be asking — you'll be experiencing specific pain that X solves. Build for today's problems, not tomorrow's hypothetical scale.
