# Temporary: Eurostat's at-risk-of-poverty rate by NUTS 2 region (ilc_li41) for Spain's autonomous communities,
# the fallback for municipalities INE's household income atlas leaves out.
import json, os, time, urllib.request
OUT = "fetch/out/es_nuts2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
geos = ["ES11", "ES12", "ES13", "ES21", "ES22", "ES23", "ES24", "ES30", "ES41", "ES42", "ES43", "ES51", "ES52", "ES53",
        "ES61", "ES62", "ES63", "ES64", "ES70"]
u = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_li41?format=JSON&lang=EN&sinceTimePeriod=2018&"
     + "&".join(f"geo={g}" for g in geos))
for a in range(3):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r: b = r.read()
        d = json.loads(b); json.dump(d, open(f"{OUT}/eurostat_ilc_li41_es.json", "w"))
        log.write(f"ok {len(b)} bytes; ids {d.get('id')} size {d.get('size')}; values {len(d.get('value', {}))}\n"); break
    except Exception as e:
        log.write(f"try {a}: {e}\n"); time.sleep(20)
log.close()
