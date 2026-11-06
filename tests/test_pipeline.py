import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pipeline


def test_all_submissions_valid():
    files = list((ROOT / "context" / "structured").glob("*.json"))
    assert files, "no structured submissions found"
    validator = pipeline.load_schema()
    assert validator is not None
    for f in files:
        errors = list(validator.iter_errors(json.load(open(f))))
        assert not errors, f"{f.name}: {[e.message for e in errors]}"


def test_trade_links_consistent_with_status_tracker():
    import csv

    links = {(r["product"], r["to"]) for r in
             csv.DictReader(open(ROOT / "data" / "trade_links.csv"))}
    status = {(r["product"], r["to"]) for r in
              csv.DictReader(open(ROOT / "data" / "verification_status.csv"))}
    missing = links - status
    assert not missing, f"links missing from verification tracker: {missing}"


def test_countries_csv_cop_distance_populated():
    import csv

    rows = list(csv.DictReader(open(ROOT / "data" / "countries.csv")))
    assert rows, "countries.csv is empty"
    for r in rows:
        assert r["distance_cop_km"], f"missing distance_cop_km for {r['iso']}"
        float(r["cop_lat"])
        float(r["cop_lon"])
        float(r["distance_cop_km"])


def test_prereq_blockers_detected():
    blockers = pipeline.check_scoring_prereqs()
    assert not any("missing CoP distance" in b for b in blockers)
    assert any("not verified" in b for b in blockers)
