"""Build Canadian school board data: child low income (ages 0-17, LIM-AT, 2021 Census / 2020
incomes) for each board, from Statistics Canada census subdivision (CSD) figures and board borders.

Usage (needs internet; see the README):
  python3 data-prep/build_canada.py WORKDIR OUTDIR

Inputs it downloads into WORKDIR:
  - Statistics Canada table 98-10-0103-01 (low income by age, CSD level)
  - lcsd000b21a_e.zip: 2021 CSD cartographic boundaries (from this repo's statcan-csd-2021 release)
  - board borders: BC (DataBC), Manitoba (Manitoba geoportal), Quebec (Données Québec), Alberta
    (Alberta geospatial services)

Each board's children and low-income children are the sum over the CSDs inside its border; a CSD
split between boards is shared by land area. Provinces without published borders are built from
counties or regions (Nova Scotia, New Brunswick, Northwest Territories), and province- or
territory-wide boards use the whole province or territory. Outputs: OUTDIR/canada.csv and
OUTDIR/canada_boards.geojson.
"""
import csv, io, json, os, re, sys, time, urllib.request, zipfile

import geopandas as gpd
import pandas as pd

UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
PROV = {"10": "NL", "11": "PE", "12": "NS", "13": "NB", "24": "QC", "35": "ON", "46": "MB", "47": "SK",
        "48": "AB", "59": "BC", "60": "YT", "61": "NT", "62": "NU"}


def fetch(url, path):
    if os.path.exists(path):
        return path
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=900) as r, open(path, "wb") as f:
                f.write(r.read())
            return path
        except Exception as e:
            print("retry", url[:100], e); time.sleep(15)
    raise RuntimeError(f"could not download {url}")


def low_income_by_csd(work):
    z = zipfile.ZipFile(fetch("https://www150.statcan.gc.ca/n1/tbl/csv/98100103-eng.zip", f"{work}/98100103.zip"))
    name = [n for n in z.namelist() if not n.endswith("MetaData.csv")][0]
    rows = csv.reader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig"))
    head = next(rows)
    col = {h: i for i, h in enumerate(head)}
    gender = [h for h in head if h.startswith("Gender")][0]
    age = [h for h in head if h.startswith("Age")][0]
    year = [h for h in head if h.startswith("Year")][0]
    total = [h for h in head if "Total - Individual low-income status based on low-income measure, after tax" in h][0]
    low = [h for h in head if h.endswith("In low income (LIM-AT)[2]")][0]
    out, years, ages = {}, set(), set()
    for r in rows:
        if len(r) < len(head):
            continue   # footnote or blank lines
        years.add(r[col[year]]); ages.add(r[col[age]])
        if not r[col[gender]].startswith("Total") or r[col[age]] != "0 to 17 years":
            continue
        dg = r[col["DGUID"]]
        if dg[4:9] != "A0005":
            continue
        out.setdefault(r[col[year]], {})[dg[-7:]] = (float(r[col[total]] or 0), float(r[col[low]] or 0))
    print("ages", sorted(ages), "years", sorted(years))
    y = max(out)   # latest income year
    print("using income year", y, len(out[y]), "CSDs")
    return out[y], y


def esri_geojson(url):
    feats, offset = [], 0
    while True:
        u = f"{url}/query?where=1%3D1&outFields=*&outSR=4326&f=geojson&resultOffset={offset}&resultRecordCount=1000"
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r:
            j = json.load(r)
        feats += j.get("features", [])
        if not j.get("properties", {}).get("exceededTransferLimit") and len(j.get("features", [])) < 1000:
            break
        offset += 1000
    return gpd.GeoDataFrame.from_features(feats, crs=4326)


