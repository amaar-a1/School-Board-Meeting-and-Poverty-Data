"""Estimated enrollment for places with no pupil count: school-age children living there.

Run after any build that rewrites docs/data/*.csv (the daily US refresh runs it too). For every row whose
Enrollment is empty (or 0, where that means "none reported"), it writes an estimate into Enrollment and says so in a
column of its own, "Enrollment estimated" (shown in tooltips, so an estimate is never taken for a count). Rows it
estimated before are estimated again, so it can be re-run. Real counts are never touched.

The estimate is the number of children of the ages the country's enrollment figures cover, from the child counts the
site already has (each rule below says which), or for countries without them, the place's population times its
region's share of those ages (inputs/estimates/*.json, from Eurostat and the HDX population statistics).
Usage: python3 data-prep/estimate_enrollment.py [FILE ...]   (default: every file with a rule)
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs", "data")
EST = os.path.join(HERE, "inputs", "estimates")
FLAG = "Enrollment estimated"


def num(v):
    try: return float(str(v).replace(",", ""))
    except (TypeError, ValueError): return None


def share(name):
    p = os.path.join(EST, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def from_column(col, factor, text):
    def rule(r):
        v = num(r.get(col))
        return (round(v * factor), text) if v else None
    return rule


def from_region_share(name, key, text):
    """Population times the share of school-age children in the place's region (inputs/estimates/NAME)."""
    data = share(name)
    def rule(r):
        if not data: return None
        sh, pop = data["share"].get(key(r)), num(r.get("Population"))
        return (round(pop * sh), text.format(region=data.get("names", {}).get(key(r), key(r)))) if sh and pop else None
    return rule


RULES = {
    "national.csv": from_column("Children Ages 5-17", 1, "Estimate: children aged 5–17 living in the district (Census, SAIPE 2024); no enrollment reported to NCES"),
    "japan.csv": from_column("Children under 15", 9 / 15, "Estimate: children aged 6–14 living in the municipality (nine fifteenths of its children under 15)"),
    "iceland.csv": from_column("Children", 10 / 18, "Estimate: children aged 6–15 living in the municipality (ten eighteenths of its children under 18); it has no school of its own"),
    "germany.csv": from_column("Children", 12 / 18, "Estimate: children aged 6–17 living in the district (twelve eighteenths of its children under 18)"),
    "belgium.csv": from_column("Children under 18", 9 / 18, "Estimate: children aged 3–11 living in the municipality (nine eighteenths of its children under 18); it has no school of its own"),
    "islands.csv": from_column("Children Ages 0-14 (estimated)", 9 / 15, "Estimate: children aged 6–14 (nine fifteenths of the estimated children aged 0–14)"),
    "croatia.csv": from_region_share("hr_7_14.json", lambda r: r["District ID"][3:], "Estimate: children aged 7–14 (primary school ages): the place's 2024 population times {region}'s share of those ages (Eurostat, 2024)"),
    "italy.csv": from_region_share("it_6_13.json", lambda r: r["District ID"][3:], "Estimate: children aged 6–13 (primary and lower secondary ages): the comune's 2024 population times {region}'s share of those ages (Eurostat, 2024)"),
    "france.csv": from_region_share("fr_3_10.json", lambda r: r["District ID"][4:], "Estimate: children aged 3–10 (nursery and primary ages) living in the commune: its population times {region}'s share of those ages (Eurostat, 2024); it has no school of its own"),
    "philippines.csv": from_region_share("ph_5_17.json", lambda r: r.get("Province", ""), "Estimate: children aged 5–17 (kindergarten to grade 12 ages): the place's 2021 population times {region}'s share of those ages (PSA projections for 2025, via HDX)"),
    "spain.csv": None,   # set below: census residents in school-level studies plus children aged 3–14
}


def spain_rule():
    data = share("es_pupils.json")
    def rule(r):
        if not data: return None
        x = data["est"].get(r["District ID"][3:])
        return (x, data["text"]) if x else None
    return rule


RULES["spain.csv"] = spain_rule()


def run(fn):
    p = os.path.join(DOCS, fn)
    rule = RULES.get(fn)
    if not rule or not os.path.exists(p): return
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    cols = list(rows[0])
    if FLAG not in cols: cols.append(FLAG)
    n = 0
    for r in rows:
        if r.get(FLAG):   # an earlier estimate: recompute
            r["Enrollment"], r[FLAG] = "", ""
        v = num(r.get("Enrollment"))
        if v:   # a real count
            continue
        got = rule(r)
        if got and got[0] > 0:
            r["Enrollment"], r[FLAG] = got[0], got[1]; n += 1
    if not any(r.get(FLAG) for r in rows): cols.remove(FLAG)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    print(fn, n, "estimated;", sum(1 for r in rows if not num(r.get("Enrollment"))), "still without")


if __name__ == "__main__":
    for fn in sys.argv[1:] or RULES: run(fn)
