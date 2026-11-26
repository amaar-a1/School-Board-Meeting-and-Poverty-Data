"""Peru's pupils by district for earlier school censuses, for change over time: data-prep/inputs/peru/
pe_alumnos_history.json, {year: {"pupils": {ubigeo: n}, "pupils_public": {ubigeo: n}}}.

MINEDU, ESCALE, Censo Educativo YYYY, 00_Padron.zip (escale.minedu.gob.pe/documents/inicio/Bases de datos/A. Censo
Educativo/YYYY/; downloaded by hand): Padron.dbf, one row per school and programme, with TALUMNO (its pupils in that
census; TALUYY in older files, e.g. TALU22), CODGEO (the district's INEI ubigeo) and GESTION (1 public, directly run; 2 public, privately run, as the site
counts public; 3 private). Summed by district, as the site's 2025 figure is (every school and programme, all levels).
Usage: python3 data-prep/prep_peru_history.py YEAR 00_Padron.zip [YEAR 00_Padron.zip ...]
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


def main(args):
    out = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    for y, p in zip(args[::2], args[1::2]):
        out[y] = one(p)
        print(y, len(out[y]["pupils"]), "districts;", sum(out[y]["pupils"].values()), "pupils")
    json.dump(out, open(OUT, "w", encoding="utf-8"), separators=(",", ":"), sort_keys=True)


if __name__ == "__main__":
    main(sys.argv[1:])
