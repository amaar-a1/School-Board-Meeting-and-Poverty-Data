"""Turns the Czechia downloads (made on GitHub's runner, fetch round 39) into the inputs build_latam.czechia() reads
(data-prep/inputs/czechia/).

- Municipalities, borders, 2024 population and area: Eurostat GISCO Local Administrative Units 2024 (lau_CZ.geojson):
  6,258 municipalities (obce), each with its code (GISCO_ID "CZ_<code>").
- Region (kraj): GISCO NUTS 3 2024 (nuts3_CZ.geojson), by location.
- Poverty stand-in: Ministry of Labour and Social Affairs (MPSV) open data, unemployment in municipalities, December 2024
  (nezamestnanost-v-obcich-12-2024.json): the share of unemployed people among residents aged 15-64
  (podilNezamestnanychOsob), with the counts of available job seekers and of residents aged 15-64; the same for every
  December from 2015 (nezamestnanost-v-obcich-12-YYYY.json.gz), for change over time.
- Children (for the enrollment estimate): the municipality's 2024 population times its region's share of children of
  basic-school age, 6-14 (four fifths of ages 5-9 and all of 10-14), from Eurostat demo_r_pjangrp3 (1 January 2024).
Then, after build_latam.py, run data-prep/simplify_borders.sh czechia.
Usage: python3 data-prep/prep_czechia.py RAWDIR
"""
import gzip, json, os, sys
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "czechia")


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 5), round(c[1], 5)]


def main(raw):
    lau = json.load(open(os.path.join(raw, "lau_CZ.geojson"), encoding="utf-8"))["features"]
    nuts = [(f["properties"]["NUTS_ID"], f["properties"]["NAME_LATN"], shape(f["geometry"]).buffer(0))
            for f in json.load(open(os.path.join(raw, "nuts3_CZ.geojson"), encoding="utf-8"))["features"]]
    un = {x["obec"].split("/")[1]: x for x in json.loads(gzip.decompress(open(os.path.join(raw, "cz_unemp_12_2024.json.gz"), "rb").read()))["polozky"]}
    hist = {}
    for y in range(2015, 2025):
        f = os.path.join(raw, f"cz_unemp_12_{y}.json.gz")
        if os.path.exists(f):
            for x in json.loads(gzip.decompress(open(f, "rb").read()))["polozky"]:
                hist.setdefault(x["obec"].split("/")[1], {})[str(y)] = round(x["podilNezamestnanychOsob"], 1)
    ag = json.load(open(os.path.join(raw, "cz_ages_nuts3.json"), encoding="utf-8"))
    # JSON-stat: value index = age position * number of regions + region position (the other dimensions have one value).
    ai, gi = ag["dimension"]["age"]["category"]["index"], ag["dimension"]["geo"]["category"]["index"]
    v = lambda age, geo: ag["value"].get(str(ai[age] * len(gi) + gi[geo]))
    share = {g: (0.8 * v("Y5-9", g) + v("Y10-14", g)) / v("TOTAL", g) for g in gi}
    data, feats, miss = {}, [], []
    for f in lau:
        p = f["properties"]
        code = p["GISCO_ID"].split("_")[1]
        g = shape(f["geometry"]).buffer(0)
        pt = g.representative_point()
        n = next((n for n in nuts if n[2].contains(pt)), None) or min(nuts, key=lambda n: n[2].distance(pt))
        u = un.get(code)
        if not u: miss.append(p["LAU_NAME"])
        pop = int(p["POP_2024"]) if p.get("POP_2024") else None
        did = f"CZE-{code}"
        data[did] = {"name": p["LAU_NAME"], "region": n[1], "nuts3": n[0], "pop": pop, "area": p.get("AREA_KM2"),
                     "unemp": u and u["podilNezamestnanychOsob"], "jobseekers": u and u["dosazitelniUchazeci"], "pop15_64": u and u["obyvatelstvo15_64"],
                     "kids6_14": round(pop * share[n[0]]) if pop else None, "unemp_years": hist.get(code, {})}
        feats.append({"type": "Feature", "properties": {"id": did, "NAME": p["LAU_NAME"]},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    print("no unemployment figure:", len(miss), miss[:10])
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "cze_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "cze_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(len(data), "municipalities; population", sum(x["pop"] or 0 for x in data.values()), "; children 6-14", sum(x["kids6_14"] or 0 for x in data.values()))


if __name__ == "__main__":
    main(*sys.argv[1:])
