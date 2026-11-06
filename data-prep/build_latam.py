"""Build docs/data/chile.csv, docs/data/colombia.csv and their map files.

Chile: 345 comunas. Public schools are run by each municipality (its education department, DAEM, or
corporation) or, where the 2017 reform has reached, by a Local Public Education Service (SLEP).
- Poverty: Ministerio de Desarrollo Social y Familia, small-area estimates (SAE) 2024: share of people
  (all ages) in income poverty; the multidimensional rate is a second column. No child rate is
  published by comuna.
- Enrollment: Mineduc, Resumen de Matrícula por Establecimiento 2026, added up by comuna.
Colombia: 1,122 municipalities. Schools are run by the 96 "certified" territorial entities (ETC:
departments, districts and larger municipalities); the others' schools are run by their department.
- Poverty: DANE, multidimensional poverty index (IPM) by municipality from the 2018 census, all ages.
- Enrollment (estimated): Ministry of Education statistics by municipality, 2024: children 5-16 times
  the net enrollment rate for ages 5-16 (datos.gov.co nudc-7mev).
Both:
- Borders: geoBoundaries (gbOpen) ADM3 (Chile) and ADM2 (Colombia), simplified. Colombian municipalities
  are matched by name within their department, found from where each lies.
- Meetings (stand-in): municipal council (concejo municipal) sessions on the municipality's or council's
  own YouTube channel (nordic_youtube.py, countries CL and CO), its education committee where recorded,
  counted once per day.
- Locale (estimated): people per km² (Chile: projected population; Colombia: children 5-16 / 0.19).
Usage: python3 data-prep/build_latam.py
"""
import csv, json, os, re, sys, unicodedata
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2
from meeting_dates import parse as parse_date, summary as date_summary
from shared_titles import shared_titles

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs")
DOCS = os.path.join(HERE, "..", "docs", "data")
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())
ALIAS = {"CL": {"paiguano": "paihuano", "marchigue": "marchihue", "aisen": "aysen", "coihaique": "coyhaique", "llayllay": "llaillay", "padrelascasas": "padrelascasas",
                "ohiggins": "ohiggins", "trehuaco": "treguaco", "lascabras": "lascabras", "cabodehornos": "cabodehornos"},
         "CO": {"bogota": "bogotadc", "bogotadistritocapital": "bogotadc", "sanandres": "sanandres", "cartagena": "cartagenadeindias",
                "guadalajaradebuga": "buga", "santafedebogota": "bogotadc", "sanandresdetumaco": "tumaco", "sanjosedecucuta": "cucuta",
                "sanjosedetoluviejo": "toluviejo", "villadesandiegodeubate": "ubate", "tiquisio": "tiquiso", "papunahua": "papunauacordepartamental",
                "colosoricaurte": "coloso", "elsantuario": "santuario"},
         "MX": {"tlaquepaque": "sanpedrotlaquepaque"}}
EDU = re.compile(r"comisi[óo]n (de )?educaci[óo]n|educaci[óo]n.*comisi[óo]n|comisi[óo]n de cultura y educaci[óo]n", re.I)
COUNCIL = re.compile(r"sesi[óo]n|plenaria|concejo", re.I)
COUNCIL_MUST = re.compile(r"concejo|sesi[óo]n (ordinaria|extraordinaria|plenaria|n[°º.]|del concejo)|plenaria", re.I)
NOT_T = re.compile(r"live session|cuenta p[úu]blica|entrevista|noticias|resumen|capsula|cápsula|juvenil|infantil|niñ|elecci|campaña|candidat|aniversario|fiesta|"
                   r"himno|desfile|tedeum|te deum|saludo|felicit|programa|podcast|rendici[óo]n", re.I)


