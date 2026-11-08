# Temporary: Flemish nursery and primary pupils by the municipality of the school site (Dataloep, 1 February 2025).
import csv, io, json, os, time, traceback, urllib.request
from collections import Counter, defaultdict
OUT = "fetch/out/bep6"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) school-board research project; github.com/amaar-a1"}
log = open(f"{OUT}/log.txt", "w")
try:
    u = "https://opendata.dataplatform-onderwijs.vlaanderen.be/dataloep/inschrijvingen-leerplicht-instellingen-dataset-2024-2025-1feb.csv"
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=900) as r: b = r.read()
    rd = csv.DictReader(io.StringIO(b.decode("utf-8-sig", "ignore")))
    kinds, agg, names = Counter(), defaultdict(lambda: defaultdict(int)), {}
    for row in rd:
        h = row["hoofdstructuur_inschrijving"]; kinds[(row["hoofdstructuur_inschrijving_code"], h)] += int(float(row["aantal_inschrijvingen"] or 0))
        low = h.lower()
        key = "nursery" if "kleuter" in low else "primary" if "lager" in low else None
        if not key: continue
        nis = row["vestiging_fusiegemeente_nis"]; names[nis] = row["vestiging_fusiegemeente_naam"]
        agg[nis][key] += int(float(row["aantal_inschrijvingen"] or 0))
    json.dump({"source": u, "year": "2024-25 (1 February 2025)", "names": names, "pupils": agg}, open(f"{OUT}/vl_pupils_2425.json", "w"), ensure_ascii=False)
    log.write(f"{len(b)} bytes; {len(agg)} municipalities\nkinds: {sorted(kinds.items())}\n")
except Exception: log.write(traceback.format_exc()[-800:])
log.close()
