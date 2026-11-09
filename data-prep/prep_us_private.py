"""Private-school pupils inside each US school district's borders (for the map's public-school share).

Each private school in NCES's Private School Universe Survey 2021-22 (inputs/pss2122_private_schools.json, its
reported students, K-12 and ungraded) is placed in the unified or elementary district whose border (the site's
own map borders, docs/data/map/unsd.json and elsd.json) contains its coordinates. Secondary-only districts get no
figure, since an elementary district's private schools would be counted twice. Districts with no private school
inside get 0. Writes inputs/us_private_pupils.json: {LEAID: pupils}.
Usage: python3 data-prep/prep_us_private.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(HERE, "..", "docs", "data", "map")


def decode(path, name):
    t = json.load(open(path, encoding="utf-8")); sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    def ring(ix):
        out = []
        for i in ix:
            p = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(p if not out else p[1:])
        return out
    for g in t["objects"][name]["geometries"]:
        polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"] if g["type"] == "MultiPolygon" else []
        yield g["properties"]["GEOID"], [[ring(r) for r in poly] for poly in polys]


def inside(x, y, ring):
    c = False; j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: c = not c
        j = i
    return c


def main():
    shapes = []
    for f, n in (("unsd.json", "unsd"), ("elsd.json", "elsd")):
        for gid, polys in decode(os.path.join(MAP, f), n):
            for poly in polys:
                xs = [p[0] for p in poly[0]]; ys = [p[1] for p in poly[0]]
                shapes.append((gid, min(xs), max(xs), min(ys), max(ys), poly))
    grid = {}
    for s in shapes:
        for gx in range(int(s[1] // 1), int(s[2] // 1) + 1):
            for gy in range(int(s[3] // 1), int(s[4] // 1) + 1):
                grid.setdefault((gx, gy), []).append(s)
    pss = json.load(open(os.path.join(HERE, "inputs", "pss2122_private_schools.json"), encoding="utf-8"))
    out = {gid: 0 for gid, *_ in shapes}; missed = 0
    for _, st, lat, lon, n, lvl in pss["rows"]:
        hit = None
        for gid, x0, x1, y0, y1, poly in grid.get((int(lon // 1), int(lat // 1)), []):
            if x0 <= lon <= x1 and y0 <= lat <= y1 and inside(lon, lat, poly[0]) and not any(inside(lon, lat, h) for h in poly[1:]):
                hit = gid; break
        if hit: out[hit] += n
        else: missed += n
    json.dump(dict(sorted(out.items())), open(os.path.join(HERE, "inputs", "us_private_pupils.json"), "w", encoding="utf-8"), separators=(",", ":"))
    print(len(out), "districts;", sum(out.values()), "private pupils placed;", missed, "outside every border (water, federal land or territories)")


if __name__ == "__main__":
    main()
