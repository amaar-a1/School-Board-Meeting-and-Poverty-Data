"""Adds the First Nations reserves and settlements inside the map-only "Rest of Ontario" and "Rest of Alberta"
areas (land outside every school board) to docs/data/canada.csv, and their borders to docs/data/map/canada-fn.json.

Their schools are run by the First Nation itself (band-operated), so each counts as an education authority.
Statistics Canada publishes no low-income figures for reserves, so each shows the rate of the area around it
(children 0-17, LIM-AT) as a stand-in, in a column of its own. A reserve split into parts with the same name
is one place.

Input: data-prep/inputs/canada/ca_rest_first_nations.geojson (2021 census subdivisions of type IRI or S-É
whose interior point lies in a Rest-of area; built from this repo's statcan-csd-2021 release with mapshaper).
finish_canada.py calls it; or run: python3 data-prep/canada_first_nations.py docs/data/canada.csv
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROV = {"35": ("ON", "Ontario"), "48": ("AB", "Alberta")}
AREA = "Low-income rate of the surrounding area (children 0-17)"


def apply(path):
    src = json.load(open(os.path.join(HERE, "inputs", "canada", "ca_rest_first_nations.geojson"), encoding="utf-8"))["features"]
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    cols = list(rows[0].keys())
    rows = [r for r in rows if "-FN-" not in r["District ID"]]   # rebuild them every time
    # The rate of each Rest-of area, from the map file (computed by build_canada.py from the census subdivisions in it).
    rest = {}
    topo = json.load(open(os.path.join(HERE, "..", "docs", "data", "map", "canada.json"), encoding="utf-8"))
    for g in topo["objects"]["canada"]["geometries"]:
        p = g.get("properties") or {}
        if p.get("pseudo"): rest[p["id"]] = p.get("pct")
    # One place per name: "Fort Albany (Part) 67" comes in two parts.
    by = {}
    for f in src:
        p = f["properties"]
        key = (p["PRUID"], re.sub(r"\s*\(Part\)", "", p["CSDNAME"]))
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        e = by.setdefault(key, {"uid": p["CSDUID"], "rest": p["id"], "area": 0, "polys": [], "type": p["CSDTYPE"]})
        e["polys"] += polys; e["area"] += p.get("area_km2") or 0
    feats = []
    for (pr, name), e in sorted(by.items()):
        code, prov = PROV[pr]
        did = f"CA-{code}-FN-{e['uid']}"
        rate = rest.get(e["rest"])
        rows.append({**{c: "" for c in cols}, "District": name, "Province": prov, "Board type": "First Nation (band-operated)",
                     "Locale": "Rural", "Available Board Meetings": 0, AREA: f"{rate:.1f}%" if rate is not None else "",
                     "How poverty was calculated": f"A First Nations {'settlement' if e['type'].startswith('S') else 'reserve'} outside every provincial school board's border; "
                         f"its schools are run by the First Nation. Statistics Canada publishes no low-income figures for reserves, so the rate shown is the "
                         f"surrounding area's (Rest of {prov}, children 0-17), as a stand-in",
                     "District ID": did})
        feats.append({"type": "Feature", "properties": {"id": did, "NAME": name},
                      "geometry": {"type": "MultiPolygon", "coordinates": e["polys"]}})
    if AREA not in cols: cols.insert(cols.index("How poverty was calculated"), AREA)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, restval=""); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(os.path.dirname(os.path.abspath(path)), "map", "canada-fn.json"), "w", encoding="utf-8"),
              separators=(",", ":"), ensure_ascii=False)
    return len(feats)


if __name__ == "__main__":
    print(apply(sys.argv[1] if len(sys.argv) > 1 else "docs/data/canada.csv"), "First Nations places added")
