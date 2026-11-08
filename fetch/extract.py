# Temporary: Flemish enrolments by school (Dataloep, 1 February 2025), kept if small enough, with its header.
import csv, io, os, time, traceback, urllib.request
OUT = "fetch/out/bep5"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) school-board research project; github.com/amaar-a1"}
log = open(f"{OUT}/log.txt", "w")
for name in ("inschrijvingen-leerplicht-instellingen-dataset-2024-2025-1feb.csv", "inschrijvingen-leerplicht-instellingen-dataset-2024-2025-1okt.csv"):
    u = "https://opendata.dataplatform-onderwijs.vlaanderen.be/dataloep/" + name
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=600) as r: b = r.read()
        log.write(f"{name}: {len(b)} bytes\n{b[:1500].decode('utf-8', 'ignore')}\n")
        if len(b) < 90_000_000: open(f"{OUT}/{name}", "wb").write(b)
        break
    except Exception as e: log.write(f"{name}: ERR {traceback.format_exc()[-400:]}\n")
    time.sleep(2)
log.close()
