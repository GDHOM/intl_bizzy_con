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

## Hard constraint (filter, not penalty)

A pair survives only if France→destination exports of the product are
**< $10M/year** (or the link is nascent: < 3 years of recorded flows).
Failing pairs are excluded from ranking regardless of score.

## Change log

| Date | Version | Change |
|---|---|---|
| (init) | 1.0 | Default weights: comparative advantage 0.40, gravity 0.30, extras 0.30 shared |

Every weight change gets a dated entry in the change log above.
