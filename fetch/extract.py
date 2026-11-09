# Temporary: INE 2021 census table 66614 (population 15+ by municipality, sex, nationality and level of studies in progress).
import os, urllib.request
OUT = "fetch/out/es_enr1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for n, u in {"t66614.csv": "https://www.ine.es/jaxiT3/files/t/csv_bd/66614.csv", "t66627.csv": "https://www.ine.es/jaxiT3/files/t/csv_bd/66627.csv"}.items():
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=900) as r: b = r.read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"ok {n} {len(b)}\n")
    except Exception as e: log.write(f"ERR {n} {str(e)[:150]}\n")
log.close()
