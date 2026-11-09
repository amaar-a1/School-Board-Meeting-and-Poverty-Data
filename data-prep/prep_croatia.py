"""Joins Croatia's poverty map to its 556 cities and municipalities (data-prep/inputs/croatia/hr_data.json), for
build_latam.croatia().

Inputs (in inputs/croatia/):
- hr_poverty_wb2011.csv: the World Bank / Croatian Bureau of Statistics poverty map (World Bank, October 2016), for 2011:
  the share of people below the poverty line (23,918.62 HRK a year per adult equivalent), with standard errors, the
  poverty gap and its square, and each place's share of Croatia's poor. Level "m" is a city or municipality, "zt" the
  City of Zagreb and "zd" its 17 districts (which add up to the city; kept for the record, not used as places).
  Typed in from the report by the project's owner.
- hr_counties_wb2011.csv: the same map's county rates, with 95% confidence intervals.
- lau_HR.geojson: Eurostat GISCO Local Administrative Units 2024 for Croatia (names, 2024 population, area, borders).
- nuts3_HR.geojson: GISCO NUTS 3 (2024), Croatia's 21 counties, to place each city and municipality in its county.
Names are matched whole first ("Novigrad - Cittanova" isn't Novigrad), then after dropping the Italian half of bilingual names ("Buje - Buie") and qualifiers ("Otok (Split)");
where a name is shared, by the report's qualifier (Otok and Privlaka: "(Split)", "(Vinkovci)", "(Zadar)"), else (Sveta Nedelja) the place whose 2024 population is closest to the 2011 figure.
Usage: python3 data-prep/prep_croatia.py
"""
import collections, csv, json, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "croatia")
full = lambda t: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", re.sub(r"\s*\(.*?\)", "", t)).encode("ascii", "ignore").decode().lower())
# The report's qualifiers for shared names, as counties.
QUAL = {"Split": "Splitsko-dalmatinska", "Vinkovci": "Vukovarsko-srijemska", "Zadar": "Zadarska"}
norm = lambda t: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", re.sub(r"\s*\(.*?\)", "", t.split(" - ")[0])).encode("ascii", "ignore").decode().lower())


def inside(pt, ring):
    x, y = pt; c = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c


def polys(g):
    return g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]


def main():
    lau = json.load(open(os.path.join(IN, "lau_HR.geojson"), encoding="utf-8"))["features"]
    counties = [(re.sub(r"\s+županija$", "", f["properties"]["NAME_LATN"]), polys(f["geometry"])) for f in json.load(open(os.path.join(IN, "nuts3_HR.geojson"), encoding="utf-8"))["features"]]
    cty = {r["county"]: r for r in csv.DictReader(open(os.path.join(IN, "hr_counties_wb2011.csv"), encoding="utf-8"))}
    by, byfull = collections.defaultdict(list), collections.defaultdict(list)
    for f in lau: by[norm(f["properties"]["LAU_NAME"])].append(f); byfull[full(f["properties"]["LAU_NAME"])].append(f)
    out = {}
    for f in lau:
        p = f["properties"]
        # County: the one holding the place's centroid (border points sit on county lines too), else most of its border points.
        votes = collections.Counter()
        ring = max((poly[0] for poly in polys(f["geometry"])), key=len)
        a2 = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]))
        if a2:
            cx = sum((x1 + x2) * (x1 * y2 - x2 * y1) for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1])) / (3 * a2)
            cy = sum((y1 + y2) * (x1 * y2 - x2 * y1) for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1])) / (3 * a2)
            if inside((cx, cy), ring):
                for name, cps in counties:
                    if any(inside((cx, cy), cp[0]) and not any(inside((cx, cy), h) for h in cp[1:]) for cp in cps): votes[name] += 1000; break
        for poly in polys(f["geometry"]):
            for pt in poly[0][::3]:
                for name, cps in counties:
                    if any(inside(pt, cp[0]) and not any(inside(pt, h) for h in cp[1:]) for cp in cps): votes[name] += 1; break   # holes: Zagreb County surrounds the City of Zagreb
        out[p["GISCO_ID"][3:]] = {"name": p["LAU_NAME"], "county": votes.most_common(1)[0][0] if votes else "",
                                  "pop": p.get("POP_2024"), "area": p.get("AREA_KM2")}
    rows = [r for r in csv.DictReader(open(os.path.join(IN, "hr_poverty_wb2011.csv"), encoding="utf-8")) if r["level"] in ("m", "zt")]
    for r in rows:
        k = "gradzagreb" if r["level"] == "zt" else norm(r["location"])
        cands = byfull.get(full(r["location"])) or by.get(k, [])
        q = re.search(r"\((\w+)\)", r["location"])
        if q and len(cands) > 1: cands = [f for f in cands if out[f["properties"]["GISCO_ID"][3:]]["county"] == QUAL[q.group(1)]]
        f = min(cands, key=lambda f: abs((f["properties"].get("POP_2024") or 0) - int(r["population"])))
        o = out[f["properties"]["GISCO_ID"][3:]]
        assert "pov" not in o, (r["location"], o)
        o.update({"wb_name": r["location"], "pop2011": int(r["population"]), "pov": float(r["headcount_poverty_pct"]), "pov_se": float(r["se_headcount"]),
                  "gap": float(r["poverty_gap"]), "share_of_poor": float(r["share_of_poor_pct"])})
    for o in out.values():
        c = cty.get(o["county"])
        if c: o["county_pov"] = float(c["poverty_rate_pct"])
    json.dump(out, open(os.path.join(IN, "hr_data.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(out), "places;", sum("pov" in o for o in out.values()), "with their own rate; without:", [o["name"] for o in out.values() if "pov" not in o],
          "; no county:", [o["name"] for o in out.values() if not o["county"]], "; county names not in the table:", sorted({o["county"] for o in out.values()} - set(cty)))


if __name__ == "__main__":
    main()
