# Temporary: the four Spain ADRH tables (relative poverty by age) too big for the JSON API, as INE's CSV files.
import csv, io, json, os, time, traceback, urllib.request
OUT = "fetch/out/es_big"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=900):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
        except Exception as e:
            err = e; time.sleep(30)
    raise err
res = []
for tid in (30830, 30902, 31103, 31256):
    try:
        b = get(f"https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/{tid}.csv?nocab=1")
        t = b.decode("utf-8-sig", errors="replace")
        rd = csv.reader(io.StringIO(t), delimiter="\t" if t.count("\t") > t.count(";") else ";")
        head = next(rd); n = 0; keep = 0
        for r in rd:
            n += 1
            d = dict(zip(head, r))
            if n < 3: log.write(f"{tid} row {d}\n")
            vals = list(d.values())
            if any("Menos de 18" in v for v in vals) and any("60% de la mediana" in v for v in vals):
                res.append({"table": tid, **d}); keep += 1
        log.write(f"{tid}: {len(b)} bytes, header {head}, {n} rows, kept {keep}\n")
    except Exception:
        log.write(f"{tid}: ERR {traceback.format_exc()[-600:]}\n")
    log.flush()
# keep municipal totals only (no district or section), and only the sex total
mun = [r for r in res if not (r.get("Distritos") or "").strip() and not (r.get("Secciones") or "").strip()]
json.dump(mun or res[:50000], open(f"{OUT}/es_big_under18.json", "w"), ensure_ascii=False)
log.write(f"total kept {len(res)}, municipal {len(mun)}\n"); log.close()
