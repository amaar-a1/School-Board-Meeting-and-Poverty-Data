"""Turns the Paraguay downloads (made on GitHub's runner, fetch rounds 31-32) into the inputs build_latam.paraguay() reads
(data-prep/inputs/paraguay/).

- Poverty: Instituto Nacional de Estadística (INE), Mapa de pobreza monetaria distrital 2022 (small-area estimates from
  the 2022 census and the household survey, EPH): the share of people below the poverty line in each district, all
  ages, with its 95% range (Cuadro-Incidencia-Pobreza_Monetaria_Distrital.xlsx, Cuadro 1).
- Population: INE, Estimaciones y proyecciones de la población distrital, revisión 2025: mid-2025 population.
- Borders: geoBoundaries (gbOpen) PRY ADM2, simplified; each district's department from the ADM1 borders it lies in.
  Districts created since the borders were drawn have no border of their own and stay inside the district they came from.
- Children (for the enrollment estimate, data-prep/estimate_enrollment.py): WorldPop's 2025 age structures (R2025A,
  1 km), summed over each border by the runner (pry_ages_2025.json). The Ministry of Education's open data site doesn't
  answer GitHub's servers.
Then, after build_latam.py, run data-prep/estimate_enrollment.py paraguay.csv and data-prep/simplify_borders.sh.
Usage: python3 data-prep/prep_paraguay.py RAWDIR
"""
import difflib, json, os, re, sys, unicodedata
import openpyxl
from shapely.geometry import mapping, shape
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "paraguay")
key = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())
DEPTS = {key(d): d for d in ["Asunción", "Concepción", "San Pedro", "Cordillera", "Guairá", "Caaguazú", "Caazapá", "Itapúa", "Misiones", "Paraguarí",
                             "Alto Paraná", "Central", "Ñeembucú", "Amambay", "Canindeyú", "Presidente Hayes", "Boquerón", "Alto Paraguay"]}
ABBR = [(r"\bgral\b\.?", "general"), (r"\bdr\b\.?", "doctor"), (r"\bmcal\b\.?", "mariscal"), (r"\btte\b\.?", "teniente"),
        (r"\bsgto\b\.?", "sargento"), (r"\b1\s*(ro)?\b", "primero"), (r"\bdel?\b", ""), (r"\bla\b|\blas\b|\blos\b", "")]


def loose(s):
    """A name for fuzzy matching: abbreviations spelled out, articles dropped, Guaraní y/i and b/v and c/k folded."""
    t = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    for a, b in ABBR: t = re.sub(a, b, t)
    t = re.sub(r"[^a-z]", "", t)
    return t.replace("y", "i").replace("v", "b").replace("k", "c").replace("qu", "c")


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def cells(r):
    return [c for c in r if c is not None and str(c).strip() != ""]


def poverty(path):
    """{(department key, district key): (name, rate %, low %, high %)}, in the table's order (a department's heading, then its districts)."""
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
    out, dept = {}, None
    for r in ws.iter_rows(values_only=True):
        c = cells(r)
        if not c or not isinstance(c[0], str): continue
        name = c[0].strip()
        if len(c) == 1 and key(name) in DEPTS: dept = key(name); continue
        if len(c) >= 4 and isinstance(c[1], (int, float)):
            d = dept or key(name)   # Asunción is its own department
            out[(d, key(name))] = (name, round(100 * c[1], 1), round(100 * c[2], 1), round(100 * c[3], 1))
    return out


def projections(path, year=2025):
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    hdr = next(i for i, r in enumerate(rows) if 2000 in r and 2035 in r)
    col = list(rows[hdr]).index(year)
    out, dept = {}, None
    for r in rows[hdr + 1:]:
        name = next((c for c in r[:col] if isinstance(c, str) and c.strip()), None)
        if not name or not isinstance(r[col], (int, float)): continue
        name = name.strip()
        if name.startswith("Dpto.") or name == "Total País": dept = key(name.replace("Dpto.", "")); continue
        out[(dept or key(name), key(name))] = int(r[col])
    return out


