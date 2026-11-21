"""Turns the South Africa downloads (made on GitHub's runner) into the small inputs build_latam.south_africa() reads
(data-prep/inputs/south_africa/).

- zaf_geo.geojson: the 213 municipalities (8 metropolitan and 205 local municipalities), from geoBoundaries gbOpen ZAF
  ADM3 (simplified), matched by name.
- zaf_data.json, per municipality (Municipal Demarcation Board code):
  name, province, pop, area: English Wikipedia, "List of municipalities in South Africa" (Census 2022 population, area);
  pupils, public, q13, q_known: Department of Basic Education, national masterlist of ordinary schools, 2023 (EMIS):
    learners in open schools by local municipality; public-school learners; public-school learners in quintile 1-3
    schools (the poorest communities' no-fee schools) and in public schools with a quintile. Independent schools count
    as private.
  meetings: the municipal council's YouTube channel (fetch/nyt.py, ZA).
Usage: python3 data-prep/prep_south_africa.py RAWDIR GEODIR
"""
import csv, glob, html, json, os, re, sys, unicodedata
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "south_africa")


def key(s):
    k = re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())
    k = re.sub(r"(localmunicipality|localmunicpality|metropolitanmunicipality|municipality)$", "", k)
    k = re.sub(r"^(cityof|localmunicipalityof|of)", "", k)
    return ALIAS.get(k, k)


# Names in the masterlist or on the map that differ from the current list (renamed or merged municipalities).
ALIAS = {"fetakgomogreatertubatse": "fetakgomotubatse", "greatertubatsefetakgomo": "fetakgomotubatse", "mbizana": "winniemadikizelamandela",
         "ingquzahill": "ngquzahill", "thembisile": "thembisilehani", "solplaatje": "solplaatjie", "engcobo": "drabxuma", "umfolozi": "mfolozi",
         "ubuhlebezwe": "johannesphumaniphungula", "drpixleykaisakaseme": "pixleykaseme", "pixleykaisakaseme": "pixleykaseme",
         "modimolle": "modimollemookgophong", "mookgopong": "modimollemookgophong", "umsombomvu": "umsobomvu", "mhlontlo": "kumkanimhlontlo",
         "tlokwe": "jbmarks", "ventersdorptlokwe": "jbmarks", "rusternburg": "rustenburg", "mafikeng": "mahikeng", "chiefalbertluthuli": "albertluthuli",
         "lepellenkumpi": "lepelenkumpi", "randwest": "randwestcity", "matlosana": "matlosana", "renosterberglocalmunicpality": "renosterberg", "themsunduzi": "msunduzi"}


def find(raw, pat):
    return sorted(glob.glob(os.path.join(raw, "**", pat), recursive=True))[-1]


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 3), round(c[1], 3)]


def main(raw, geo):
    cl = lambda c: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>|\[\d+\]", "", c))).strip()
    num = lambda v: float(v.replace(",", "")) if re.match(r"[\d,.]+$", v or "") else None
    s = open(find(raw, "w_za.html"), encoding="utf-8").read()
    muni = {}
    for t in re.findall(r"<table.*?</table>", s, re.S):
        rows = [[cl(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)] for r in re.findall(r"<tr.*?</tr>", t, re.S)]
        if not rows or rows[0][:2] != ["Name", "Code"] or "Dissolved" in rows[0]: continue
        local = "District" in rows[0]
        for r in rows[2:]:
            if len(r) < 8 or r[1].startswith("DC"): continue
            # Local municipalities: name, code, province, district, seat, category, area km2, area sq mi, population, density...
            area, pop = (num(r[6]), num(r[8])) if local else (num(r[4]), num(r[6]))
            muni.setdefault(r[1], {"name": re.sub(r"\s+(Local|Metropolitan) Municipality$", "", r[0]), "province": r[2], "area": area, "pop": int(pop) if pop else None,
                                   "metro": not local})
    assert len(muni) == 213, len(muni)
    PROV = {"EC": "Eastern Cape", "MP": "Mpumalanga"}
    kk = lambda name, prov: key(name) + ("-" + prov if key(name) == "emalahleni" else "")
    K = {kk(x["name"], x["province"]): c for c, x in muni.items()}
    for x in muni.values(): x.update(pupils=0, public=0, q13=0, q_known=0)
    ws = openpyxl.load_workbook(find(raw, "za_master_new1.xlsx"), read_only=True).worksheets[0]
    it = ws.iter_rows(values_only=True); h = next(it); ix = {c: i for i, c in enumerate(h)}
    lost, LOST = 0, {}
    for r in it:
        if str(r[ix["Status"]]).upper() != "OPEN": continue
        n = r[ix["Learners2023"]] or 0
        c = K.get(kk(r[ix["LMunName"]], PROV.get(str(r[ix["Province"]]), "")))
        if not c: lost += n; LOST[r[ix["LMunName"]]] = LOST.get(r[ix["LMunName"]], 0) + n; continue
        x = muni[c]; x["pupils"] += n
        if str(r[ix["Sector"]]).upper() == "PUBLIC":
            x["public"] += n; q = str(r[ix["Quintile"]] or "")
            if re.match(r"Q?[1-5]$", q): x["q_known"] += n; x["q13"] += n if q[-1] in "123" else 0
    lat = lambda f: (lambda c: sum(p[1] for p in c) / len(c))(f["geometry"]["coordinates"][0] if f["geometry"]["type"] == "Polygon" else f["geometry"]["coordinates"][0][0])
    g = {kk(f["properties"]["shapeName"], "Mpumalanga" if lat(f) > -28 else "Eastern Cape"): f for f in json.load(open(os.path.join(geo, "geoBoundaries-ZAF-ADM3_simplified.geojson"), encoding="utf-8"))["features"]}
    feats = []
    for c, x in muni.items():
        f = g.pop(kk(x["name"], x["province"]), None)
        if f: feats.append({"type": "Feature", "properties": {"id": f"ZAF-{c}", "NAME": x["name"]}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    print("no border:", [x["name"] for c, x in muni.items() if f"ZAF-{c}" not in {f["properties"]["id"] for f in feats}], "unused borders:", list(g))
    os.makedirs(OUT, exist_ok=True)
    json.dump(muni, open(os.path.join(OUT, "zaf_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "zaf_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    tp = sum(x["pupils"] for x in muni.values()); pb = sum(x["public"] for x in muni.values())
    print(len(muni), "municipalities; learners", tp, "public", round(100 * pb / tp, 1), "% ; not placed", lost, "; pop", sum(x["pop"] or 0 for x in muni.values()),
          "; Q1-3 share", round(100 * sum(x["q13"] for x in muni.values()) / sum(x["q_known"] for x in muni.values()), 1),
          "; no learners:", [x["name"] for x in muni.values() if not x["pupils"]], sorted(LOST.items(), key=lambda v: -v[1])[:12])


if __name__ == "__main__":
    main(*sys.argv[1:])
