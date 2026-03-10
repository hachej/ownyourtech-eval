# Solution Catalog: Compute & Infrastructure

## Cloud Providers

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **Hetzner Cloud** | Strong Default | German company, GDPR-native, cost-effective (~€4-8/mo base). Best for most data workloads. |
| **OVH** | Acceptable | French jurisdiction. Consider when French data residency is specifically required. |
| **Scaleway** | Acceptable | French company. Consider when GPU workloads are needed. |
| **AWS** | Reject | US company, CLOUD Act exposure. Violates Tier 1 EU sovereignty. |
| **GCP** | Reject | US company. Same as AWS. |
| **Azure** | Reject | US company. Same as AWS. |

## Infrastructure Management

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **Terraform** | Strong Default | Reproducible, plannable, version-controlled. Industry standard for IaC. |
| **Pulumi** | Acceptable | When team strongly prefers programming language over HCL. Same principles apply. |
| **Click-ops** | Reject | Not reproducible, not auditable, not scalable. Never. |

## Terraform State Storage

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **Local state** | Default for solo | Single developer, local development, getting started fast. |
| **Remote S3-compatible** | Default for teams | Multiple developers, CI/CD, production environments. Use Hetzner Object Storage or MinIO. |

## Container Registry

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **None** | Default | Most early-stage setups don't need containerization. Skip until you need it. |
| **GHCR (GitHub Container Registry)** | Acceptable | When containerized deployment is needed. Free for public repos, integrated with GitHub Actions. |

## CI/CD

| Solution | Recommendation | Context |
|----------|---------------|---------|
| **GitHub Actions** | Strong Default | Tight integration with GitHub repos, free tier sufficient for most data teams. |
| **Self-hosted runners** | Acceptable | When build secrets or network access require it. |

## Choosing a Server Size

Ask these questions:
1. How much data will be processed? < 10GB in memory → smallest VM (cx22 equivalent)
2. Will DuckDB run on this machine? → needs RAM ≈ 2x largest table
3. Will PostgreSQL serve concurrent queries? → allocate 256MB per expected connection
4. When in doubt, start small and resize — cloud VMs scale up trivially
