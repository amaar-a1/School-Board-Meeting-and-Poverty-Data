"""Population and people per km² for Canadian boards, and children aged 5–17 on the First Nations reserves.

Input: inputs/canada/canada_population_2021.json, made on GitHub's runner by
inputs/canada/canada_population_2021_runner.py (it needs geopandas) from the 2021 Census:
  - population by census subdivision (CSD): Statistics Canada table 98-10-0002-01 (population and dwelling
    counts) and 98-10-0022-01 (age in single years, by CSD), which also gives children aged 5-17;
  - 2021 CSD cartographic boundaries, intersected with the site's board borders (docs/data/map/canada.json):
    a CSD split between boards is shared by land area, as for the child low-income figures.
A board's density is its population over the land inside its border; boards that overlap (public, Catholic,
French) share the same area and so the same density. Reserves use their own CSD's figures.
Adds or refreshes the columns Population, People per km² (estimated) and Children Ages 5-17 (2021 Census)
in docs/data/canada.csv; run estimate_enrollment.py canada.csv afterwards. Safe to re-run.
Usage: python3 data-prep/add_canada_population.py
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "..", "docs", "data", "canada.csv")
d = json.load(open(os.path.join(HERE, "inputs", "canada", "canada_population_2021.json"), encoding="utf-8"))
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
cols = list(rows[0].keys())
new = ["Population", "People per km² (estimated)", "Children Ages 5-17 (2021 Census)"]
at = cols.index("Children Ages 0-17")
for c in new:
    if c not in cols:
        cols.insert(at, c); at += 1
n = 0
for r in rows:
    x = d["boards"].get(r["District ID"]) or d["fn"].get(r["District ID"]) or {}
    pop, land = x.get("pop"), x.get("land_km2")
    r["Population"] = round(pop) if pop else ""
    r["People per km² (estimated)"] = (f"{pop / land:.1f}" if pop / land < 10 else round(pop / land)) if pop and land else ""
    r["Children Ages 5-17 (2021 Census)"] = round(x["kids_5_17"]) if x.get("kids_5_17") else ""
    n += bool(r["Population"])
w = csv.DictWriter(open(CSV, "w", newline="", encoding="utf-8"), fieldnames=cols); w.writeheader(); w.writerows(rows)
print(len(rows), "rows;", n, "with population;", sum(1 for r in rows if r["Children Ages 5-17 (2021 Census)"]), "with children 5-17")
