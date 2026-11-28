"""Each region's outline (US state, province, département, ...), for marking the region on the map when one is picked
(docs/data/map/regions/<data file>.json, read by map.js).

A region's districts are joined into one shape (small gaps between them closed) and its edge saved as lines:
{"col": the region column, "regions": {region: [[[lng, lat], ...], ...]}}. The region column is the data file's
group column (config.js), else the first of State, Province, Region, Nation, Department, Territory with 2-150 values,
as Compare picks it. Map areas with no row of their own (land outside every district or board, France's groups of
smaller communes) go with the region their id or properties point to.

Run after changing the map files or the data's regions: python3 data-prep/map_region_outlines.py
"""
import csv, glob, json, os, re

from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs")
MAP = os.path.join(DOCS, "data", "map")
OUT = os.path.join(MAP, "regions")
REGION_COLS = ["State", "Province", "Region", "Nation", "Department", "Territory"]
GAP, SIMPLIFY, HOLE = 0.01, 0.004, 0.3

from map_outlines import topo_features


def group_columns():
    """data file -> its group column, from config.js."""
    src = open(os.path.join(DOCS, "config.js"), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'file:\s*"data/([^"]+)\.csv"(.{0,4000}?)(?=file:\s*"data/|$)', src, re.S):
        g = re.search(r'groups:\s*\{[^}]*?column:\s*"([^"]+)"', m[2])
        if g: out[m[1]] = g[1]
    return out


def region_col(rows, preferred):
    for c in [preferred] + REGION_COLS:
        if c and len({r.get(c) for r in rows if r.get(c)}) in range(2, 151): return c
    return None


def lines_of(geoms):
    u = unary_union(geoms).buffer(GAP, join_style="mitre").buffer(-GAP, join_style="mitre")
    out = []
    for p in (u.geoms if isinstance(u, MultiPolygon) else [u]):
        if not isinstance(p, Polygon) or p.is_empty: continue
        p = Polygon(p.exterior, [h for h in p.interiors if Polygon(h).area > HOLE]).simplify(SIMPLIFY)
        for ring in [p.exterior, *p.interiors]:
            pts = [[round(x, 3), round(y, 3)] for x, y in ring.coords]
            if len(pts) >= 4: out.append(pts)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    cols = group_columns()
    region_of, file_of, prefix = {}, {}, {}
    for path in sorted(glob.glob(os.path.join(DOCS, "data", "*.csv"))):
        key = os.path.basename(path)[:-4]
        rows = list(csv.DictReader(open(path, encoding="utf-8")))
        if not rows or "District ID" not in rows[0]: continue
        col = region_col(rows, cols.get(key))
        if not col: continue
        for r in rows:
            i, g = r["District ID"], r.get(col)
            if not i or not g: continue
            region_of[i], file_of[i] = g, (key, col)
            p = i[:2] if i.isdigit() else i.rsplit("-", 1)[0]   # US: the state's FIPS code; else the id up to its last part
            prefix.setdefault(p, (g, key, col))
    groups = {}
    for fn in sorted(os.listdir(MAP)):
        name = fn[:-5]
        if not fn.endswith(".json") or name.endswith("-hi") or name in ("world", "islands", "index", "aliases", "outlines", "france-small", "canada-fn", "scsd"):
            continue
        d = json.load(open(os.path.join(MAP, fn), encoding="utf-8"))
        feats = d["features"] if d.get("type") == "FeatureCollection" else topo_features(d, keep_props=True)
        for f in feats:
            g = f.get("geometry"); pr = f.get("properties") or {}
            if not g or "Polygon" not in g["type"]: continue
            i = str(pr.get("id") or pr.get("GEOID") or "")
            if i in region_of:
                key, col = file_of[i]; reg = region_of[i]
            elif pr.get("dep") and i.startswith("FRA-"):
                reg, (key, col) = pr["dep"], ("france", "Region")
            else:
                p = i[:2] if i.isdigit() else i.rsplit("-", 1)[0]
                if p not in prefix: continue
                reg, key, col = prefix[p]
            s = shape(g)
            groups.setdefault((key, col), {}).setdefault(reg, []).append(s if s.is_valid else s.buffer(0))
    for (key, col), regs in sorted(groups.items()):
        res = {"col": col, "regions": {reg: lines_of(gs) for reg, gs in sorted(regs.items())}}
        json.dump(res, open(os.path.join(OUT, key + ".json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
        print(key, col, len(regs), "regions", sum(len(l) for v in res["regions"].values() for l in v), "points")


if __name__ == "__main__":
    main()