def main(raw):
    pov = poverty(os.path.join(raw, "py_pov_dist.xlsx"))
    pop = projections(os.path.join(raw, "py_proj_dist.xlsx"))
    adm1 = [(DEPTS.get(key(f["properties"]["shapeName"]), f["properties"]["shapeName"].title()), shape(f["geometry"]).buffer(0))
            for f in json.load(open(os.path.join(raw, "py_gb_ADM1.geojson"), encoding="utf-8"))["features"]]
    gb = json.load(open(os.path.join(raw, "py_gb_ADM2.geojson"), encoding="utf-8"))["features"]
    ages = json.load(open(os.path.join(raw, "pry_ages_2025.json"), encoding="utf-8"))["districts"] if os.path.exists(os.path.join(raw, "pry_ages_2025.json")) else {}
    data, feats, nofig, taken = {}, [], [], set()
    pop_by_name, pop_loose = {}, {}
    for (d, n), v in pop.items(): pop_by_name.setdefault(n, []).append(v)
    for (d, n), v in pop.items(): pop_loose[(d, loose(n))] = v
    for f in gb:
        g = shape(f["geometry"]).buffer(0)
        pt = g.representative_point()
        dname = next((n for n, pg in adm1 if pg.contains(pt)), None) or min(adm1, key=lambda p: p[1].distance(pt))[0]
        dk, nk = key(dname), key(f["properties"]["shapeName"])
        p = pov.get((dk, nk))
        if not p:   # the same district spelled differently: the closest name in its department
            cands = {loose(v[0]): k for k, v in pov.items() if k[0] == dk and k not in taken}
            m = difflib.get_close_matches(loose(f["properties"]["shapeName"]), list(cands), n=1, cutoff=0.6)
            m = m or [c for c in cands if loose(f["properties"]["shapeName"]) in c or c in loose(f["properties"]["shapeName"])][:1]
            if m: nk = cands[m[0]][1]; p = pov[(dk, nk)]; print("matched", f["properties"]["shapeName"], "->", p[0])
        if not p: nofig.append((dname, f["properties"]["shapeName"])); continue
        taken.add((dk, nk))
        a = ages.get(f["properties"]["shapeID"], {})
        prev = next((k for k, v in data.items() if (key(v["dept"]), key(v["name"])) == (dk, key(p[0]))), None)
        if prev:   # the same district in more pieces (geoBoundaries has slivers of San Juan del Paraná): one border, counts added
            x = data[prev]
            for gr in ("05", "10", "15"):
                if x["ages"] is not None: x["ages"][gr] += round(a.get("f" + gr, 0) + a.get("m" + gr, 0))
            ft = next(ft for ft in feats if ft["properties"]["id"] == prev)
            ft["geometry"] = mapping(unary_union([shape(ft["geometry"]).buffer(0), g]))
            ft["geometry"] = {"type": ft["geometry"]["type"], "coordinates": rnd(json.loads(json.dumps(ft["geometry"]["coordinates"])))}
            print("merged another piece of", p[0]); continue
        did = "PRY-" + f["properties"]["shapeID"][-8:]
        data[did] = {"name": p[0], "dept": dname, "pov": p[1], "low": p[2], "high": p[3], "pop": pop.get((dk, nk)) or (pop_by_name[nk][0] if len(pop_by_name.get(nk, [])) == 1 else None) or pop_loose.get((dk, loose(p[0]))) or pop_loose.get((dk, loose(f["properties"]["shapeName"]))),
                     "ages": {gr: round(a.get("f" + gr, 0) + a.get("m" + gr, 0)) for gr in ("05", "10", "15")} if a else None}
        feats.append({"type": "Feature", "properties": {"id": did, "NAME": p[0]},
                      "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    used = {(key(v["dept"]), key(v["name"])) for v in data.values()}
    used |= {k for k in pov if (k[0], key(pov[k][0])) in used}
    print("borders with no poverty figure:", nofig)
    print("poverty districts with no border (newer districts, inside their parent's):", sorted(v[0] for k, v in pov.items() if k not in used))
    print("no population:", [v["name"] for v in data.values() if not v["pop"]])
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "pry_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "pry_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"))
    print(len(data), "districts of", len(pov), "; population", sum(v["pop"] or 0 for v in data.values()))


if __name__ == "__main__":
    main(*sys.argv[1:])
