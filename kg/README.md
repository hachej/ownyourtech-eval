# BoringData Knowledge Base — Staff Engineer Edition

This knowledge base assumes the implementing agent is a competent engineer who knows how to use the tools. It does not contain step-by-step instructions, templates, or shell commands.

Instead, it provides:

- **Principles** — Tiered constraints that govern all decisions (core → strong defaults → preferences)
- **Catalog** — Curated solution recommendations with context for when each applies
- **Patterns** — Reference architectures and structural conventions
- **Anti-patterns** — What to avoid and why

## How to Use This KB

1. Start with **principles/** — these are non-negotiable and override everything else
2. Use **catalog/** to select tools — match the user's context to the right recommendation
3. Apply **patterns/** for project structure and conventions
4. Check **anti-patterns/** before finalizing — make sure you're not over-engineering

## Enforcement Behavior

- **Tier 1 violation** → Refuse. Explain why and offer alternatives.
- **Tier 2 deviation** → Warn. Explain the default choice and why it's preferred. Proceed only if the user has a specific reason.
- **Tier 3 deviation** → Note. Mention the preference but don't block.
