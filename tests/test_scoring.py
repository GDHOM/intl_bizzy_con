import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from scoring import Pair, composite, passes_constraint, rank, CONSTRAINT_MAX_TRADE_USD


def make_pair(**overrides):
    defaults = dict(
        product="wine",
        country="Vietnam",
        rca_score=0.8,
        gravity_score=0.6,
        undertraded_bonus=0.5,
        existing_trade_usd=1_000_000,
        extra_frameworks={},
    )
    defaults.update(overrides)
    return Pair(**defaults)


def test_passes_constraint():
    assert passes_constraint(make_pair(existing_trade_usd=9_999_999))
    assert not passes_constraint(make_pair(existing_trade_usd=10_000_000))
    assert not passes_constraint(make_pair(existing_trade_usd=50_000_000))


def test_composite_in_range():
    p = make_pair()
    s = composite(p)
    assert s is not None
    assert 0.0 <= s <= 1.0
    # 0.40*0.8 + 0.30*(0.6+0.5)/2 = 0.32 + 0.165 = 0.485
    assert s == 0.485


def test_composite_excludes_failing_constraint():
    p = make_pair(existing_trade_usd=CONSTRAINT_MAX_TRADE_USD)
    assert composite(p) is None


def test_custom_weights():
    p = make_pair(extra_frameworks={"heckscher_ohlin": 1.0})
    s = composite(p, weights={"comparative_advantage": 0.5, "gravity": 0.2, "extra": 0.3})
    assert s is not None
    # 0.5*0.8 + 0.2*(0.6+0.5)/2 + 0.3*1.0 = 0.4 + 0.11 + 0.3 = 0.81
    assert s == 0.81


def test_rank_orders_and_filters():
    low = make_pair(product="cheese", country="Chile", rca_score=0.1, gravity_score=0.1, undertraded_bonus=0.0)
    high = make_pair(product="perfume", country="Chile", rca_score=1.0, gravity_score=1.0, undertraded_bonus=1.0)
    excluded = make_pair(product="wine", country="USA", existing_trade_usd=500_000_000)
    result = rank([low, excluded, high])
    assert [p.product for p, _ in result] == ["perfume", "cheese"]
    assert result[0][1] > result[1][1]
