"""Gravity prediction helper.

Estimates expected bilateral trade volume with the basic gravity formulation:

    predicted_trade(i, j) ~ (GDP_i * GDP_j) / distance_ij

and computes the "under-traded" ratio used as a bonus in composite scoring.
"""

import math


def predicted_trade(gdp_i: float, gdp_j: float, distance_km: float) -> float:
    """Raw gravity prediction (unscaled). Distance must be > 0."""
    if distance_km <= 0:
        raise ValueError("distance_km must be positive")
    return (gdp_i * gdp_j) / distance_km


def normalize(values: list[float]) -> list[float]:
    """Min-max normalize a list of non-negative values to [0, 1]."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def undertraded_ratio(predicted: float, actual: float) -> float:
    """(predicted - actual) / predicted, clamped to [0, 1]."""
    if predicted <= 0:
        return 0.0
    return min(max((predicted - actual) / predicted, 0.0), 1.0)
