"""IntlEconAgent pipeline driver.

Commands:
    validate <file.json>   validate one structured submission against the schema
    sync                   regenerate data/*.csv from context/structured/*.json
    score                  compute ranked pairs -> reports/<date>-scored-ranking.md

Scoring is blocked until prerequisites in docs/runbook.md are met.
"""

import csv
import json
import pathlib
import sys
import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "context" / "structured"
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
SCHEMA = ROOT / "schemas" / "context.schema.json"

sys.path.insert(0, str(ROOT / "src"))
from scoring import Pair, rank  # noqa: E402


def load_schema():
    try:
        from jsonschema import Draft202012Validator
        return Draft202012Validator(json.load(open(SCHEMA)))
    except ImportError:
        print("jsonschema not installed; run: pip install jsonschema")
        return None


def cmd_validate(path):
    validator = load_schema()
    if validator is None:
        return 1
    data = json.load(open(path))
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        for e in errors:
            print(f"INVALID {path} at {list(e.path)}: {e.message}")
        return 1
    print(f"VALID {path}")
    return 0


def iter_submissions():
    for f in sorted(CONTEXT.glob("*.json")):
        yield json.load(open(f))


def cmd_sync():
    countries_csv = DATA / "countries.csv"
    by_iso, by_name = {}, {}
    if countries_csv.exists():
        with open(countries_csv) as f:
            for row in csv.DictReader(f):
                by_iso[row["iso"]] = row
                by_name[row["name"].lower()] = row
    countries = dict(by_iso)
    trade = []
    for sub in iter_submissions():
        for c in sub.get("countries", []):
            iso = c.get("iso") or c["name"]
            row = by_iso.get(iso) or by_name.get(c["name"].lower())
            if row is None:
                row = {"iso": iso, "name": c["name"]}
                countries[iso] = row
            for key in ("name", "gdp_usd", "cop_lat", "cop_lon", "distance_cop_km"):
                if key in c:
                    row[key] = c[key]
        for t in sub.get("trade_links", []):
            trade.append(
                (t["product"], t["from"], t["to"], t["value_usd"], t["year"],
                 t.get("source", "estimate"))
            )

    with open(countries_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["iso", "name", "gdp_usd", "cop_lat", "cop_lon", "distance_cop_km"])
        for iso in sorted(countries):
            row = countries[iso]
            w.writerow([iso, row.get("name", ""), row.get("gdp_usd", ""),
                        row.get("cop_lat", ""), row.get("cop_lon", ""),
                        row.get("distance_cop_km", "")])

    with open(DATA / "trade_links.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["product", "from", "to", "value_usd", "year", "source"])
        for row in trade:
            w.writerow(row)

    print(f"synced {len(countries)} countries, {len(trade)} trade links")
    return 0


def check_scoring_prereqs():
    blockers = []
    with open(DATA / "countries.csv") as f:
        for row in csv.DictReader(f):
            if not row["distance_cop_km"] or not row["cop_lat"] or not row["cop_lon"]:
                blockers.append(f"missing CoP distance for {row['name']}")
    status = list(csv.DictReader(open(DATA / "verification_status.csv")))
    unverified = [r for r in status if r["verification"] != "verified"]
    if unverified:
        blockers.append(f"{len(unverified)} trade values not verified")
    if not (ROOT / "docs" / "methodology.md").read_text().count("Open decisions"):
        pass  # section exists check is informational only
    return blockers


def cmd_score():
    blockers = check_scoring_prereqs()
    if blockers:
        print("SCORING BLOCKED:")
        for b in blockers:
            print(f"  - {b}")
        print("Resolve prerequisites in docs/runbook.md or instruct "
              "the agent to score on estimates (labeled as such).")
        return 1
    pairs = json.load(open(DATA / "pair_inputs.json"))
    ranked = rank([Pair(**p) for p in pairs])
    today = datetime.date.today().isoformat()
    out = REPORTS / f"{today}-scored-ranking.md"
    REPORTS.mkdir(exist_ok=True)
    with open(out, "w") as f:
        f.write(f"# Scored ranking — {today}\n\n")
        f.write("| Rank | Product | Country | Composite |\n|---|---|---|---|\n")
        for i, (p, s) in enumerate(ranked, 1):
            f.write(f"| {i} | {p.product} | {p.country} | {s} |\n")
    print(f"wrote {out}")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "validate" and len(sys.argv) == 3:
        return cmd_validate(sys.argv[2])
    if cmd == "sync":
        return cmd_sync()
    if cmd == "score":
        return cmd_score()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
