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

## Open decisions (blocking scoring for affected products)

1. **Drones: merge or split?** Military and commercial drones share HS 8806;
   customs data cannot separate them. Either merge products 3 and 4, or
   source military flows from SIPRI Arms Transfers Database.
2. **Nuclear services under Ricardo/gravity.** A service with no HS code;
   RCA must be inferred from installed-base share and EDF/Framatome/Orano
   order books. Decide the adaptation (or drop the product).
3. **Do growth-stage links count as "new"?** Wine→Vietnam and cheese→Mexico
   may exceed $10M but are recently-maturing. Confirm with the professor
   whether the constraint is value-only or admits a recency/nascent exception.
4. **CFM JV nationality.** Engines are 50% GE. Confirm the paper's stance;
   customs already attributes French-shipped engines to France.
5. **hs_code null handling.** Services submissions use `""` for services
   (schema requires string). Confirm, or amend the schema to allow null.

## Change log

- **v1.0** — initial defaults (0.40 / 0.30 / 0.30). Every weight change must be
  recorded here with a date and rationale.
