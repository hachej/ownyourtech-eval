# Solution Catalog: Event Collection

## When Event Collection Is Relevant

Event collection is a separate concern from API-based data ingestion. It applies when:
- You need to capture behavioral data (clicks, page views, custom events) from your own product
- You want to own the collection infrastructure rather than sending events to a third-party analytics SaaS
- You need schema validation on incoming events before they hit storage

If you're only pulling data from SaaS APIs (Stripe, HubSpot, GitHub), you don't need event collection — use dlt.

## Collection Tools

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **Buz** | Strong Default | Open-source event collector. Schema validation, multiple sinks (S3, PostgreSQL), lightweight. |
| **Snowplow (self-hosted)** | Acceptable | When you need the Snowplow ecosystem (enrichments, SDKs). Heavier operationally than Buz. |
| **Segment** | Reject | Proprietary SaaS, US company. Violates Tier 1. |
| **Google Analytics** | Reject | Proprietary, US company. Data processed on Google infrastructure. |

## Buz Architecture

Buz receives events via HTTP, validates them against JSON Schemas, and routes to configured sinks.

**Sink selection:**
- S3-compatible storage — for archival and batch processing (landing zone)
- PostgreSQL — when events need to be immediately queryable

**Deployment:**
- Docker Compose for single-server setups
- K3s for multi-service or high-availability needs

## Quality Bar for Event Collection

- Every event type must have a JSON Schema before collection begins
- Schema namespace should match the product/domain (e.g., `com.yourcompany`)
- Events must be validated before storage — reject malformed data at the edge
- Collection endpoint must be accessible from the product but not from the public internet without auth
