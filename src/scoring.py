"""IntlEconAgent composite scoring.

score(pair) = sum over frameworks of (weight_f * score_f(pair)),
then hard-filter pairs violating the new-trade-link constraint.
"""

from dataclasses import dataclass


@dataclass
class Pair:
    product: str
    country: str
    rca_score: float          # [0,1] comparative advantage (RCA-normalized)
    gravity_score: float      # [0,1] gravity potential
    undertraded_bonus: float  # [0,1] (predicted - actual) / predicted trade
    existing_trade_usd: float
    extra_frameworks: dict    # name -> [0,1] score


DEFAULT_WEIGHTS = {
    "comparative_advantage": 0.40,
    "gravity": 0.30,
}
CONSTRAINT_MAX_TRADE_USD = 10_000_000


def passes_constraint(p: Pair, max_trade_usd: float = CONSTRAINT_MAX_TRADE_USD) -> bool:
    return p.existing_trade_usd < max_trade_usd


def composite(p: Pair, weights: dict | None = None) -> float | None:
    """Returns composite score in [0,1], or None if the pair fails constraints."""
    if not passes_constraint(p):
        return None
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        w = weights
    extra_w = w.get("extra", 0.0)
    n_extra = max(len(p.extra_frameworks), 1)
    score = (
        w.get("comparative_advantage", 0) * p.rca_score
        + w.get("gravity", 0) * (p.gravity_score + p.undertraded_bonus) / 2
        + extra_w * sum(p.extra_frameworks.values()) / n_extra
    )
    return round(min(max(score, 0.0), 1.0), 4)


def rank(pairs: list[Pair], weights: dict | None = None) -> list[tuple[Pair, float]]:
    scored = [(p, composite(p, weights)) for p in pairs]
    scored = [(p, s) for p, s in scored if s is not None]
    return sorted(scored, key=lambda x: x[1], reverse=True)
