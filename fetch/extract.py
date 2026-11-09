# Temporary: (1) INE census 2021 table 66614 (studies in progress, 15+, by municipality): only its layout (header, sample,
# each column's values), as the file is over GitHub's size limit; (2) Eurostat population by 5-year age group for every
# NUTS 3 region, 2024; (3) Eurostat's LAU-NUTS 2024 correspondence (which NUTS 3 region each municipality is in).
import collections, csv, io, json, os, urllib.request
OUT = "fetch/out/es_enr2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=900):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
try:
    b = get("https://www.ine.es/jaxiT3/files/t/csv_bd/66614.csv")
    t = b.decode("utf-8-sig", "ignore"); lines = t.splitlines()
    open(f"{OUT}/t66614_head.txt", "w").write("\n".join(lines[:300]))
    rd = csv.reader(io.StringIO(t), delimiter="\t"); h = next(rd); vals = collections.defaultdict(collections.Counter)
    for i, row in enumerate(rd):
        for j, c in enumerate(row[:-1]):
            if len(vals[j]) < 60 or c in vals[j]: vals[j][c] += 1
    json.dump({"header": h, "rows": len(lines) - 1, "values": {h[j]: dict(v.most_common(60)) for j, v in vals.items()}}, open(f"{OUT}/t66614_layout.json", "w"), ensure_ascii=False, indent=0)
    log.write(f"ine ok {len(b)} {len(lines)}\n")
except Exception as e: log.write(f"ERR ine {str(e)[:200]}\n")
log.flush()
try:
    u = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_r_pjangrp3?format=JSON&lang=EN&sex=T&unit=NR&time=2024"
         "&age=TOTAL&age=Y_LT5&age=Y5-9&age=Y10-14&age=Y15-19")
    b = get(u); open(f"{OUT}/eurostat_nuts3_age_2024.json", "wb").write(b); log.write(f"eurostat ok {len(b)}\n")
except Exception as e: log.write(f"ERR eurostat {str(e)[:200]}\n")
for name, u in (("lau_nuts_2024.xlsx", "https://ec.europa.eu/eurostat/documents/345175/501971/EU-27-LAU-2024-NUTS-2024.xlsx"),
                ("lau_nuts_2023.xlsx", "https://ec.europa.eu/eurostat/documents/345175/501971/EU-27-LAU-2023-NUTS-2021.xlsx")):
    try: b = get(u); open(f"{OUT}/{name}", "wb").write(b); log.write(f"ok {name} {len(b)}\n")
    except Exception as e: log.write(f"ERR {name} {str(e)[:150]}\n")
log.close()
