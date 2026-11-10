# Temporary: Mayotte communes' legal population and area (geo.api.gouv.fr, from INSEE).
import json, os, urllib.request
OUT = "fetch/out/myt1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for u in ["https://geo.api.gouv.fr/communes?codeDepartement=976&fields=nom,code,population,surface",
          "https://geo.api.gouv.fr/communes?codeDepartement=971&fields=nom,code,population,surface&limit=3"]:
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
        log.write(u + "\n" + b.decode()[:4000] + "\n")
        if "976" in u: open(f"{OUT}/mayotte.json", "wb").write(b)
    except Exception as e: log.write(f"ERR {u} {e}\n")
log.close()