def find_alberta():
    """Alberta's board layers: search the geospatial server's folders for education services."""
    base = "https://geospatial.alberta.ca/titan/rest/services"
    found = []
    try:
        with urllib.request.urlopen(urllib.request.Request(base + "?f=json", headers=UA), timeout=120) as r:
            root = json.load(r)
        for folder in root.get("folders", []):
            with urllib.request.urlopen(urllib.request.Request(f"{base}/{folder}?f=json", headers=UA), timeout=120) as r:
                for s in json.load(r).get("services", []):
                    if re.search(r"edu|school", s["name"], re.I):
                        found.append(f"{base}/{s['name']}/{s['type']}")
    except Exception as e:
        print("alberta search failed", e)
    layers = []
    for svc in found:
        try:
            with urllib.request.urlopen(urllib.request.Request(svc + "?f=json", headers=UA), timeout=120) as r:
                for l in json.load(r).get("layers", []):
                    if re.search(r"authorit|jurisdiction|district", l["name"], re.I):
                        layers.append((l["name"], f"{svc}/{l['id']}"))
        except Exception as e:
            print("alberta layer list failed", svc, e)
    print("alberta services", found, "layers", layers)
    return layers


def boards(work):
    """Board polygons with columns: id, name, province, type, website."""
    out = []
    bc = gpd.read_file(fetch("https://openmaps.gov.bc.ca/geo/pub/WHSE_TANTALIS.TA_SCHOOL_DISTRICTS_SVW/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=WHSE_TANTALIS.TA_SCHOOL_DISTRICTS_SVW&outputFormat=application/json&srsName=EPSG:4326", f"{work}/bc.geojson"))
    out.append(gpd.GeoDataFrame({"id": "CA-BC-SD" + bc.SCHOOL_DISTRICT_NUMBER.astype(int).astype(str).str.zfill(2),
        "name": "School District " + bc.SCHOOL_DISTRICT_NUMBER.astype(int).astype(str) + " (" + bc.SCHOOL_DISTRICT_NAME + ")",
        "province": "BC", "type": "Public", "website": ""}, geometry=bc.geometry, crs=bc.crs))
    mb = gpd.read_file(fetch("https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_School_Divisions/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson", f"{work}/mb.geojson"))
    out.append(gpd.GeoDataFrame({"id": "CA-MB-" + mb.School_Div.str.replace(r"\W+", "", regex=True),
        "name": mb.School_Div + " School Division", "province": "MB", "type": "Public", "website": mb.get("Website", "")}, geometry=mb.geometry, crs=mb.crs))
    zipfile.ZipFile(fetch("https://www.donneesquebec.ca/recherche/dataset/37d944eb-335b-40fe-8d80-835ff77bc5cb/resource/2ded8ebe-5e71-4dff-91de-896b4150e19c/download", f"{work}/qc.zip")).extractall(f"{work}/qc")
    for shp, typ in [("CS_FRA.shp", "French"), ("CS_ANG.shp", "English"), ("CS_STA.shp", "Special status")]:
        q = gpd.read_file(f"{work}/qc/{shp}")
        out.append(gpd.GeoDataFrame({"id": "CA-QC-" + q.CD_CS.astype(str), "name": q.NOM_LONG, "province": "QC", "type": typ,
            "website": q.SITE_WEB}, geometry=q.geometry, crs=q.crs))
    for lname, url in find_alberta():
        try:
            a = esri_geojson(url)
        except Exception as e:
            print("alberta download failed", url, e); continue
        namecol = next((c for c in a.columns if re.search(r"name", c, re.I)), None)
        codecol = next((c for c in a.columns if re.search(r"code|number|auth", c, re.I) and c != namecol), None)
        print("alberta layer", lname, len(a), list(a.columns)[:12])
        typ = "Separate (Catholic)" if re.search(r"separ", lname, re.I) else "Francophone" if re.search(r"franco", lname, re.I) else "Public"
        if re.search(r"unorgan", lname, re.I):
            continue
        out.append(gpd.GeoDataFrame({"id": "CA-AB-" + (a[codecol].astype(str) if codecol else a.index.astype(str)) + "-" + typ[:3],
            "name": a[namecol] if namecol else lname, "province": "AB", "type": typ, "website": ""}, geometry=a.geometry, crs=a.crs))
    return pd.concat([b.to_crs(3347) for b in out], ignore_index=True)


