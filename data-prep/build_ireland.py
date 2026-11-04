"""Build docs/data/ireland.csv and docs/data/map/ireland.json: Ireland's 16 Education and Training Boards.

Each ETB is made of local authority areas (Education and Training Boards Act 2013, Schedule 1).
- Poverty stand-in: Ireland publishes no local child poverty rate, so the unemployment rate from
  Census 2022 stands in (CSO SAP2022T8T1LEA22, principal economic status of people aged 15+):
  (looking for first job + short-term + long-term unemployed) / (those + at work).
- Children 5-17: Census 2022 (CSO Census Hub layer CensusHub2022_T1_1_LA), which also gives the
  31 local authority borders.
- Meetings: none found; ETBs' YouTube channels (etb_youtube.json) post no board meetings.
Usage: python3 data-prep/build_ireland.py
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "ireland")
ETB = {
    "City of Dublin ETB": ["Dublin City"],
    "Dublin and Dún Laoghaire ETB": ["Dún Laoghaire-Rathdown", "Fingal", "South Dublin"],
    "Cavan and Monaghan ETB": ["Cavan", "Monaghan"], "Cork ETB": ["Cork City", "Cork County"], "Donegal ETB": ["Donegal"],
    "Galway and Roscommon ETB": ["Galway City", "Galway County", "Roscommon"], "Kerry ETB": ["Kerry"],
    "Kildare and Wicklow ETB": ["Kildare", "Wicklow"], "Kilkenny and Carlow ETB": ["Kilkenny", "Carlow"],
    "Laois and Offaly ETB": ["Laois", "Offaly"], "Limerick and Clare ETB": ["Limerick", "Clare"],
    "Longford and Westmeath ETB": ["Longford", "Westmeath"], "Louth and Meath ETB": ["Louth", "Meath"],
    "Mayo, Sligo and Leitrim ETB": ["Mayo", "Sligo", "Leitrim"], "Tipperary ETB": ["Tipperary"],
    "Waterford and Wexford ETB": ["Waterford", "Wexford"],
}
def key(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(council|and county|city and county|county council|city council)\b", " ", s)
    return re.sub(r"[^a-z]", "", s)


def main():
    # unemployment by local authority, from local electoral areas
    lab = {}
    for r in csv.DictReader(open(os.path.join(IN, "ie_SAP2022T8T1LEA22.csv"), encoding="utf-8-sig")):
        if r["Sex"] != "Both Sexes":
            continue
        la = r["CSO Local Electoral Areas 2022"].split(", ")[-1]
        a = lab.setdefault(la, {"work": 0, "unemp": 0})
        v = float(r["VALUE"] or 0)
        if r["Principle Economic Status"] == "At work":
            a["work"] += v
        elif r["Principle Economic Status"] in ("Looking for first regular job", "Short term unemployed", "Long term unemployed"):
            a["unemp"] += v
    geo = json.load(open(os.path.join(IN, "ie_la_census2022_t1_1.geojson")))
    la_of_feat = {}
    for f in geo["features"]:
        p = f["properties"]
        name = p["LOCAL_AUTHORITY"]
        match = [la for las in ETB.values() for la in las if key(la) == key(name) or key(la) == key(name.replace("CITY AND COUNTY", ""))]
        if not match:
            k = key(name)
            match = [la for las in ETB.values() for la in las if k.startswith(key(la)) or key(la).startswith(k)]
        la_of_feat[id(f)] = match[0] if match else None
        kids = sum(float(p.get(f"T1_1AGE{a}T") or (float(p.get(f"T1_1AGE{a}M") or 0) + float(p.get(f"T1_1AGE{a}F") or 0))) for a in range(5, 18))
        p["_kids"] = kids
    rows, feats = [], []
    for i, (etb, las) in enumerate(ETB.items()):
        work = sum(lab[l]["work"] for l in las); un = sum(lab[l]["unemp"] for l in las)
        kids = sum(f["properties"]["_kids"] for f in geo["features"] if la_of_feat[id(f)] in las)
        eid = "IE-" + re.sub(r"\W+", "", unicodedata.normalize("NFKD", etb).encode("ascii", "ignore").decode())[:30]
        rows.append({"District": etb, "Region": geo and next((f["properties"]["PROVINCE"] for f in geo["features"] if la_of_feat[id(f)] in las), ""),
                     "Local authority areas": ", ".join(las), "Available Board Meetings": 0,
                     "Meetings note": "No board meetings found on the ETB's YouTube channel; ETBs publish board minutes on their own websites",
                     "Children Ages 5-17": round(kids), "Unemployment rate (stand-in for poverty)": f"{100 * un / (un + work):.2f}%",
                     "District ID": eid})
        for f in geo["features"]:
            if la_of_feat[id(f)] in las:
                feats.append({"type": "Feature", "properties": {"id": eid, "NAME": f["properties"]["LOCAL_AUTHORITY"].title()}, "geometry": f["geometry"]})
    miss = [f["properties"]["LOCAL_AUTHORITY"] for f in geo["features"] if not la_of_feat[id(f)]]
    with open(os.path.join(HERE, "..", "docs", "data", "ireland.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    # Estimated locale from population density: people = children / 0.178 (their share of the
    # population), over land area. Urban 2,000+ per km², suburban 500-2,000, mixed 100-500, rural under 100.
    area = {}
    for f in feats:
        area[f["properties"]["id"]] = area.get(f["properties"]["id"], 0) + area_km2(f["geometry"])
    for r in rows:
        k = float(r["Children Ages 5-17"] or 0)
        d = k / 0.178 / area[r["District ID"]] if area.get(r["District ID"]) else 0
        r["Locale"] = "Urban" if d >= 2000 else "Suburban" if d >= 500 else "Mixed" if d >= 100 else "Rural"
        r["People per km² (estimated)"] = round(d)
    path = OUT_CSV if "OUT_CSV" in globals() else os.path.join(HERE, "..", "docs", "data", "ireland.csv")
    data = rows
    with open(path, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]
    for f in feats:
        f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(HERE, "..", "docs", "data", "map", "ireland.json"), "w"), separators=(",", ":"))
    print(len(rows), "ETBs;", len(feats), "shapes; unmatched local authorities:", miss)
    for r in rows: print(" ", r["District"], r["Unemployment rate (stand-in for poverty)"], r["Children Ages 5-17"])


if __name__ == "__main__":
    main()