def pip(pt, geom):
    """Point in polygon (ray casting) for a Polygon or MultiPolygon."""
    x, y = pt
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        ring = poly[0]; inside = False; j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]; xj, yj = ring[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: inside = not inside
            j = i
        if inside: return True
    return False


def centroid(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    ring = max((p[0] for p in polys), key=len)
    a = cx = cy = 0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        c = x0 * y1 - x1 * y0; a += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    return (cx / (3 * a), cy / (3 * a)) if a else tuple(ring[0])


_CACHE = {}
DIRS = {"CL": "chile", "CO": "colombia", "MX": "mexico", "BR": "brazil"}
# Brazil: municipal chambers (câmara municipal) and their education committees, in Portuguese.
RULES = {"BR": (re.compile(r"comiss[ãa]o (permanente )?de educa[çc][ãa]o|educa[çc][ãa]o.*comiss[ãa]o", re.I),
                re.compile(r"sess[ãa]o|c[âa]mara", re.I),
                re.compile(r"sess[ãa]o (ordin[áa]ria|extraordin[áa]ria|solene|especial|de |da |n[°º.]|\d)|\d+[ªa]? sess[ãa]o|sess[ãa]o plen", re.I),
                re.compile(r"live session|entrevista|not[íi]cias|resumo|podcast|programa|campanha|candidat|anivers[áa]rio|festa|hino|desfile|"
                           r"homenagem|solene|culto|missa|show|jogo|futebol|sess[ãa]o de fotos", re.I))}


def meetings(cc, did):
    d = os.path.join(IN, DIRS[cc], "youtube")
    files = sorted(f for f in os.listdir(d) if re.fullmatch(rf"{cc}(_\d+)?_youtube\.csv", f)) if os.path.isdir(d) else []   # one file, or one per shard
    if not files: return 0, "", [], ""
    if cc not in _CACHE:
        titles = {}
        for f in sorted(os.listdir(d)):
            if re.fullmatch(r"titles(_\d+)?\.json", f): titles.update(json.load(open(os.path.join(d, f), encoding="utf-8")))
        titles.update(shared_titles())
        _CACHE[cc] = ({r["District ID"]: r for f in files for r in csv.DictReader(open(os.path.join(d, f), encoding="utf-8"))}, titles)
    rows, titles = _CACHE[cc]
    r = rows.get(did) or {}
    url = r.get("Channel URL", "")
    if not url or url not in titles or url in NOT_CHANNELS.get(cc, set()): return 0, "", [], ""
    edu, council, must, not_t = RULES.get(cc, (EDU, COUNCIL, COUNCIL_MUST, NOT_T))
    vids = [t for t in titles[url] if not not_t.search(t)]
    for keep, kind in (([t for t in vids if edu.search(t)], "Education committee"),
                       ([t for t in vids if council.search(t) and must.search(t) and not edu.search(t)], "Council (stand-in)")):
        keys = {parse_date(t) or re.sub(r"\b(parte|part)\s*\d+\b|\(\d\)|\d/\d", "", t, flags=re.I).strip().lower() for t in keep}
        if keys: return len(keys), url, keep, kind
    return 0, "", [], ""


# Channels checked by hand and found to be another place's (by channel URL). The search matched on the name, and
# many of these names exist in other Spanish-speaking countries too, or in both Chile and Colombia.
NOT_CHANNELS = {
    "MX": set(), "BR": set(),
    "CL": {"https://www.youtube.com/channel/UC70nQc3caJyhIQQHlwBb_RA",    # La Molina, Lima (Peru), not Molina
           "https://www.youtube.com/channel/UCgvUIPWaySeDAGe-oUTSDUA",    # La Unión, Costa Rica ("Concejo de Distrito")
           "https://www.youtube.com/channel/UCQgCHXXxl4IyPg0GEULz2RA",    # San Carlos, Costa Rica
           "https://www.youtube.com/channel/UC3rWA_wd9eyOA1T0WuMTZQg",    # San Ramón, Costa Rica (regidores, cantonal)
           "https://www.youtube.com/channel/UCZXpwy8DfsnN1x61GBQB0ZA",    # Santa Cruz, Bolivia
           "https://www.youtube.com/channel/UCdjGfVXeZ7nu1QYlS49q91g",    # El Retiro, Antioquia (Colombia's Retiro)
           "https://www.youtube.com/channel/UCe1pVTpAU89txiLiGPFe3YA"},   # La Calera, Cundinamarca (Colombia's)
    "CO": {"https://www.youtube.com/channel/UCj983fAuispRHiUb9KfZH0Q",    # Santa Lucía, Corrientes (Argentina)
           "https://www.youtube.com/channel/UCzxvBsAVswjwc6dRN4uglWA",    # a Colón with "Sesión de Cabildo" (Mexico/Panama)
           "https://www.youtube.com/channel/UClJErJ8eEEUQ6cIJOfn1TFw",    # La Chorrera, Panama
           "https://www.youtube.com/channel/UCkV-Fcci5WXRTNKk3EI43cg",    # San Marcos, El Salvador
           "https://www.youtube.com/channel/UChP0E7AeiBDBKFRrYBhrEgw",    # San Cristóbal, Táchira (Venezuela)
           "https://www.youtube.com/channel/UCZaI4dep0kp5vZa3gCsEwLQ",    # Santo Domingo, Chile ("I.M.")
           "https://www.youtube.com/channel/UCK7OgXBRvGeUy0op536HsNg",    # Villarrica, Chile ("Cuenta Pública")
           "https://www.youtube.com/channel/UC3rOsD5LY68opkbDQnSjA7A",    # Santiago, Chile's capital
           "https://www.youtube.com/channel/UC3t9uauFej-XiU3VoNWKB-A"},   # Santiago, Dominican Republic (Ayuntamiento)
}


FOREIGN = re.compile(r"deliberante|distrital de carmen alto|municipalidad distrital|provincial", re.I)   # Argentina's and Peru's councils


def owners(cc, rows):
    """Which district each channel belongs to. Many places share a name (Colombia has three Granadas and four
    Villanuevas), so the search found the same channel for several. A channel counts for one district only:
    the one whose longer full name, or whose department, the channel name gives; if none does, for none.
    A channel naming a different department is dropped."""
    if cc not in _CACHE: return {}
    yt = _CACHE[cc][0]
    words = lambda s: " " + re.sub(r"[^a-z]+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()) + " "
    regions = {words(r["Region"]).strip() for r in rows if r.get("Region")}
    by = {}
    for r in rows:
        y = yt.get(r["District ID"]) or {}
        if y.get("Channel URL"): by.setdefault(y["Channel URL"], []).append(r)
    own = {}
    for url, rs in by.items():
        ch = words((yt.get(rs[0]["District ID"]) or {}).get("Channel", ""))
        if FOREIGN.search(ch): continue
        def score(r):
            nm = words(r["District"]).strip()
            if " " + nm + " " not in ch: return -1
            other = any(" " + g + " " in ch for g in regions - {words(r["Region"]).strip()} if " " + g + " " not in " " + nm + " ")
            named = " " + words(r["Region"]).strip() + " " in ch or (cc == "CO" and words(r["Region"]).split()[0] in ch.split())
            return -1 if other and not named else len(nm) + (100 if named else 0)
        sc = sorted(((score(r), r["District ID"]) for r in rs), reverse=True)
        if sc[0][0] < 0: continue
        if len(sc) > 1 and sc[0][0] == sc[1][0]: continue
        own[url] = sc[0][1]
    return own


def write(cc, key, rows, feats):
    meetings(cc, "")
    own = owners(cc, rows)
    for r in rows:
        n, url, keep, kind = meetings(cc, r["District ID"])
        if url and own.get(url) != r["District ID"]: n, url, keep, kind = 0, "", [], ""
        latest, years = date_summary(keep) if n else ("", "")
        r.update({"Available Board Meetings": n, "Meetings type": kind, "Meetings source": url, "Latest meeting": latest, "Meetings by year": years})
    cols = ["District", "Region", "Locale", "Available Board Meetings", "Meetings type", "Meetings source", "Latest meeting", "Meetings by year",
            "Population", "Poverty rate (all ages)", "Multidimensional poverty (all ages)", "Poverty note", "Enrollment", "Enrollment year",
            "Public school enrollment", "School system", "People per km² (estimated)", "District ID"]
    extra = [c for c in ("Extreme poverty (all ages)", "Poverty by year", "Children 6–17", "Bolsa Família families", "Households") if any(r.get(c) not in (None, "") for r in rows)]
    cols = cols[:cols.index("Poverty note") + 1] + [c for c in extra if c != "Children 6–17"] + cols[cols.index("Poverty note") + 1:-1] + [c for c in extra if c == "Children 6–17"] + cols[-1:]
    rows.sort(key=lambda r: r["District"])
    with open(os.path.join(DOCS, f"{key}.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=cols, restval="", extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", f"{key}.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(cc, len(rows), "rows; poverty", sum(1 for r in rows if r["Poverty rate (all ages)"]), "; enrollment", sum(1 for r in rows if r["Enrollment"]),
          "; meetings", sum(1 for r in rows if r["Available Board Meetings"]), "; no border", [r["District"] for r in rows if not r.get("_geo")][:10])


def loc(d):
    return "Urban" if d >= 2000 else "Suburban" if d >= 500 else "Mixed" if d >= 100 else "Rural"


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def chile():
    sheet = lambda f: [r for r in openpyxl.load_workbook(os.path.join(IN, "chile", f), read_only=True).worksheets[0].iter_rows(values_only=True)
                       if r and isinstance(r[0], (int, float))]
    inc = {str(int(r[0])).zfill(5): r for r in sheet("sae_ingresos_2024.xlsx")}
    mul = {str(int(r[0])).zfill(5): r for r in sheet("sae_multidimensional_2024.xlsx")}
    enr = json.load(open(os.path.join(IN, "chile", "enrolment_by_comuna_2026.json")))
    geo = json.load(open(os.path.join(IN, "chile", "gb_CHL_ADM3.geojson"), encoding="utf-8"))
    by_name = {}
    for f in geo["features"]:
        n = norm(f["properties"]["shapeName"]); by_name[ALIAS["CL"].get(n, n)] = f
    rows, feats = [], []
    for code, r in inc.items():
        e = enr.get(str(int(code))) or enr.get(code) or {}
        dep = e.get("by_dependency", {})
        public = sum(v for k, v in dep.items() if k in ("1", "2", "5", "6"))   # COD_DEPE: 1-2 municipal, 5 delegated, 6 SLEP
        slep = dep.get("6", 0); muni = dep.get("1", 0) + dep.get("2", 0)
        f = by_name.get(ALIAS["CL"].get(norm(r[2]), norm(r[2])))
        area = area_km2(f["geometry"]) if f else 0
        did = f"CL-{code}"
        row = {"District": r[2], "Region": r[1], "Population": int(r[3]), "Poverty rate (all ages)": f"{100 * r[5]:.2f}%",
               "Multidimensional poverty (all ages)": f"{100 * mul[code][5]:.2f}%" if code in mul else "",
               "Poverty note": f"All ages, 2024 small-area estimate ({r[9]}); no child rate is published by comuna",
               "Enrollment": e.get("total", ""), "Enrollment year": "2026" if e else "", "Public school enrollment": public or "",
               "School system": "Local Public Education Service (SLEP)" if slep > muni else "Municipality (DAEM or corporation)" if muni else "",
               "Locale": loc(int(r[3]) / area) if area else "", "People per km² (estimated)": round(int(r[3]) / area) if area else "",
               "District ID": did, "_geo": bool(f)}
        rows.append(row)
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": r[2]}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("CL", "chile", rows, feats)


def colombia():
    ws = openpyxl.load_workbook(os.path.join(IN, "colombia", "ipm_municipal_2018.xlsx"), read_only=True)["2_IPM Mpio y Dpt"]
    ipm = {str(r[0]): r for r in ws.iter_rows(values_only=True) if r and r[0] and len(str(r[0])) == 5 and str(r[0]).isdigit()}
    men = {r["c_digo_municipio"].zfill(5): r for r in json.load(open(os.path.join(IN, "colombia", "men_estadisticas_municipio_2024.json"), encoding="utf-8"))}
    dept_name = {r["c_digo_departamento"].zfill(2): r["departamento"] for r in men.values()}
    adm1 = json.load(open(os.path.join(IN, "colombia", "gb_COL_ADM1.geojson"), encoding="utf-8"))["features"]
    dcode = {}
    for f in adm1:
        n = norm(f["properties"]["shapeName"])
        code = next((c for c, nm in dept_name.items() if norm(nm) == n or norm(nm)[:8] == n[:8] or (c == "11" and "bogota" in n)), None)
        dcode[id(f)] = code
    geo = json.load(open(os.path.join(IN, "colombia", "gb_COL_ADM2.geojson"), encoding="utf-8"))
    keyed = {}
    for f in geo["features"]:
        c = centroid(f["geometry"])
        d = next((dcode[id(a)] for a in adm1 if pip(c, a["geometry"])), None)
        n = norm(f["properties"]["shapeName"]); n = ALIAS["CO"].get(n, n)
        keyed.setdefault((d, n), f)
    rows, feats = [], []
    # Exact matches (department and name) first, so a fuzzy match never takes another municipality's border.
    exact = {code: keyed.get((code[:2], ALIAS["CO"].get(norm(r[1]), norm(r[1])))) for code, r in ipm.items()}
    used = {id(f) for f in exact.values() if f}
    for code, r in ipm.items():
        m = men.get(code, {})
        nm = str(r[1]).title().replace(" De ", " de ").replace(" Del ", " del ").replace(" La ", " la ").replace(" El ", " el ")
        n = norm(r[1]); n = ALIAS["CO"].get(n, n)
        f = exact[code] or next((g for (d, k), g in keyed.items() if id(g) not in used and d == code[:2] and (k.startswith(n) or n.startswith(k)) and min(len(k), len(n)) >= 5), None)
        if not f:   # a border near a coast or department edge can fall outside its simplified department: use the name if it's unique
            same = [g for (d, k), g in keyed.items() if k == n and id(g) not in used]
            f = same[0] if len(same) == 1 else None
        if f and not exact[code]: used.add(id(f))
        pop = float(m.get("poblaci_n_5_16") or 0); rate = float(m.get("tasa_matriculaci_n_5_16") or 0)
        area = area_km2(f["geometry"]) if f else 0
        dens = pop / 0.19 / area if area and pop else 0
        did = f"CO-{code}"
        rows.append({"District": nm, "Region": dept_name.get(code[:2], ""), "Poverty rate (all ages)": f"{float(r[2]):.2f}%" if isinstance(r[2], (int, float)) else "",
                     "Poverty note": "Multidimensional poverty, all ages, 2018 census (DANE); no child or income rate is published by municipality",
                     "Enrollment": round(pop * rate / 100) if pop and rate else "", "Enrollment year": "2024 (estimated: children 5–16 × net enrollment rate)" if pop and rate else "",
                     "School system": m.get("etc", ""), "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "",
                     "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": nm}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("CO", "colombia", rows, feats)


def adm_match(cc, rows, adm2, adm1, state_of_adm1):
    """Borders for rows ({"name", "state", "id"}): exact (state, name) first, then a prefix match within the
    state, then a name unique in the country; a border is never used twice. Returns {id: feature}."""
    full = lambda s: re.sub(r"\bDr\.\s*", "Doctor ", re.sub(r"\bGral\.\s*", "General ", str(s)))   # Nuevo León's abbreviations
    keyed = {}
    for f in adm2:
        c = centroid(f["geometry"])
        st = next((state_of_adm1[id(a)] for a in adm1 if pip(c, a["geometry"])), None)
        n = norm(full(f["properties"]["shapeName"])); n = ALIAS.get(cc, {}).get(n, n)
        keyed.setdefault((st, n), f)
    key = lambda r: ALIAS.get(cc, {}).get(norm(full(r["name"])), norm(full(r["name"])))
    bare = lambda k: re.sub(r"^(el|la|los|las|o|a|os|as)(?=[a-z]{4})", "", k)   # "El Carmen" / "Carmen"
    out = {r["id"]: keyed.get((r["state"], key(r))) for r in rows}
    used = {id(f) for f in out.values() if f}
    for r in rows:
        if out[r["id"]]: continue
        n = key(r)
        f = next((g for (d, k), g in keyed.items() if id(g) not in used and d == r["state"] and (k.startswith(n) or n.startswith(k)) and min(len(k), len(n)) >= 5), None)
        f = f or next((g for (d, k), g in keyed.items() if id(g) not in used and d == r["state"] and (bare(k) == bare(n) or (len(n) >= 12 and n in k))), None)
        if not f:
            same = [g for (d, k), g in keyed.items() if k == n and id(g) not in used]
            f = same[0] if len(same) == 1 else None
        if f: used.add(id(f)); out[r["id"]] = f
    return out


MX_ISO = {"AGU": "01", "BCN": "02", "BCS": "03", "CAM": "04", "COA": "05", "COL": "06", "CHP": "07", "CHH": "08", "CMX": "09", "DIF": "09", "DUR": "10",
          "GUA": "11", "GRO": "12", "HID": "13", "JAL": "14", "MEX": "15", "MIC": "16", "MOR": "17", "NAY": "18", "NLE": "19", "OAX": "20", "PUE": "21",
          "QUE": "22", "ROO": "23", "SLP": "24", "SIN": "25", "SON": "26", "TAB": "27", "TAM": "28", "TLA": "29", "VER": "30", "YUC": "31", "ZAC": "32"}
MX_STATE = {"México": "Estado de México", "Coahuila de Zaragoza": "Coahuila", "Michoacán de Ocampo": "Michoacán", "Veracruz de Ignacio de la Llave": "Veracruz"}


def mexico():
    """2,469 municipalities. Schools are run by each state's education authority (the federal SEP pays for most
    basic education), not by municipalities; town councils (cabildos) stand in for meetings."""
    ws = openpyxl.load_workbook(os.path.join(IN, "mexico", "coneval_pobreza_municipal_2020.xlsx"), read_only=True)["Concentrado municipal"]
    con = {str(r[3]): r for r in ws.iter_rows(values_only=True) if r and r[3] and re.fullmatch(r"\d{5}", str(r[3]))}
    num = lambda v: int(v) if str(v).strip().isdigit() else None
    it = {}
    for r in csv.DictReader(open(os.path.join(IN, "mexico", "inegi_iter_2020_municipal.csv"), encoding="utf-8")):
        it[r["ENTIDAD"] + r["MUN"]] = r
    adm1 = json.load(open(os.path.join(IN, "mexico", "gb_MEX_ADM1.geojson"), encoding="utf-8"))["features"]
    st = {id(f): MX_ISO.get(f["properties"]["shapeISO"].split("-")[-1]) for f in adm1}
    adm2 = json.load(open(os.path.join(IN, "mexico", "gb_MEX_ADM2.geojson"), encoding="utf-8"))["features"]
    geo = adm_match("MX", [{"name": r[4], "state": c[:2], "id": c} for c, r in con.items()], adm2, adm1, st)
    rows, feats = [], []
    for code, r in con.items():
        i = it.get(code, {})
        a, b, c6, d, e = (num(i.get(k)) for k in ("P_6A11", "P6A11_NOA", "P_12A14", "P12A14NOA", "P15A17A"))
        enr = (a - b) + (c6 - d) + e if None not in (a, b, c6, d, e) else ""
        kids = sum(x for x in (num(i.get("P_6A11")), num(i.get("P_12A14")), num(i.get("P_15A17"))) if x) or ""
        pop = num(i.get("POBTOT")) or (int(r[7]) if r[7] else 0)
        f = geo.get(code); area = area_km2(f["geometry"]) if f else 0
        dens = pop / area if area and pop else 0
        pct = lambda v: f"{float(v):.2f}%" if isinstance(v, (int, float)) else ""
        did = f"MX-{code}"
        rows.append({"District": str(r[4]), "Region": MX_STATE.get(str(r[2]), str(r[2])), "Population": pop,
                     "Poverty rate (all ages)": pct(r[10]), "Extreme poverty (all ages)": pct(r[19]),
                     "Poverty by year": "; ".join(f"{y}:{float(v):.1f}" for y, v in zip((2010, 2015, 2020), r[8:11]) if isinstance(v, (int, float))),
                     "Poverty note": "Multidimensional poverty (income below the poverty line and at least one social deprivation), all ages, 2020 (CONEVAL); no child rate is published by municipality",
                     "Enrollment": enr, "Enrollment year": "2020 (estimated: census count of children 6–17 attending school)" if enr != "" else "",
                     "Children 6–17": kids, "School system": "State education authority",
                     "Locale": loc(dens) if dens else "", "People per km² (estimated)": round(dens) if dens else "", "District ID": did, "_geo": bool(f)})
        if f: feats.append({"type": "Feature", "properties": {"id": did, "NAME": str(r[4])}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    write("MX", "mexico", rows, feats)


if __name__ == "__main__":
    which = sys.argv[1:] or ["chile", "colombia", "mexico"]
    for w in which: globals()[w]()
