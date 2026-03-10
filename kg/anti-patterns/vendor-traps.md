# Anti-Pattern: Vendor Traps

Patterns that create lock-in, compliance risk, or unnecessary cost. These often feel like shortcuts but become constraints.

---

## The "Free Tier" Trap

Cloud vendors offer generous free tiers to create switching costs. By the time you outgrow the free tier, your data, queries, and workflows are deeply integrated.

**Examples:**
- Snowflake credits for startups → proprietary storage format, can't export efficiently at scale
- BigQuery free tier → your SQL uses BigQuery-specific syntax (STRUCT, UNNEST patterns)
- dbt Cloud free tier → your project depends on cloud-specific features (environment management, scheduling)

**Mitigation:** Use tools where the free version and the paid version are the same software (open-source core). PostgreSQL is PostgreSQL whether you run it on your laptop or a server.

---

## The "Managed Service" Trap

"We'll manage it so you don't have to" often means "we'll own your data path so you can't leave."

**Acceptable managed services:**
- EU provider running open-source software (Hetzner managed PostgreSQL)
- Services where the underlying tech is standard and portable (S3-compatible storage)

**Dangerous managed services:**
- Services with proprietary query engines (Snowflake, BigQuery)
- Services that add proprietary features on top of open source (Databricks runtime extensions)
- Services where export is technically possible but practically painful

---

## The "Just Use AWS" Trap

AWS is the default for most engineers because it's what they know. But for EU data teams:

- **Legal risk:** US CLOUD Act allows compelled access to data regardless of region
- **Cost opacity:** Egress fees, cross-AZ transfer, NAT gateway charges add up invisibly
- **Over-complexity:** 200+ services when you need 3 (compute, storage, database)

Hetzner does what most data teams need at 1/5th the cost with zero legal ambiguity.

---

## The "Best Tool for the Job" Trap

Using the theoretically optimal tool for each component leads to a Frankenstein stack:
- Fivetran for ingestion + Snowflake for storage + dbt Cloud for transforms + Looker for BI
- Five vendors, five contracts, five sets of credentials, five points of failure

**The boring alternative:** dlt + DuckDB/PostgreSQL + dbt-core + Metabase. Four open-source tools, one Python environment, one server, zero vendor contracts.

Consistency and simplicity beat component-level optimization every time.

---

## The "Enterprise-Ready" Trap

Choosing tools because they're "enterprise-ready" when you're not an enterprise:

- **RBAC and SSO** — you have 3 people, you don't need role-based access control
- **Multi-tenancy** — you have one client (yourself)
- **SLA guarantees** — you're the only user, uptime is "did I run the script?"
- **Audit logging** — git history is your audit log at this stage

Enterprise features are for enterprises. Early-stage teams pay for complexity they'll never use.

---

## Detection Checklist

Before adding any tool or service, ask:

1. **Can I export all my data in a standard format?** (If no → vendor trap)
2. **Can I run this on my own infrastructure?** (If no → dependency risk)
3. **Is the company EU-based?** (If no → compliance risk for data path components)
4. **Does the free/open version do everything I need?** (If no → evaluate whether the paid features are actually needed)
5. **Am I choosing this because it's the best, or because it's the default?** (If default → reconsider)
