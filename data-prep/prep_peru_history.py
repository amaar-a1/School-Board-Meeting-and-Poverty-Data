"""Peru's pupils by district for earlier school censuses, for change over time: data-prep/inputs/peru/
pe_alumnos_history.json, {year: {"pupils": {ubigeo: n}, "pupils_public": {ubigeo: n}}}.

MINEDU, ESCALE, Censo Educativo YYYY, 00_Padron.zip (escale.minedu.gob.pe/documents/inicio/Bases de datos/A. Censo
Educativo/YYYY/; downloaded by hand): Padron.dbf, one row per school and programme, with TALUMNO (its pupils in that
census; TALUYY in older files, e.g. TALU22), CODGEO (the district's INEI ubigeo) and GESTION (1 public, directly run; 2 public, privately run, as the site
counts public; 3 private). Summed by district, as the site's 2025 figure is (every school and programme, all levels).
The 2016–2021 Padron.dbf files have no pupil count, so their pupils come from M01_edades.zip (2021) or
01_/02_/03_Matricula_01.zip (2017–2020) or Matricula.dbf.zip (2016, every table of the form; see OLD_TABLES) of the same folder (enrollment by age,
cuadro C201, or C202/C206 for the few programmes counted there; ages and columns added up per school, the largest of a
school's tables taken, or their sum for cédula 7A whose two tables count different pupils), with the school's district
and management from that year's Padron.dbf. District by district the median is about 98% of the next year's
count (national totals 8.66M in 2016, 8.72M in 2017, 8.79M in 2018, 9.00M in 2019, 9.05M in 2020 and 9.10M in 2021, against 9.42M in 2022); Lima's Cercado is the main outlier
(130k in 2021, 200k in 2022), and San Isidro's 2019 figure includes
TELESUP's 25k students, a technical institute that closed (counts cover every school in the padrón, institutes included).
Usage: python3 data-prep/prep_peru_history.py YEAR 00_Padron.zip [YEAR 00_Padron.zip ...]
       python3 data-prep/prep_peru_history.py --edades 2021 Padron.zip M01_edades.zip
       python3 data-prep/prep_peru_history.py --edades 2020 01_Padron.zip 02_Matricula_01.zip   (2016–2019 likewise)
"""
import io, json, os, sys, tempfile, zipfile
from dbfread import DBF

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "peru", "pe_alumnos_history.json")


def one(path):
    tmp = tempfile.mkdtemp()
    z = zipfile.ZipFile(path)
    name = next(n for n in z.namelist() if n.lower().endswith("padron.dbf"))
    z.extract(name, tmp)
    pupils, public = {}, {}
    t = DBF(os.path.join(tmp, name), encoding="latin-1", load=False)
    col = next(c for c in t.field_names if c == "TALUMNO" or c.startswith("TALU"))   # TALUMNO, or TALU22 in 2022's file
    for r in t:
        n = r.get(col) or 0
        if not n or not r.get("CODGEO"): continue
        c = str(r["CODGEO"]).zfill(6)
        pupils[c] = pupils.get(c, 0) + int(n)
        if str(r.get("GESTION")) in ("1", "2"): public[c] = public.get(c, 0) + int(n)
    return {"pupils": pupils, "pupils_public": public}


# Up to 2016 a single Matricula.dbf holds every table of the census form, numbered by cédula ("01", "4A", ...). These are
# the tables that count each school's pupils once, chosen by matching schools against 2017's counts.
OLD_TABLES = {"01": ("201",), "02": ("201",), "03": ("201",), "05": ("201",), "06": ("201",), "07": ("209",),
              "08": ("201", "203"), "09": ("201",), "4A": ("209",), "4I": ("208",)}


def edades(year, padron, m01):
    tmp = tempfile.mkdtemp()
    for zp in (padron, m01):
        z = zipfile.ZipFile(zp); z.extractall(tmp)
    find = lambda pat: next(os.path.join(dp, f) for dp, _, fs in os.walk(tmp) for f in fs if f.lower() == pat)
    where = {(r["COD_MOD"], r["ANEXO"]): (str(r["CODGEO"]).zfill(6), str(r.get("GESTION"))) for r in DBF(find("padron.dbf"), encoding="latin-1", load=False)}
    per, ced = {}, {}
    m = next(os.path.join(dp, f) for dp, _, fs in os.walk(tmp) for f in fs if f.lower() in ("m01_edades.dbf", "matricula_01.dbf", "matricula.dbf"))
    t = DBF(m, encoding="latin-1", load=False); d = [f for f in t.field_names if f[0] == "D" and f[1:].isdigit()]
    for r in t:
        k = (r["COD_MOD"], r["ANEXO"]); n = sum(r[f] or 0 for f in d)
        if r["NROCED"] in OLD_TABLES and r["CUADRO"] not in OLD_TABLES[r["NROCED"]]: continue
        per.setdefault(k, {}); per[k][r["CUADRO"]] = per[k].get(r["CUADRO"], 0) + n; ced[k] = r["NROCED"]
    pupils, public = {}, {}
    for k, t in per.items():
        n = int(sum(t.values()) if ced[k] in ("7A", "08") else max(t.values()))
        if not n or k not in where: continue
        c, g = where[k]
        pupils[c] = pupils.get(c, 0) + n
        if g in ("1", "2"): public[c] = public.get(c, 0) + n
    out = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    out[year] = {"pupils": pupils, "pupils_public": public}
    json.dump(out, open(OUT, "w", encoding="utf-8"), separators=(",", ":"), sort_keys=True)
    print(year, len(pupils), "districts;", sum(pupils.values()), "pupils;", sum(1 for k in per if k not in where), "schools not in the padrón")


def main(args):
    out = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    for y, p in zip(args[::2], args[1::2]):
        out[y] = one(p)
        print(y, len(out[y]["pupils"]), "districts;", sum(out[y]["pupils"].values()), "pupils")
    json.dump(out, open(OUT, "w", encoding="utf-8"), separators=(",", ":"), sort_keys=True)


if __name__ == "__main__" and sys.argv[1] == "--edades":
    edades(*sys.argv[2:5])
elif __name__ == "__main__":
    main(sys.argv[1:])