# Boards built from census divisions (counties/regions) where no border file is published.
NS_RCE = {"Tri-County Regional Centre for Education": ["1201", "1202", "1203"], "South Shore Regional Centre for Education": ["1204", "1206"],
          "Annapolis Valley Regional Centre for Education": ["1205", "1207", "1208W"], "Halifax Regional Centre for Education": ["1209"],
          "Chignecto-Central Regional Centre for Education": ["1208E", "1210", "1211", "1212"],
          "Strait Regional Centre for Education": ["1213", "1214", "1215", "1216"], "Cape Breton-Victoria Regional Centre for Education": ["1217", "1218"]}
NB = {"Anglophone School District South": (["1301", "1302", "1305"], "English"), "Anglophone School District West": (["1303", "1304", "1310", "1311", "1312", "1313"], "English"),
      "Anglophone School District East": (["1306", "1307", "1308"], "English"), "Anglophone School District North": (["1309", "1314", "1315"], "English"),
      "District scolaire francophone Nord-Ouest": (["1312", "1313", "1314W"], "French"), "District scolaire francophone Nord-Est": (["1309", "1314E", "1315"], "French"),
      "District scolaire francophone Sud": (["1301", "1302", "1303", "1304", "1305", "1306", "1307", "1308", "1310", "1311"], "French")}
NT = {"Beaufort-Delta Divisional Education Council": ["6101"], "Sahtu Divisional Education Council": ["6102"], "Tłı̨chǫ Community Services Agency": ["6103"],
      "Dehcho Divisional Education Council": ["6104"], "South Slave Divisional Education Council": ["6105"], "Yellowknife Education District No. 1": ["6106"],
      "Yellowknife Catholic Schools": ["6106"]}
WIDE = [("Conseil scolaire francophone de la Colombie-Britannique", "BC", "Francophone"), ("Division scolaire franco-manitobaine", "MB", "Francophone"),
        ("Conseil scolaire acadien provincial", "NS", "Francophone"), ("Public Schools Branch", "PE", "English"),
        ("Commission scolaire de langue française", "PE", "Francophone"), ("NLSchools (Department of Education)", "NL", "English"),
        ("Conseil scolaire francophone provincial de Terre-Neuve-et-Labrador", "NL", "Francophone"),
        ("Commission scolaire francophone du Yukon", "YT", "Francophone"), ("Yukon First Nation School Board", "YT", "First Nation"),
        ("Commission scolaire francophone des Territoires du Nord-Ouest", "NT", "Francophone"), ("Commission scolaire francophone du Nunavut", "NU", "Francophone")]


