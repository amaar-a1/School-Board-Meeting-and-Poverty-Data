# Round 59: CBS's page for each year's municipal division, 2012-2026 (each lists the municipalities abolished that
# 1 January and the new ones they formed).
import os, urllib.request, time
OUT = "fetch/out/c59"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
for y in range(2012, 2027):
    u = f"https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/overig/gemeentelijke-indelingen-per-jaar/indeling-per-jaar/gemeentelijke-indeling-op-1-januari-{y}"
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
        open(f"{OUT}/nl_{y}.html", "wb").write(b); log.write(f"OK {y} {len(b)} {u}\n")
    except Exception as e: log.write(f"ERR {y} {str(e)[:200]} {u}\n")
    log.flush(); time.sleep(1.5)
log.close()
