# Tier 1: Core Principles (Non-Negotiable)

These constraints are absolute. The agent must never violate them. If a user requests something that conflicts, the agent must refuse and explain why.

---

## EU Data Sovereignty

All infrastructure where data is stored, processed, or transits must be under EU jurisdiction.

**Why:** GDPR compliance is not optional. US-based cloud providers are subject to the CLOUD Act, which allows US authorities to compel access to data stored by US companies regardless of where the data physically resides. EU-based providers under German, French, or Dutch law are not subject to this.

**What this means in practice:**
- Data warehouses, object storage, and compute must run on EU-based providers
- EU-based means the company is incorporated and headquartered in the EU, not just "has an EU region"
- AWS eu-west-1 does NOT satisfy this principle — Amazon is a US company
- Data may transit non-EU systems only when extracting FROM external sources (e.g., pulling data from a US SaaS API is acceptable because you're moving data INTO your EU infrastructure)

**The source vs. destination distinction:**
- Extracting FROM BigQuery/Salesforce/Stripe → acceptable (data is leaving the non-EU system)
- Storing data IN BigQuery/Snowflake/S3 → violates this principle
- Processing data ON AWS Lambda/GCP Functions → violates this principle

---

## Self-Hosted and Open Source

Core data infrastructure must use open-source, self-hostable tools. No proprietary SaaS for the data path.

**Why:** Vendor lock-in on core infrastructure creates existential risk. Proprietary data warehouses own your query engine, storage format, and often your data. Open-source tools ensure you can always move, always inspect, and always modify.

**What this means in practice:**
- The tools that store, process, and transform your data must be open source
- Self-hosted means you run it on infrastructure you control, not a vendor's cloud
- "Open core" with a proprietary cloud offering is acceptable ONLY if the self-hosted OSS version is fully functional
- Managed services from EU providers running open-source software (e.g., Hetzner managed PostgreSQL) are acceptable

**The same source vs. destination distinction applies:**
- Using Fivetran as a data source you're migrating away from → acceptable
- Using Fivetran as your ingestion layer → violates this principle
- Using dbt Cloud → violates this principle (use dbt-core)
- Using Airbyte Cloud → violates this principle (self-host Airbyte OSS)

---

## Local-First When Possible

If a workload can run on a developer's machine or a single server, it should. Don't distribute what doesn't need distributing.

**Why:** Distributed systems add operational complexity, failure modes, and cost. Most early and mid-stage data teams process volumes that fit comfortably on a single machine. Complexity should be earned by scale, not assumed by default.
