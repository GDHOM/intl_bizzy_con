"""Gravity prediction helper.

Expected trade between France and a destination country:

    predicted = G * (GDP_fra * GDP_dest) / distance_km

G is calibrated so that the sum of predicted trade across the candidate set
matches the sum of actual France-origin trade across the same set (when actual
data is supplied). Without calibration data, a unit constant is used and the
result is only valid relative to other candidates.
"""

import csv
import pathlib
from dataclasses import dataclass

DATA = pathlib.Path(__file__).resolve().parents[1] / "data"


@dataclass
class Country:
    name: str
    iso: str
    gdp_usd: float
    cop_lat: float = 0.0
    cop_lon: float = 0.0
    distance_cop_km: float = 0.0


def load_countries(path=None) -> list[Country]:
    """Load candidate countries from data/countries.csv (CoP distance standard)."""
    path = path or DATA / "countries.csv"
    with open(path) as f:
        return [
            Country(
                name=row["name"],
                iso=row["iso"],
                gdp_usd=float(row["gdp_usd"]),
                cop_lat=float(row["cop_lat"]),
                cop_lon=float(row["cop_lon"]),
                distance_cop_km=float(row["distance_cop_km"]),
            )
            for row in csv.DictReader(f)
        ]


def gravity_mass(gdp_i: float, gdp_j: float, distance_km: float) -> float:
    """Raw gravity term (GDP_i * GDP_j) / distance, in USD*USD per km."""
    if distance_km <= 0:
        raise ValueError("distance_km must be positive")
    return (gdp_i * gdp_j) / distance_km


def calibrate_constant(pairs: list[tuple[float, float]]) -> float:
    """Calibrate G from (predicted_raw, actual) pairs by least squares through origin."""
    if not pairs:
        return 1.0
    num = sum(raw * actual for raw, actual in pairs)
    den = sum(raw * raw for raw, _ in pairs)
    if den == 0:
        return 1.0
    return num / den


def predict_trade(
    gdp_france_usd: float,
    dest: Country,
    g: float = 1.0,
) -> float:
    """Predicted France -> dest trade value in arbitrary units (USD if G calibrated)."""
    return g * gravity_mass(gdp_france_usd, dest.gdp_usd, dest.distance_cop_km)


def undertraded_ratio(predicted: float, actual: float) -> float:
    """(predicted - actual) / predicted, clamped to [0, 1]."""
    if predicted <= 0:
        return 0.0
    ratio = (predicted - actual) / predicted
    return min(max(ratio, 0.0), 1.0)
