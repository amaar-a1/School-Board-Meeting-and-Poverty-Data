"""Estimated pupils by Spanish municipality, for estimate_enrollment.py (data-prep/inputs/estimates/es_pupils.json).

Spain publishes no national enrollment by municipality (Catalonia and Madrid do: prep_spain_regional_pupils.py, used first). The estimate is the school-age population living there:
- children aged 3-14 (nursery to lower secondary ages): twelve eighteenths of the municipality's children under 18
  (docs/data/spain.csv, "Children under 18 (estimated)");
- plus, in municipalities of 500 or more people, the residents aged 15 and over studying at school level (primary,
  lower or upper secondary, or vocational) in INE's census (table 66627, "Población de 15 y más años ... por nivel de
  estudios en curso", latest year), summed by municipality on GitHub's runner: inputs/spain/ine_census_15plus_school_studies.json;
- in smaller municipalities, which that table leaves out, children aged 3-17 (fifteen eighteenths of under-18s) instead.
Usage: python3 data-prep/prep_spain_pupils.py
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    cen = json.load(open(os.path.join(HERE, "inputs", "spain", "ine_census_15plus_school_studies.json"), encoding="utf-8"))
    by = cen["by_municipality"]; per = cen["period"]
    est = {}
    n_cen = 0
    for r in csv.DictReader(open(os.path.join(HERE, "..", "docs", "data", "spain.csv"), encoding="utf-8")):
        code = r["District ID"][3:]
        u18 = float(r.get("Children under 18 (estimated)") or 0)
        if not u18: continue
        if code in by: est[code] = round(u18 * 12 / 18 + by[code]); n_cen += 1
        else: est[code] = round(u18 * 15 / 18)
    text = (f"Estimate: children aged 3–14 living in the municipality (twelve eighteenths of its estimated children under 18), plus residents aged 15 and over "
            f"studying at school level in INE's census ({per}); for municipalities under 500 people, children aged 3–17. Spain publishes no enrollment by municipality")
    json.dump({"text": text, "est": est}, open(os.path.join(HERE, "inputs", "estimates", "es_pupils.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(est), "municipalities;", n_cen, "with census figures; total", sum(est.values()))


if __name__ == "__main__":
    main()
