"""Turns the Georgia downloads (made on GitHub's runner from Geostat's site) into the small inputs build_latam.georgia()
reads (data-prep/inputs/georgia/).

- geo_geo.geojson: municipalities from geoBoundaries gbOpen GEO ADM2 (simplified). The self-governing cities of Batumi,
  Kutaisi, Rustavi and Poti have no border of their own there. Abkhazia's districts and Java (South Ossetia), outside the
  Georgian government's control, are kept as places with no data.
- geo_data.json, per municipality (IDs GEO-01..65 as in fetch/lists/georgia.csv, alphabetical):
  pop: Geostat, "Population as of 1 January by regions and self-governed units" (01-population-by-self-governed-unit.xlsx), latest year;
  pupils: Geostat, "Number of schools, pupils and teachers by municipalities" (11_...by-Municipalities.xlsx, sheet pupils),
    public and private general schools, latest school year;
  tsa: Geostat (from the Social Service Agency), "Number of families registered in the Targeted Social Assistance program
    database and receiving subsistence allowance by municipalities", end of the latest year;
  ka: the municipality's Georgian name (Georgian Wikipedia); meetings: the council's (sakrebulo's) YouTube channel (fetch/ge_yt.py).
Usage: python3 data-prep/prep_georgia.py RAWDIR GEODIR LISTCSV GE_MEET_JSON
"""
import csv, glob, json, os, re, sys
import openpyxl, xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "georgia")
key = lambda s: re.sub(r"[^a-z]", "", re.sub(r"municipality|city of|^c\.|city|tbilisi city", "", str(s).lower().replace("tbilisi city", "tbilisi")))
ALIAS = {"dedoplistskaro": "dedoplistsqaro", "dedoflistskaros": "dedoplistsqaro", "tetrisqaro": "tetritsqaro", "tetritskaro": "tetritsqaro", "sighnaghi": "sighnagi",
         "signagi": "sighnagi", "qvareli": "kvareli", "bagdati": "baghdati", "tkibuli": "tqibuli", "tskaltubo": "tsqaltubo"}
OCCUPIED = {"Akhalgori": "South Ossetia (Tskhinvali region)", "Gagra": "Abkhazia", "Gali": "Abkhazia", "Gudauta": "Abkhazia", "Gulripshi": "Abkhazia", "Ochamchire": "Abkhazia", "Sokhumi": "Abkhazia",
            "Java": "South Ossetia (Tskhinvali region)"}


def find(raw, pat):
    return sorted(glob.glob(os.path.join(raw, "**", pat), recursive=True))[-1]


def rows_xls(path, sheet=0):
    if path.lower().endswith(".xls"):
        sh = xlrd.open_workbook(path).sheet_by_index(sheet)
        return [sh.row_values(i) for i in range(sh.nrows)]
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet] if isinstance(sheet, str) else wb.worksheets[sheet]
    return [list(r) for r in ws.iter_rows(values_only=True)]


def latest(rows, add=False):
    """{key(name): (value, year)} from a table with years in a header row and names in the first column."""
    hdr = next(r for r in rows if sum(isinstance(c, (int, float)) and 1990 < float(c) < 2100 or bool(re.match(r"20\d\d/20\d\d", str(c))) for c in r) >= 5)
    cols = [(i, str(c)) for i, c in enumerate(hdr) if c not in (None, "")]
    cols = [(i, re.sub(r"\.0$|\*$", "", y)) for i, y in cols if re.match(r"(19|20)\d\d", y)]
    out = {}
    for r in rows:
        if not r or not isinstance(r[0], str): continue
        for i, y in reversed(cols):
            v = r[i] if i < len(r) else None
            if isinstance(v, (int, float)):
                k = ALIAS.get(key(r[0]), key(r[0]))
                if add and k in out and y == out[k][1]: out[k] = (out[k][0] + v, y)   # "Akhaltsikhe City" + "Akhaltsikhe Municipality"
                elif k not in out or y > out[k][1]: out[k] = (v, y)   # a former self-governing city (e.g. Ozurgeti, to 2017) shares the name
                break
    return out


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def main(raw, geo, listcsv, meet):
    pop = latest(rows_xls(find(raw, "*01_population_by_self_governed_unit.xlsx")))
    pup = latest(rows_xls(find(raw, "*11_Number_of_schools_Pupils_Teachers_by_Municipalities.xlsx"), "pupils"))
    # The allowance table splits some towns into "... City" and "... Municipality" rows (the same municipality today), so add them;
    # it has no row for Akhalkalaki.
    tsa = latest(rows_xls(find(raw, "*subsistence_allowance_by_municipal*.xls")), add=True)
    mt = json.load(open(meet, encoding="utf-8"))
    g = {ALIAS.get(key(f["properties"]["shapeName"]), key(f["properties"]["shapeName"])): f for f in json.load(open(os.path.join(geo, "geoBoundaries-GEO-ADM2_simplified.geojson"), encoding="utf-8"))["features"]}
    data, feats, miss = {}, [], []
    for r in csv.DictReader(open(listcsv, encoding="utf-8")):
        if r["District"] in OCCUPIED: continue
        k = ALIAS.get(key(r["District"]), key(r["District"]))
        x = {"name": r["District"], "ka": r["ka"], "city": r["District"] in ("Tbilisi", "Batumi", "Kutaisi", "Rustavi", "Poti")}
        for f, d, scale in (("pop", pop, 1000), ("pupils", pup, 1), ("tsa", tsa, 1)):
            if k in d: x[f] = round(d[k][0] * scale); x[f + "_year"] = d[k][1]
            else: miss.append((r["District"], f))
        m = mt.get(r["District ID"]) or {}
        x["meetings"] = {"channel": m.get("channel", ""), "url": m.get("url", ""), "videos": m.get("videos", [])}
        data[r["District ID"]] = x
        if k in g:
            f = g.pop(k)
            feats.append({"type": "Feature", "properties": {"id": r["District ID"], "NAME": r["District"]}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    for n, region in OCCUPIED.items():
        f = g.pop(key(n))
        did = "GEO-X" + key(n)[:4].upper()
        data[did] = {"name": n, "occupied": region}
        feats.append({"type": "Feature", "properties": {"id": did, "NAME": n}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "geo_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "geo_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(len(data), "places;", len(feats), "borders; unused borders", list(g), "; missing", miss)
    v = [x for x in data.values() if "pop" in x]
    print("pop", sum(x["pop"] for x in v), "pupils", sum(x.get("pupils", 0) for x in v), "tsa", sum(x.get("tsa", 0) for x in v), {x.get("pop_year") for x in v}, {x.get("pupils_year") for x in v}, {x.get("tsa_year") for x in v})


if __name__ == "__main__":
    main(*sys.argv[1:])
