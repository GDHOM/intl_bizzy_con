# IntlEconAgent

Agentic workflow for choosing a French export product and a new destination
country trade link, scored with frameworks from International Business Economics
(comparative advantage, economic gravity, and others added by the team).

## How to contribute context

Context arrives by email, relayed into the agent session (no PRs needed).

**Intake checklist — paste this at the top of every submission:**

```
Source:        (UN COMTRADE / Eurostat Comext / World Bank / SIPRI / EBOPS / class notes / news article — URL or citation)
Date of data:  (e.g. 2024)
Type:          structured JSON | unstructured text
Verification:  verified | estimate
Products/countries affected: ...
```

1. **Structured**: JSON valid against `schemas/context.schema.json`.
   It is archived to `context/structured/<product>.json` and synced into `data/*.csv`.
2. **Unstructured**: notes, articles, class summaries. Archived to
   `context/unstructured/YYYY-MM-DD-<slug>.md`; facts without a source are
   labeled `unverified claim`.
3. Every ingestion produces a **Knowledge Base Delta** (added / changed /
   conflicts) and updates `data/verification_status.csv`.

The full deterministic procedure is in `docs/runbook.md`.

## Scoring
Composite score = Σ (framework_weight × framework_score) per product × country pair,
then hard-filter for the new-trade-link constraint. See `docs/methodology.md`.

## Constraints
Recommended pair must be a new trade link: < $10M/year existing France→destination
exports of the product, or nascent (<3 years of recorded flows).
