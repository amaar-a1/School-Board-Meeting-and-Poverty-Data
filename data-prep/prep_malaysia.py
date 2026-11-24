"""Turns the Malaysia downloads (made on GitHub's runner, fetch rounds 27-28) into the inputs build_latam.malaysia() reads
(data-prep/inputs/malaysia/).

Sources, all from the Department of Statistics Malaysia (DOSM) and the Ministry of Education, through OpenDOSM and
data.gov.my:
- Borders: DOSM's administrative districts (administrative_2_district.geojson, dosm-malaysia/data-open on GitHub), 160
  districts. Six districts Sarawak created since (Gedong, Lingga, Lubok Antu, Pantu, Sebuyau, Siburan) and Sabah's
  Membakut have no border of their own there and stay inside the district they came from.
- Poverty: DOSM, Household Income and Expenditure Survey (HIES) 2024, hh_poverty_district.csv: the share of
  households below the national poverty line income (absolute poverty), and below half the median household income
  (relative poverty). Earlier years (2019, 2022) are kept for the trend.
- Household income: DOSM, HIES 2024, hies_district.csv (mean and median monthly household income, Gini).
- Population: DOSM, population_district.csv, 1 January 2025 (thousands; all ages, and five-year age groups).
- Enrollment: Ministry of Education, enrolment_school_district (data.gov.my), 30 June 2025: pupils in government and
  government-aided primary and secondary schools (not private or international schools), by education district.
  Where an education district is the administrative district (most of them), that's the count; where it isn't (two
  districts share one education office, one district has two, or the district is newer than the office), the
  district gets an estimate instead: its children aged 7-17 (three fifths of 5-9, all of 10-14, three fifths of
  15-19), marked as estimated.
Then, after build_latam.py, run data-prep/simplify_borders.sh.
Usage: python3 data-prep/prep_malaysia.py RAWDIR
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "malaysia")
key = lambda s: re.sub(r"[^a-z]", "", str(s).lower().replace("&", "dan").replace("s.p.", "seberangperai"))
# Names in the poverty, income and enrollment tables that differ from the borders'.
ALIAS = {"larutdanmatang": "larutdanmatang", "seberangperaiselatan": "seberangperaiselatan", "hulu": "huluterengganu",
         "pasirputih": "pasirputeh", "kualalipis": "lipis", "manjungdinding": "manjung", "jpnperlis": "perlis"}


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def main(raw):
    geo = json.load(open(os.path.join(raw, "my_district.geojson"), encoding="utf-8"))["features"]
    dist = {}
    for f in geo:
        p = f["properties"]
        did = f"MYS-{p['code_state']:02d}{p['code_district']:02d}"
        dist[(key(p["state"]), key(p["district"]))] = {"id": did, "name": p["district"].replace(" Dan ", " dan "), "state": p["state"], "geom": f["geometry"]}
    look = lambda st, d: dist.get((key(st), ALIAS.get(key(d), key(d))))

    pov, miss = {}, set()
    for r in csv.DictReader(open(os.path.join(raw, "my_hh_poverty_district.csv"), encoding="utf-8")):
        x = look(r["state"], r["district"])
        if not x: miss.add((r["state"], r["district"])); continue
        pov.setdefault(x["id"], {})[r["date"][:4]] = (float(r["poverty_absolute"]), float(r["poverty_relative"]))
    inc = {}
    for r in csv.DictReader(open(os.path.join(raw, "my_hies_district.csv"), encoding="utf-8")):
        x = look(r["state"], r["district"])
        if x and r["date"].startswith("2024"): inc[x["id"]] = (int(float(r["income_mean"])), int(float(r["income_median"])), float(r["gini"]))
    print("poverty rows with no border (inside their parent's):", sorted(miss))
    # Perlis and the three federal territories are each one district: the district table stops at 2022 for them, and the
    # state table has the 2024 figure (the same measure; no relative poverty).
    for r in csv.DictReader(open(os.path.join(raw, "my_hies_state.csv"), encoding="utf-8")):
        x = look(r["state"], r["state"])
        if x and r["date"].startswith("2024") and "2024" not in pov.get(x["id"], {}):
            pov.setdefault(x["id"], {})["2024"] = (float(r["poverty"]), None)
            inc.setdefault(x["id"], (int(float(r["income_mean"])), int(float(r["income_median"])), float(r["gini"])))

    pop, ages, pop_years = {}, {}, {}
    for r in csv.DictReader(open(os.path.join(raw, "my_pop_district.csv"), encoding="utf-8")):
        if r["sex"] != "both" or r["ethnicity"] != "overall": continue
        if r["age"] == "overall":   # every year, for change over time
            x = look(r["state"], r["district"])
            if x: pop_years.setdefault(x["id"], {})[r["date"][:4]] = round(float(r["population"]) * 1000)
        if r["date"] != "2025-01-01": continue
        x = look(r["state"], r["district"])
        if not x: continue
        v = float(r["population"]) * 1000
        if r["age"] == "overall": pop[x["id"]] = round(v)
        else: ages.setdefault(x["id"], {})[r["age"]] = v

    enr, ekeys, enr_years = {}, {}, {}
    for r in json.load(open(os.path.join(raw, "my_enrol.json"), encoding="utf-8")):
        if r["sex"] != "both" or r["stage"] not in ("primary", "secondary") or r["district"] == "All Districts": continue
        x = look(r["state"], r["district"])
        if x: enr_years.setdefault(x["id"], {}).setdefault(r["date"][:4], 0); enr_years[x["id"]][r["date"][:4]] += int(r["students"])
        if r["date"] != "2025-06-30": continue
        ekeys.setdefault((r["state"], r["district"]), x and x["id"])
        if x: enr[x["id"]] = enr.get(x["id"], 0) + int(r["students"])
    print("education districts that aren't one administrative district:", sorted(k for k, v in ekeys.items() if not v))

    data, feats = {}, []
    for x in sorted(dist.values(), key=lambda v: v["id"]):
        did, a = x["id"], ages.get(x["id"], {})
        kids = round(0.6 * a.get("5-9", 0) + a.get("10-14", 0) + 0.6 * a.get("15-19", 0)) if a else None
        p = pov.get(did, {})
        data[did] = {"name": x["name"], "state": x["state"], "pop": pop.get(did), "kids7_17": kids,
                     "pov": p.get("2024", (None, None))[0], "rel": p.get("2024", (None, None))[1],
                     "pov_years": {y: v[0] for y, v in sorted(p.items())},
                     "income": inc.get(did), "pupils": enr.get(did),
                     "pop_years": dict(sorted(pop_years.get(did, {}).items())), "pupil_years": dict(sorted(enr_years.get(did, {}).items())) if enr.get(did) else {}}
        feats.append({"type": "Feature", "properties": {"id": did, "NAME": x["name"]},
                      "geometry": {"type": x["geom"]["type"], "coordinates": rnd(x["geom"]["coordinates"])}})
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "my_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "my_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"))
    n = len(data)
    print(n, "districts;", sum(1 for v in data.values() if v["pov"] is not None), "with poverty;", sum(1 for v in data.values() if v["pupils"]), "with a pupil count;",
          "population", sum(v["pop"] or 0 for v in data.values()), "; pupils", sum(v["pupils"] or 0 for v in data.values()))


if __name__ == "__main__":
    main(*sys.argv[1:])
