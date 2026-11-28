"""Each map layer's outer edge, for the map's region and country views (docs/data/map/outlines.json).

Shown by region or country, the map draws each area's border. Borders between regions come from the edges that
neighbouring districts share (map.js finds them as it draws), but a layer's outer edge can't: its districts' borders
were simplified one by one, so where two don't quite meet, their edges look like the edge of the land. Here each
layer's districts are joined into one shape (small gaps between them closed), and its outline saved as lines:
{layer: [[[lng, lat], ...], ...]}. The US layers overlap (unified, elementary and secondary districts, territories),
so their outline is the US's, saved under unsd, and the others get none; Canada's under canada (its overlapping
boards, canada2, none).

Run after changing any file in docs/data/map: python3 data-prep/map_outlines.py
"""
import json
import os

from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.ops import unary_union

MAP = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "map")
SKIP = {"world", "islands", "france-small", "canada-fn", "index", "aliases"}   # canada-fn: drawn over the boards
GAP = 0.01        # degrees: gaps narrower than about 1 km between districts are closed
SIMPLIFY = 0.005  # degrees
HOLE = 0.3        # square degrees: holes larger than this (Lesotho inside South Africa) stay


def topo_features(t, keep_props=False):
    """The features of a TopoJSON file, as GeoJSON (with their properties, if asked)."""
    sx, sy = t["transform"]["scale"]
    tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(ix):
        out = []
        for i in ix:
            pts = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(pts if not out else pts[1:])
        return out

    feats = []
    for obj in t["objects"].values():
        for g in obj.get("geometries", []):
            if g["type"] == "Polygon":
                feats.append({"geometry": {"type": "Polygon", "coordinates": [ring(r) for r in g["arcs"]]}, "properties": g.get("properties") if keep_props else None})
            elif g["type"] == "MultiPolygon":
                feats.append({"geometry": {"type": "MultiPolygon", "coordinates": [[ring(r) for r in p] for p in g["arcs"]]}, "properties": g.get("properties") if keep_props else None})
    return feats


def outline(fc):
    polys = []
    for f in fc["features"]:
        g = f.get("geometry")
        if not g or "Polygon" not in g["type"]:
            continue
        s = shape(g)
        if not s.is_valid:
            s = s.buffer(0)
        polys.append(s)
    u = unary_union(polys).buffer(GAP, join_style="mitre").buffer(-GAP, join_style="mitre")
    parts = list(u.geoms) if isinstance(u, MultiPolygon) else [u]
    lines = []
    for p in parts:
        if not isinstance(p, Polygon) or p.is_empty:
            continue
        p = Polygon(p.exterior, [h for h in p.interiors if Polygon(h).area > HOLE]).simplify(SIMPLIFY)
        for ring in [p.exterior, *p.interiors]:
            pts = [[round(x, 3), round(y, 3)] for x, y in ring.coords]
            if len(pts) >= 4:
                lines.append(pts)
    return lines


def main():
    out = {}
    for fn in sorted(os.listdir(MAP)):
        name = fn[:-5]
        if not fn.endswith(".json") or name in SKIP or name.endswith("-hi") or name == "outlines":
            continue
        d = json.load(open(os.path.join(MAP, fn)))
        if d.get("type") != "FeatureCollection":
            continue
        out[name] = outline(d)
        print(name, len(out[name]), sum(len(l) for l in out[name]))
    us = []
    for n in ("unsd", "elsd", "territories"):
        us += topo_features(json.load(open(os.path.join(MAP, n + ".json"))))
    out["unsd"] = outline({"features": us})
    out["elsd"] = out["scsd"] = out["territories"] = []
    out["canada"] = outline({"features": topo_features(json.load(open(os.path.join(MAP, "canada.json"))))})
    out["canada2"] = []
    for name in ("unsd", "canada"):
        print(name, len(out[name]), sum(len(l) for l in out[name]))
    with open(os.path.join(MAP, "outlines.json"), "w") as f:
        json.dump(out, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
