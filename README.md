# IntlEconAgent

Agentic workflow for choosing a French export product and a new destination
country trade link, scored with frameworks from International Business Economics
(comparative advantage, economic gravity, and others added by the team).

## How to contribute context
1. Add a JSON file to `context/structured/` (follow `schemas/context.schema.json`)
   or a Markdown file to `context/unstructured/`.
2. Open a Pull Request describing what you added and where the data came from.
3. After merge, the agent owner ingests it in the Mistral AI Work project.

## Scoring
Composite score = Σ (framework_weight × framework_score) per product × country pair,
then hard-filter for the new-trade-link constraint. See `docs/methodology.md`.

## Constraints
Recommended pair must be a new trade link: < $10M/year existing France→destination
exports of the product, or nascent (<3 years of recorded flows).
