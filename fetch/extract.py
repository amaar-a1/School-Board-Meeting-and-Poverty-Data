# Temporary: NCES Private School Survey (school-level, with coordinates) for private pupils by US district.
import io, json, os, urllib.request, zipfile, csv
OUT = "fetch/out/pss1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
for y in ("2021", "2019", "2017"):
    try:
        d = json.loads(get(f"https://educationdata.urban.org/api/v1/schools/pss/directory/{y}/?page=1", 120))
        log.write(f"urban pss {y}: count {d.get('count')} keys {list((d.get('results') or [{}])[0].keys())[:40]}\n")
    except Exception as e: log.write(f"urban pss {y} ERR {str(e)[:120]}\n")
for name in ("pss2122_pu_csv.zip", "pss1920_pu_csv.zip"):
    try:
        b = get("https://nces.ed.gov/surveys/pss/zip/" + name)
        z = zipfile.ZipFile(io.BytesIO(b)); log.write(f"{name}: {len(b)} {z.namelist()}\n")
        f = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        rows = list(csv.DictReader(io.TextIOWrapper(z.open(f), encoding="latin-1")))
        cols = list(rows[0].keys()); log.write(f"cols {cols}\n")
        keep = [c for c in cols if c.upper() in ("PPIN", "PINST", "PSTABB", "PCNTNM", "LATITUDE22", "LONGITUDE22", "LATITUDE20", "LONGITUDE20", "NUMSTUDS", "P305", "PZIP", "PCITY", "LEVEL", "TYPOLOGY", "P_INDIAN", "PFNLWT")]
        log.write(f"keep {keep} rows {len(rows)}\n")
        json.dump({"file": name, "cols": keep, "rows": [[r[c] for c in keep] for r in rows]}, open(f"{OUT}/{name[:-8]}.json", "w"))
        break
    except Exception as e: log.write(f"{name} ERR {str(e)[:200]}\n")
log.close()
