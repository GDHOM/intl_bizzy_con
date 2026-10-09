# Methodology

## Version 1.0 (initial scaffold)

Composite score per product × country pair:

```
score = w_ca * rca_score
      + w_gr  * (gravity_score + undertraded_bonus) / 2
      + w_ex  * mean(extra_framework scores)
```

### Default weights

| Framework | Weight | Key |
|---|---|---|
| Comparative advantage (Ricardo, RCA/Balassa) | 0.40 | `comparative_advantage` |
| Gravity model | 0.30 | `gravity` |
| Additional frameworks (team-supplied) | 0.30 total, split equally | `extra` |

### Framework scores

- **Comparative advantage**: normalized RCA of France in the product's HS code
  (RCA = product export share of France / product export share of world),
  adjusted by the destination's own production capacity in that product.
- **Gravity**: `(GDP_i × GDP_j) / distance_ij` normalized across the candidate
  set (see `src/gravity.py`), plus an under-traded bonus proportional to
  `(predicted − actual) / predicted` trade.

### Hard constraints (filter, not penalty)

A pair is excluded when it fails the new-trade-link constraint:

- France→destination exports of the product **≥ $10M/year**, or
- **≥ 1%** of France's total exports of that HS code, and
- the link is **not nascent** (≥ 3 years of recorded flows).

Destinations must be plausible markets: no failed states, no embargoed
destinations, no countries where the product is illegal.

## Change log

- **v1.0** — initial defaults (0.40 / 0.30 / 0.30). Every weight change must be
  recorded here with a date and rationale.
