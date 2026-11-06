# Runbook — Ingestion & Scoring Procedure

Deterministic procedure for every context submission and scoring run.
Follow it exactly; deviations must be recorded in the session report.

## Per-submission ingestion (any email/paste relay)

1. **Classify the input.**
   - JSON payload → structured path (below).
   - Prose, notes, articles, PDFs-as-text → unstructured path (§ Unstructured).
2. **Structured path:**
   1. Validate against `schemas/context.schema.json`
      (`python3 src/pipeline.py validate <file>`).
   2. If INVALID: report exactly which fields fail, archive nothing, request a
      corrected payload. Never silently drop or repair fields — the single
      permitted repair is `hs_code: null` → `""` for services, flagged in the
      Delta.
   3. If VALID: save to `context/structured/<product-or-topic>.json`.
   4. Run `python3 src/pipeline.py sync` to regenerate `data/*.csv` from all
      archived submissions.
   5. Update `data/verification_status.csv` if the submission changes any
      value's verification state.
3. **Unstructured path:**
   1. Save the text to `context/unstructured/YYYY-MM-DD-<slug>.md`.
   2. Extract: (a) framework definitions/formulas, (b) product/market facts,
      (c) team preferences/constraints. Label extracted facts as
      `unverified claim` unless a source and date are present.
   3. Merge into the knowledge base only what does not conflict; surface
      conflicts and ask which takes precedence. Never silently overwrite.
4. **Run tests:** `python3 -m pytest tests/ -q` must pass.
5. **Commit:** one commit per ingestion
   (`Ingest context: <topic>`), push to the working branch.
6. **Report the Knowledge Base Delta:** added / changed / conflicts, plus an
   updated constraint pre-check table when trade values changed.

## Scoring run (only when inputs are ready)

Prerequisites — a scoring run is **blocked** until all hold:

1. Every trade value in the scoring set is `verified` in
   `data/verification_status.csv` (or the team explicitly instructs to score
   on estimates, labeled as such).
2. `distance_to_france_km` is populated for every candidate country.
3. France's total exports per HS code (for RCA and the 1% constraint limb)
   is present in `data/verification_status.csv` or supplied in context.
4. All open methodology decisions (docs/methodology.md § Open decisions)
   are resolved.

Procedure:

1. `python3 src/pipeline.py score` → writes `reports/YYYY-MM-DD-scored-ranking.md`.
2. Apply the hard constraint as a filter; report excluded pairs with reasons.
3. Write the recommendation memo to `reports/YYYY-MM-DD-recommendation.md`.
4. Commit with message `Reports: scored ranking + recommendation (YYYY-MM-DD)`.

## Weight or constraint changes

Any change to weights or thresholds gets a dated entry in
`docs/methodology.md` § Change log before the next scoring run. Team decisions
always override defaults; record who decided and when.
