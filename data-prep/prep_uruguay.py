"""Turns the Uruguay downloads (made on GitHub's runner) into the small inputs build_latam.uruguay() reads
(data-prep/inputs/uruguay/).

- ury_geo.geojson: the 19 departments, from geoBoundaries gbOpen URY ADM1 (simplified).
- ury_data.json, per department:
  pop: INE, population projected to 30 June 2025 (Anuario Estadístico Nacional 2025, table 2.2.4);
  pupils, public: INE, Anuario Estadístico Nacional 2025, 2024: common primary school pupils (table 3.1.3), lower
    secondary (Educación Media Básica, 3.1.6) and upper secondary (Educación Media Superior, 3.1.10), general and
    vocational, in public and private schools (forma de administración);
  poverty (stand-in): Tarjeta Uruguay Social cards in 2024 (MIDES, in INE's yearbook 2025, table 3.9.3, saved as
    uy_3.9.3.xlsx) per 100 residents; band: INE, Estimación de la pobreza por el método del ingreso, año 2025, map 1
    (households below the poverty line by department, shown only in three bands);
  meetings: the Junta Departamental's YouTube channel (fetch/nyt.py, UY).
Then run data-prep/simplify_borders.sh (the map needs lighter borders than geoBoundaries' full detail).
Usage: python3 data-prep/prep_uruguay.py RAWDIR [RAWDIR ...] GEODIR
"""
import glob, json, os, re, sys, unicodedata
import xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "uruguay")
DEPT = ["Montevideo", "Artigas", "Canelones", "Cerro Largo", "Colonia", "Durazno", "Flores", "Florida", "Lavalleja", "Maldonado", "Paysandú",
        "Río Negro", "Rivera", "Rocha", "Salto", "San José", "Soriano", "Tacuarembó", "Treinta y Tres"]
key = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())


def find(dirs, name):
    return sorted(f for d in dirs for f in glob.glob(os.path.join(d, "**", name), recursive=True))[-1]


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


num = lambda v: float(v) if isinstance(v, float) else 0.0


def year_block(path, year):
    """Rows of one year's block in an INE yearbook table: {department: row}."""
    sh = xlrd.open_workbook(path).sheet_by_index(0)
    out, on = {}, False
    for r in range(sh.nrows):
        v = sh.row_values(r)
        if isinstance(v[0], float) and int(v[0]) in range(2000, 2100): on = int(v[0]) == year; continue
        if on and key(v[0]) in {key(d) for d in DEPT}:
            out[next(d for d in DEPT if key(d) == key(v[0]))] = v
    assert len(out) == 19, (path, year, len(out))
    return out


def main(*args):
    *dirs, geo = args
    os.makedirs(OUT, exist_ok=True)
    yr = 2024
    pri = year_block(find(dirs, "uy_3.1.3.xls"), yr)     # Pública: establecimientos, maestros, alumnos; Privada: same
    mb = year_block(find(dirs, "uy_3.1.6.xls"), yr)      # General pub H, M, priv H, M; Vocacional pub H, M, priv H, M
    ms = year_block(find(dirs, "uy_3.1.10.xls"), yr)
    sh = xlrd.open_workbook(find(dirs, "uy_2.2.4.xls")).sheet_by_index(0)
    hdr = sh.row_values(2); col = hdr.index(2025.0)
    pop = {next(d for d in DEPT if key(d) == key(sh.cell_value(r, 0))): sh.cell_value(r, col) for r in range(sh.nrows) if key(sh.cell_value(r, 0)) in {key(d) for d in DEPT}}
    data = {}
    for i, d in enumerate(DEPT):
        p, b, s = pri[d], mb[d], ms[d]
        vals = lambda row: [num(x) for x in row[1:]]
        pv, bv, sv = vals(p), vals(b), vals(s)
        public = pv[2] + bv[0] + bv[1] + bv[4] + bv[5] + sv[0] + sv[1] + sv[4] + sv[5]
        private = pv[5] + bv[2] + bv[3] + bv[6] + bv[7] + sv[2] + sv[3] + sv[6] + sv[7]
        data[d] = {"code": f"{i + 1:02d}", "pop": round(pop[d]), "pupils": round(public + private), "public": round(public), "pupils_year": yr}
    # Poverty stand-in: INE publishes poverty by department only as a banded map, so the figure is Tarjeta Uruguay Social
    # cards (MIDES' food card for the most vulnerable households; "doble" for the most vulnerable of them) in 2024
    # (INE yearbook 2025, table 3.9.3, first sheet; its 2023 column has Río Negro and Rivera swapped, 2024 matches the
    # series) per 100 residents, with the department's band in INE's 2025 map of households below the poverty line.
    import openpyxl
    ws = openpyxl.load_workbook(os.path.join(OUT, "uy_3.9.3.xlsx"), read_only=True)["3.9.3"]
    tus = {}
    for r in ws.iter_rows(values_only=True):
        if r[0] and key(r[0]) in {key(d) for d in DEPT}:
            tus[next(d for d in DEPT if key(d) == key(r[0]))] = (int(r[6]), int(r[7]))
    assert len(tus) == 19
    BAND = {"Artigas": "15.0–23.9%", "Salto": "15.0–23.9%", "Paysandú": "15.0–23.9%", "Rivera": "15.0–23.9%", "Cerro Largo": "15.0–23.9%",
            "Treinta y Tres": "15.0–23.9%", "Colonia": "under 9%", "San José": "under 9%", "Flores": "under 9%", "Maldonado": "under 9%"}
    for d in DEPT:
        s_, dbl = tus[d]
        data[d].update(tus=s_ + dbl, tus_double=dbl, poverty=round(100 * (s_ + dbl) / data[d]["pop"], 2),
                       band=BAND.get(d, "9.0–14.9%"))
    g = {key(f["properties"]["shapeName"]): f for f in json.load(open(os.path.join(geo, "geoBoundaries-URY-ADM1_simplified.geojson"), encoding="utf-8"))["features"]}
    feats = [{"type": "Feature", "properties": {"id": "URY-" + data[d]["code"], "NAME": d}, "geometry": {"type": g[key(d)]["geometry"]["type"], "coordinates": rnd(g[key(d)]["geometry"]["coordinates"])}} for d in DEPT]
    json.dump(data, open(os.path.join(OUT, "ury_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "ury_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    for d, x in data.items(): print(d, x["pop"], x["pupils"], round(100 * x["public"] / x["pupils"], 1), x.get("poverty"))
    print(sum(x["pupils"] for x in data.values()), sum(x["public"] for x in data.values()))


if __name__ == "__main__":
    main(*sys.argv[1:])
