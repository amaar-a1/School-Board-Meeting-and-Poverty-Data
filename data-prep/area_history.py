"""Figures over time for whole countries and their regions, for years their places have none (the user's rule: a
year known only nationally or regionally is drawn on the country's or region's line, never a district's):
docs/data/area_history.json, {country: {"": {column: {year: value}}, region: {column: {year: value}}}}, read by
history.js (the Trends tab's lines) and compare.js (a country or region compared). A year its places do have is
left to them.

- Peru: total population at the 2007, 2017 and 2025 censuses and by department in 2025 (INEI, first results of the
  2025 census, uploaded by the project's owner: inputs/peru/pe_census2025_departments.json).
- Philippines: population for the country and its regions, 2022-2025 (UNFPA/PSA via HDX, fetch round 61:
  inputs/philippines/ph_admpop_regions_2022_2025.json). Western and Central Visayas and the ARMM are left out: those
  figures are on the regions before the 2024 Negros Island Region and before BARMM.

  python3 data-prep/area_history.py
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs")
OUT = os.path.join(HERE, "..", "docs", "data", "area_history.json")
POP = "Population by year"


def regions(name):
    return {r["Region"] for r in csv.DictReader(open(os.path.join(HERE, "..", "docs", "data", f"{name}.csv"), encoding="utf-8")) if r.get("Region")}


def main():
    out = {}
    pe = json.load(open(os.path.join(IN, "peru", "pe_census2025_departments.json"), encoding="utf-8"))
    have = regions("peru")
    out["Peru"] = {"": {POP: pe["country"]}, **{d: {POP: {"2025": n}} for d, n in pe["departments_2025"].items() if d in have}}
    ph = json.load(open(os.path.join(IN, "philippines", "ph_admpop_regions_2022_2025.json"), encoding="utf-8"))
    have = {r.upper(): r for r in regions("philippines")}
    alias = {"MIMAROPA REGION": "REGION IV-B (MIMAROPA)"}
    skip = {"REGION VI (WESTERN VISAYAS)", "REGION VII (CENTRAL VISAYAS)", "AUTONOMOUS REGION IN MUSLIM MINDANAO (ARMM)"}
    out["Philippines"] = {"": {POP: ph["country"]}}
    for n, s in ph["regions"].items():
        k = alias.get(n.upper(), n.upper())
        if k in skip or k not in have: continue
        out["Philippines"][have[k]] = {POP: s}
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    for c, v in out.items(): print(c, len(v) - 1, "regions;", ", ".join(sorted(v[""][POP])))


if __name__ == "__main__":
    main()
