import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from scoring import Pair, composite, passes_constraint, rank


def make_pair(**kw):
    base = dict(
        product="wine",
        country="VNM",
        rca_score=0.8,
        gravity_score=0.6,
        undertraded_bonus=0.5,
        existing_trade_usd=1_000_000,
        extra_frameworks={},
    )
    base.update(kw)
    return Pair(**base)


def test_passes_constraint():
    assert passes_constraint(make_pair())
    assert not passes_constraint(make_pair(existing_trade_usd=10_000_000))
    assert not passes_constraint(make_pair(existing_trade_usd=50_000_000))


def test_composite_fails_constraint_returns_none():
    assert composite(make_pair(existing_trade_usd=20_000_000)) is None


def test_composite_default_weights():
    p = make_pair()
    expected = round(min(max(0.40 * 0.8 + 0.30 * (0.6 + 0.5) / 2, 0.0), 1.0), 4)
    assert composite(p) == expected


def test_composite_extra_frameworks():
    p = make_pair(extra_frameworks={"cage": 0.5, "porters_diamond": 1.0})
    weights = {"comparative_advantage": 0.35, "gravity": 0.25, "extra": 0.30}
    expected = round(
        min(
            max(0.35 * 0.8 + 0.25 * (0.6 + 0.5) / 2 + 0.30 * 0.75, 0.0),
            1.0,
        ),
        4,
    )
    assert composite(p, weights) == expected


def test_composite_clamped_to_unit_interval():
    p = make_pair(rca_score=1.0, gravity_score=1.0, undertraded_bonus=1.0)
    assert composite(p) == round(0.40 * 1.0 + 0.30 * (1.0 + 1.0) / 2, 4)


def test_rank_orders_and_filters():
    low = make_pair(country="X", rca_score=0.2, gravity_score=0.1, undertraded_bonus=0.0)
    high = make_pair(country="Y")
    excluded = make_pair(country="Z", existing_trade_usd=100_000_000)
    ranked = rank([low, high, excluded])
    assert [p.country for p, _ in ranked] == ["Y", "X"]
