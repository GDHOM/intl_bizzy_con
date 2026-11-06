# Methodology — IntlEconAgent weighting function

**Version:** 1.0 — default weights

## Composite score

For each product × country pair, a score in [0, 1] is computed per framework,
then combined as a weighted sum:

```
composite = 0.40 * rca_score
          + 0.30 * (gravity_score + undertraded_bonus) / 2
          + extra_w * mean(extra_framework_scores)
```

| Framework | Weight | Score definition |
|---|---|---|
| Comparative advantage (Ricardo, via Balassa RCA) | 0.40 | Normalized RCA of France in the product's HS code, adjusted for the destination's own production capacity |
| Gravity model | 0.30 | (GDP_i × GDP_j) / distance normalized across the candidate set, plus under-traded bonus (predicted − actual) / predicted |
| Additional team frameworks | 0.30 total | Split evenly across any extra frameworks the team supplies; requires a team-defined score or an agreed proposal |

## Distance standard

Center-of-population (CoP) distance, from `distance_cop_km` in `data/countries.csv`.
France's CoP ≈ 47.6°N, 2.7°E (population-weighted metro centroid). Destination CoPs
are population-weighted metro centroids — labeled approximations, upgradeable to
SEDAC GPW or CEPII GeoDist values without schema change. Recorded per submission via
`frameworks[].distance_standard: "cop"` in `schemas/context.schema.json`.

## Gravity specification and data gaps

Commodity-specific gravity (Karemera, Koo, Smalls & Whiteside 2015, JEI 30(2), 240–268):

```
X_ij = B · Y_i^β1 · Y_j^β2 · D_ij^β3 · N_i^β4 · N_j^β5 · Pr_i^β6 · Pr_j^β7 · V_ij^β8
       · exp[β9·A_ij + RTA dummies + product-specific shock dummies]
```

D_ij = `distance_cop_km` (CoP). V_ij = moving std of log changes in the real
EUR→local rate, default m = 4 on annual series (Koray & Lastrapes 1989; Chowdhury 1993),
optionally Pérée & Steinherr long-run robustness. CFA-pegged destinations (XOF/XAF)
have near-zero V by construction.

Data gaps (primary source that would fill each):

- Population N_i/N_j and per-capita GDP Y — World Bank (WDI)
- Exchange-rate series and V_ij — IMF IFS
- Border dummy A_ij and RTA membership (AfCFTA, EU FTAs, ASEAN, MERCOSUR, USMCA) — WTO RTA schedules
- Per-commodity production capacity Pr — FAOSTAT / UN COMTRADE
- France's total exports per HS code (RCA denominator, 1% constraint limb) — Eurostat Comext

## Hard constraint (filter, not penalty)

A pair survives only if France→destination exports of the product are
**< $10M/year** (or the link is nascent: < 3 years of recorded flows).
Failing pairs are excluded from ranking regardless of score.

## Change log

| Date | Version | Change |
|---|---|---|
| (init) | 1.0 | Default weights: comparative advantage 0.40, gravity 0.30, extras 0.30 shared |
| (2025, team decision) | 1.1 | Scope decisions: (1) military drones merged into commercial drones — HS 8806 rows unified, military use cases assessed qualitatively via SIPRI in the paper; (2) nuclear powerplant services excluded from scoring (no HS code); its goods twin, nuclear reactor parts (HS 8401), remains; (3) recently-maturing links (e.g., wine→Vietnam, cheese→Mexico, skincare→Senegal) are preserved as VERIFY rows for discussion, not pre-emptively excluded; (4) cultural-distance effects for wine/spirits assessed qualitatively in the paper rather than as a scoring modifier at this stage. Candidate universe: 12 products × 29 countries (145 + 203 = 348 pairs). |
| (2026-11, owner decision) | 1.2 | Distance standard switched to CoP: `distance_cop_km` with `cop_lat`/`cop_lon` in `data/countries.csv`, replacing capital-based distances. Schema extended with `frameworks[].distance_standard` ("capital"|"cop") and `frameworks[].volatility_params`; country entries may carry `population`, `cop_lat`, `cop_lon`, `distance_cop_km`. Weights unchanged: the pushed team override 0.40/0.30/0.30 stands (skill default 0.40/0.40/0.20 not adopted). |
