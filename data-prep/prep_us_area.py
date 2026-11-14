"""Land area (km²) of each US school district (and territory), from the site's own map borders, for population density.

The borders are the Census Bureau's 2024 cartographic boundary files (clipped to the shoreline, simplified), in
docs/data/map/unsd.json, elsd.json, scsd.json (TopoJSON) and territories.json. Area is spherical (WGS84 mean radius).
Writes inputs/us_district_land_km2.json: {GEOID or territory id: km²}; build_national.py writes it as "Land area (km²)".
Usage: python3 data-prep/prep_us_area.py
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prep_us_private import decode

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(HERE, "..", "docs", "data", "map")
R = 6371.0088


def ring_area(ring):
    a = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        a += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return abs(a * R * R / 2)


def poly_area(poly):
    return ring_area(poly[0]) - sum(ring_area(h) for h in poly[1:])


out = {}
for f in ("unsd", "elsd", "scsd"):
    for gid, polys in decode(os.path.join(MAP, f + ".json"), f):
        out[gid] = round(out.get(gid, 0) + sum(poly_area(p) for p in polys), 2)
t = json.load(open(os.path.join(MAP, "territories.json"), encoding="utf-8"))
if "objects" in t:
    terr = {}
    for gid, polys in decode(os.path.join(MAP, "territories.json"), list(t["objects"])[0]):
        terr[gid] = round(terr.get(gid, 0) + sum(poly_area(p) for p in polys), 2)
    out.update(terr)   # Puerto Rico is in the district files too: count its border once
else:
    for ft in t["features"]:
        g = ft["geometry"]; polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        gid = ft["properties"].get("GEOID") or ft["properties"].get("id")
        out[gid] = round(out.get(gid, 0) + sum(poly_area(p) for p in polys), 2)
json.dump(dict(sorted(out.items())), open(os.path.join(HERE, "inputs", "us_district_land_km2.json"), "w"), separators=(",", ":"))
print(len(out), "areas; e.g. LA Unified", out.get("0622710"), "km²")