def main(work, outdir):
    os.makedirs(work, exist_ok=True); os.makedirs(outdir, exist_ok=True)
    li, year = low_income_by_csd(work)
    csd = gpd.read_file("zip://" + fetch("https://github.com/amaar-a1/School-Board-Meeting-and-Poverty-Data/releases/download/statcan-csd-2021/lcsd000b21a_e.zip", f"{work}/csd.zip")).to_crs(3347)
    csd["kids"] = csd.CSDUID.map(lambda u: li.get(u, (0, 0))[0])
    csd["low"] = csd.CSDUID.map(lambda u: li.get(u, (0, 0))[1])
    csd["area"] = csd.geometry.area
    csd["CD"] = csd.CSDUID.str[:4]
    # split counties used by two boards
    csd.loc[(csd.CD == "1208") & csd.CSDNAME.str.contains("West Hants", case=False), "CD"] = "1208W"
    csd.loc[csd.CD == "1208", "CD"] = "1208E"
    west_rest = csd.CSDNAME.str.contains("Kedgwick|Saint-Quentin|Grimmer|Saint-Jean-Baptiste-de-Restigouche", case=False)
    csd.loc[(csd.CD == "1314") & west_rest, "CD"] = "1314W"
    csd.loc[csd.CD == "1314", "CD"] = "1314E"
    print("CSDs", len(csd), "children", csd.kids.sum(), "low income", csd.low.sum())

    rows, shapes = [], []
    poly = boards(work)
    inter = gpd.overlay(csd[["CSDUID", "kids", "low", "area", "geometry"]], poly[["id", "geometry"]], how="intersection", keep_geom_type=True)
    inter["share"] = inter.geometry.area / inter.area
    agg = inter.assign(k=inter.kids * inter.share, l=inter.low * inter.share).groupby("id")[["k", "l"]].sum()
    for _, b in poly.iterrows():
        k, l = agg.loc[b.id] if b.id in agg.index else (0, 0)
        rows.append({"id": b.id, "name": b["name"], "province": b.province, "type": b.type, "kids": round(k), "low": round(l),
                     "method": "Census subdivisions inside the board's published border (split ones shared by land area)", "website": b.website})
        shapes.append({"id": b.id, "geometry": b.geometry})

    def from_cds(name, prov, typ, cds, how):
        sub = csd[csd.CD.isin(cds)]
        rows.append({"id": f"CA-{prov}-" + re.sub(r"\W+", "", name)[:40], "name": name, "province": prov, "type": typ,
                     "kids": round(sub.kids.sum()), "low": round(sub.low.sum()), "method": how, "website": ""})
        return sub.dissolve().geometry.iloc[0] if len(sub) else None

    for name, cds in NS_RCE.items():
        g = from_cds(name, "NS", "English", cds, "Approximated from the counties it serves (no published border)")
        shapes.append({"id": rows[-1]["id"], "geometry": g})
    for name, (cds, typ) in NB.items():
        g = from_cds(name, "NB", typ, cds, "Approximated from the counties it serves (no published border); anglophone and francophone districts overlap")
        if typ == "English":
            shapes.append({"id": rows[-1]["id"], "geometry": g})
    for name, cds in NT.items():
        g = from_cds(name, "NT", "Catholic" if "Catholic" in name else "Public", cds, "Approximated from the census region it serves (no published border)")
        if "Catholic" not in name:
            shapes.append({"id": rows[-1]["id"], "geometry": g})
    for name, prov, typ in WIDE:
        pr = [k for k, v in PROV.items() if v == prov][0]
        sub = csd[csd.CSDUID.str[:2] == pr]
        rows.append({"id": f"CA-{prov}-" + re.sub(r"\W+", "", name)[:40], "name": name, "province": prov, "type": typ,
                     "kids": round(sub.kids.sum()), "low": round(sub.low.sum()),
                     "method": "Serves the whole province or territory, so its figures are province- or territory-wide", "website": ""})
    for r in rows:
        r["pct"] = f"{100 * r['low'] / r['kids']:.2f}%" if r["kids"] else ""
    with open(f"{outdir}/canada.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["District", "Province", "Board type", "Children Ages 0-17", "Children Ages 0-17 in Low Income",
                    "Percentage of Children Ages 0-17 in Low Income", "How poverty was calculated", "Website", "District ID"])
        for r in sorted(rows, key=lambda r: (r["province"], r["name"])):
            w.writerow([r["name"], r["province"], r["type"], r["kids"], r["low"], r["pct"], r["method"], r["website"], r["id"]])
    shp = gpd.GeoDataFrame(shapes, geometry="geometry", crs=3347).dropna().to_crs(4326)
    shp.to_file(f"{outdir}/canada_boards.geojson", driver="GeoJSON")
    print(len(rows), "boards;", len(shp), "shapes; income year", year)


if __name__ == "__main__":
    main(*sys.argv[1:3])
