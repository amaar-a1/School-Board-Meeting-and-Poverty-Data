"""Build docs/data/ireland.csv and docs/data/map/ireland.json: Ireland's 16 Education and Training Boards.

Each ETB is made of local authority areas (Education and Training Boards Act 2013, Schedule 1).
- Poverty stand-in: Ireland publishes no local child poverty rate, so the unemployment rate from
  Census 2022 stands in (CSO SAP2022T8T1LEA22, principal economic status of people aged 15+):
  (looking for first job + short-term + long-term unemployed) / (those + at work).
- Poverty: Ireland publishes no local child poverty rate, so each ETB gets the overall at-risk-of-poverty
  rate (all ages, below 60% of the median income) of the NUTS 2 region it lies in (Eurostat ilc_li41,
  latest year); the unemployment rate stays as a second, local stand-in.
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
# NUTS 2 regions (2016-): IE04 Northern and Western, IE05 Southern, IE06 Eastern and Midland.
NUTS2 = {"IE04": ["Cavan", "Donegal", "Galway City", "Galway County", "Leitrim", "Mayo", "Monaghan", "Roscommon", "Sligo"],
         "IE05": ["Carlow", "Clare", "Cork City", "Cork County", "Kerry", "Kilkenny", "Limerick", "Tipperary", "Waterford", "Wexford"],
         "IE06": ["Dublin City", "Dún Laoghaire-Rathdown", "Fingal", "South Dublin", "Kildare", "Laois", "Longford", "Louth", "Meath", "Offaly", "Westmeath", "Wicklow"]}
REGION_NAME = {"IE04": "Northern and Western", "IE05": "Southern", "IE06": "Eastern and Midland"}


def arop():
    """{NUTS 2 code: (rate, year)} from Eurostat ilc_li41."""
    d = json.load(open(os.path.join(IN, "eurostat_ilc_li41.json")))
    ids, size = d["id"], d["size"]; cat = {k: list(d["dimension"][k]["category"]["index"]) for k in ids}
    out = {}
    for g in cat["geo"]:
        for t in sorted(cat["time"], reverse=True):
            sel = {k: cat[k][0] for k in ids}; sel.update(geo=g, time=t); i = 0
            for k, n in zip(ids, size): i = i * n + cat[k].index(sel[k])
            if str(i) in d["value"]:
                out[g] = (d["value"][str(i)], t); break
    return out


def key(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(council|and county|city and county|county council|city council)\b", " ", s)
    return re.sub(r"[^a-z]", "", s)


def school_la(la, county):
    """Map the Department of Education's local authority names (some from before the 2014 mergers, e.g.
    "Tipperary (NR) County Council", "Limerick City Council") to the ETB areas above."""
    s = re.sub(r"\(.*?\)|county council|city council|council", " ", (la or county or "").lower()).strip()
    s = re.sub(r"\s+", " ", s)
    city = "city" in (la or "").lower()
    if s in ("cork", "galway"): return f"{s.title()} {'City' if city else 'County'}"
    if s == "dublin": return "Dublin City"
    if s.startswith("dun laoghaire"): return "Dún Laoghaire-Rathdown"
    return s.title()


def enrolment():
    """Pupils in state-aided primary (mainstream and special) and post-primary schools, 2024/25, by ETB area."""
    import openpyxl
    out = {}
    def add(la, county, n):
        a = school_la(la, county)
        etb = next((e for e, las in ETB.items() if a in las), None)
        assert etb, (la, county, a)
        out[etb] = out.get(etb, 0) + int(n or 0)
    wb = openpyxl.load_workbook(os.path.join(IN, "ie_primary_schools_2024_25.xlsx"), read_only=True, data_only=True)
    for sheet in ("Mainstream Schools by Standard", "Special Schools"):
        rows = wb[sheet].iter_rows(values_only=True); next(rows); hdr = list(next(rows))
        for r in rows:
            if r and r[1]: add(r[hdr.index("Local Authority Description")], r[hdr.index("County Description")], r[hdr.index("Enrolment per Return")])
    wb = openpyxl.load_workbook(os.path.join(IN, "ie_postprimary_schools_2024_25.xlsx"), read_only=True, data_only=True)
    rows = wb["Programme & Year"].iter_rows(values_only=True); next(rows); hdr = list(next(rows))
    tot = next(i for i, h in enumerate(hdr) if str(h).startswith("Total"))
    for r in rows:
        if r and r[1]: add(r[hdr.index("Local Authority")], r[hdr.index("County")], r[tot])
    return out


def minutes_counts():
    """Board meetings with minutes on the ETB's own website (inputs/ireland/ie_etb_minutes.json: links to the
    minutes files on each ETB's minutes pages, collected November 2026). One meeting per date in the link text or
    file name; a minutes file dated only by month counts when no other meeting that month is dated."""
    import html, urllib.parse
    sys.path.insert(0, HERE)
    from meeting_dates import parse
    path = os.path.join(IN, "ie_etb_minutes.json")
    if not os.path.exists(path): return {}
    out = {}
    for etb, v in json.load(open(path, encoding="utf-8")).items():
        days, months = set(), set()
        for u, t in v["minutes"].items():
            name = re.sub(r"\.(pdf|docx?)$", "", urllib.parse.unquote(u.rsplit("/", 1)[-1]), flags=re.I).replace("-", " ").replace("_", " ")
            t = html.unescape(t)
            cands = [parse(t), parse(name)]
            m8 = re.search(r"\b(\d{2})(\d{2})(20\d{2})\b", name)            # 23022021
            if m8: cands.append((int(m8.group(3)), int(m8.group(2)), int(m8.group(1))))
            m6 = re.search(r"\b(\d{2}) (\d{2}) (\d{2}) Board", name)         # 26 06 23 Board Minutes
            if m6: cands.insert(0, (2000 + int(m6.group(1)), int(m6.group(2)), int(m6.group(3))))
            full = [c for c in cands if c and c[1] and c[2] and 2010 <= c[0] <= 2026]
            mon = [c for c in cands if c and c[1] and 2010 <= c[0] <= 2026]
            if full: days.add(full[0])
            elif mon: months.add(mon[0][:2])
        months -= {d[:2] for d in days}
        keys = sorted(days) + sorted((y, m, 0) for y, m in months)
        if keys:
            per = {}
            for y, m, d in keys: per[y] = per.get(y, 0) + 1
            latest = max(keys)
            out[etb] = (len(keys), f"{latest[0]:04d}-{latest[1]:02d}" + (f"-{latest[2]:02d}" if latest[2] else ""),
                        "; ".join(f"{y}:{per[y]}" for y in sorted(per)), (v.get("pages") or [""])[0])
    return out


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
    ar = arop()
    enr = enrolment()
    mins = minutes_counts()
    for i, (etb, las) in enumerate(ETB.items()):
        reg = {g for g, members in NUTS2.items() for l in las if l in members}
        assert len(reg) == 1, (etb, reg)
        reg = reg.pop()
        work = sum(lab[l]["work"] for l in las); un = sum(lab[l]["unemp"] for l in las)
        kids = sum(f["properties"]["_kids"] for f in geo["features"] if la_of_feat[id(f)] in las)
        eid = "IE-" + re.sub(r"\W+", "", unicodedata.normalize("NFKD", etb).encode("ascii", "ignore").decode())[:30]
        rows.append({"District": etb, "Region": geo and next((f["properties"]["PROVINCE"] for f in geo["features"] if la_of_feat[id(f)] in las), ""),
                     "Local authority areas": ", ".join(las), "Available Board Meetings": 0,
                     "Meetings note": "No board meetings found on the ETB's YouTube channel; ETBs publish board minutes on their own websites",
                     "Children Ages 5-17": round(kids),
                     "Poverty rate (region, all ages)": f"{ar[reg][0]:.2f}%",
                     "Poverty note": f"Overall at-risk-of-poverty rate of the {REGION_NAME[reg]} region, {ar[reg][1]} (Eurostat); no local or child rate is published",
                     "Unemployment rate (Census 2022)": f"{100 * un / (un + work):.2f}%",
                     "Enrollment": enr[etb], "Enrollment year": "2024/25",
                     "Enrollment note": "All pupils in state-aided primary, special and post-primary schools in the ETB's area (Department of Education), not only the ETB's own schools",
                     "District ID": eid})
        if etb in mins:
            n, latest, years, page = mins[etb]
            rows[-1].update({"Meetings note": "No board meetings found on the ETB's YouTube channel; the count from other sources is board meetings whose minutes the ETB publishes on its website",
                             "Other Board Meetings": n, "Other meetings source": f"board meetings with minutes on the ETB's website ({page})",
                             "Latest meeting": latest, "Meetings by year": years})
        for f in geo["features"]:
            if la_of_feat[id(f)] in las:
                feats.append({"type": "Feature", "properties": {"id": eid, "NAME": f["properties"]["LOCAL_AUTHORITY"].title()}, "geometry": f["geometry"]})
    miss = [f["properties"]["LOCAL_AUTHORITY"] for f in geo["features"] if not la_of_feat[id(f)]]
    with open(os.path.join(HERE, "..", "docs", "data", "ireland.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), restval=""); w.writeheader(); w.writerows(rows)
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
        w = csv.DictWriter(fo, fieldnames=list(dict.fromkeys(k for r in data for k in r)), restval=""); w.writeheader(); w.writerows(data)
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]
    for f in feats:
        f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(HERE, "..", "docs", "data", "map", "ireland.json"), "w"), separators=(",", ":"))
    print(len(rows), "ETBs;", len(feats), "shapes; unmatched local authorities:", miss)
    for r in rows: print(" ", r["District"], r["Poverty rate (region, all ages)"], r["Unemployment rate (Census 2022)"], r["Children Ages 5-17"])


if __name__ == "__main__":
    main()
