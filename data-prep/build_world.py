"""Build docs/data/map/world.json: grey outlines for every country the site doesn't cover.

From Natural Earth 1:50m admin-0 countries (public domain). Countries with their own data on the
site (and their own borders in docs/data/map/) are left out, so they aren't drawn twice.
Usage: python3 data-prep/build_world.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "inputs", "world", "ne_50m_admin_0_countries.geojson")
DST = os.path.join(HERE, "..", "docs", "data", "map", "world.json")
# On the site already: the US and its territories, Canada, Saint-Pierre-et-Miquelon, the UK,
# Ireland, the Nordic countries, the Netherlands, Germany, New Zealand and the island set.
COVERED = {"USA", "PRI", "VIR", "GUM", "MNP", "ASM", "CAN", "SPM", "GBR", "IRL", "NOR", "SWE", "FIN", "DNK", "NLD"}
for f, iso in (("germany.csv", "DEU"), ("new-zealand.csv", "NZL"), ("iceland.csv", "ISL"), ("switzerland.csv", "CHE"), ("chile.csv", "CHL"), ("colombia.csv", "COL"), ("mexico.csv", "MEX")):
    if os.path.exists(os.path.join(HERE, "..", "docs", "data", f)):
        COVERED.add(iso)
ISL = os.path.join(HERE, "..", "docs", "data", "islands.csv")
if os.path.exists(ISL):
    import csv
    COVERED |= {r["District ID"].split("-", 1)[1] for r in csv.DictReader(open(ISL, encoding="utf-8"))}


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 2), round(c[1], 2)]


d = json.load(open(SRC, encoding="utf-8"))
out = []
for f in d["features"]:
    p = f["properties"]
    if p["ADM0_A3"] in COVERED:
        continue
    out.append({"type": "Feature", "properties": {"id": f"W-{p['ADM0_A3']}", "NAME": p["NAME_LONG"] or p["NAME"]},
                "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
json.dump({"type": "FeatureCollection", "features": out}, open(DST, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
print(len(out), "countries drawn grey;", os.path.getsize(DST) // 1024, "KB")
