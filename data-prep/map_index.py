"""Writes docs/data/map/index.json: for each map layer, the 10-degree cells it has land in, as boxes [west, south, east,
north], so the map can load a country's borders only when it comes into view (docs/map.js). Cells, not one box: the US
(Alaska's Aleutians, Guam) and France (its overseas départements) would otherwise span the whole world. Run after any
map file changes.

It also writes "_area": land area in km² from the full-detail borders, for the rows on those layers that have a
population but no density or land-area column, so the map works out their density from the detailed border whichever
copy it has loaded."""
import csv, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(HERE, "..", "docs", "data", "map")


def coords(c):
    if isinstance(c[0], (int, float)): yield c
    else:
        for x in c: yield from coords(x)


def bbox(path):
    t = json.load(open(path, encoding="utf-8"))
    xs, ys = [], []
    if t.get("type") == "Topology":
        tr = t.get("transform")
        for arc in t["arcs"]:
            x = y = 0
            for p in arc:
                if tr: x += p[0]; y += p[1]; xs.append(x * tr["scale"][0] + tr["translate"][0]); ys.append(y * tr["scale"][1] + tr["translate"][1])
                else: xs.append(p[0]); ys.append(p[1])
    else:
        for f in t["features"]:
            if f.get("geometry"):
                for x, y in coords(f["geometry"]["coordinates"]): xs.append(x); ys.append(y)
    cells = {}
    for x, y in zip(xs, ys):
        k = (int((x + 180) // 10), int((y + 90) // 10))
        c = cells.get(k)
        cells[k] = [min(c[0], x), min(c[1], y), max(c[2], x), max(c[3], y)] if c else [x, y, x, y]
    return [[round(v, 2) for v in c] for c in cells.values()] if cells else None


out = {}
for p in sorted(glob.glob(os.path.join(MAP, "*.json"))):
    n = os.path.basename(p)[:-5]
    if n in ("index", "aliases", "world") or n.endswith("-hi"): continue
    b = bbox(p)
    if b: out[n] = b
# Layers with a full-detail copy (<name>-hi.json, data-prep/simplify_borders.sh), loaded when zoomed in.
out["_hi"] = sorted(os.path.basename(p)[:-8] for p in glob.glob(os.path.join(MAP, "*-hi.json")))
need = set()
for f in glob.glob(os.path.join(MAP, "..", "*.csv")):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if (r.get("Population") or "0") != "0" and not r.get("People per km² (estimated)") and not r.get("Land area (km²)"):
            need.add(r.get("District ID") or r.get("GEOID") or "")
area = {}
for p in glob.glob(os.path.join(MAP, "*-hi.json")):
    t = json.load(open(p, encoding="utf-8"))
    if t.get("type") == "Topology":   # Canada: every row has its census density
        continue
    for f in t["features"]:
        k = f["properties"].get("GEOID") or f["properties"].get("id")
        if k in need and f.get("geometry"): area[k] = round(area.get(k, 0) + area_km2(f["geometry"]), 3)
out["_area"] = area
json.dump(out, open(os.path.join(MAP, "index.json"), "w"), separators=(",", ":"))
print(len(out), "layers;", {k: v for k, v in list(out.items())[:6]})
