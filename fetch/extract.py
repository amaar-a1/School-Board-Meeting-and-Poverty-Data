# Temporary: Belgium's integration income (RIS / leefloon) by municipality, from stat.mi-is.be's map data.
import json, os, time, traceback, urllib.request
OUT = "fetch/out/bp6"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "application/json, */*", "X-Requested-With": "XMLHttpRequest"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    err = None
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
        except Exception as e: err = e; time.sleep(30 * (a + 1))
    raise err
for slug in ("ris_cities", "gpmis_leefloon_ratio"):
    for per in ("202501-202512", "202401-202412"):
        for lang in ("fr", "nl"):
            u = f"https://stat.mi-is.be/{lang}/export/map/{slug}/{per}.json"
            try:
                b = get(u); open(f"{OUT}/mi_{slug}_{per}.json", "wb").write(b); log.write(f"{u}: {len(b)} {b[:300]!r}\n"); break
            except Exception as e: log.write(f"{u}: ERR {str(e)[:100]}\n")
        log.flush()
log.close()
