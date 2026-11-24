# Round 45: Czechia: unemployment in municipalities, every December 2015-2023 (MPSV open data), for change over time.
import os, urllib.request, time
OUT = "fetch/out/c45"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
for y in range(2015, 2024):
    u = f"https://data.mpsv.cz/od/soubory/nezamestnanost-v-obcich/nezamestnanost-v-obcich-12-{y}.json.gz"
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
        open(f"{OUT}/cz_unemp_12_{y}.json.gz", "wb").write(b); log.write(f"OK {y} {len(b)}\n")
    except Exception as e: log.write(f"ERR {y} {e}\n")
    log.flush(); time.sleep(2)
