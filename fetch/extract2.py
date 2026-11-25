# Round 49: Poland's family-benefit share by gmina for 2017-2023 (BDL), retried slowly after round 48's server errors.
import os, json, urllib.request, time
OUT = "fetch/out/c49"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "application/json"}
BDL = "https://bdl.stat.gov.pl/api/v1"
def fetch(url):
    for t in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read())
        except Exception as e:
            log.write(f"  retry {t} {str(e)[:80]} {url}\n"); log.flush(); time.sleep(30 * (t + 1))
    return None
vals = {}
for yr in range(2017, 2024):
    page, got = 0, 0
    while True:
        d = fetch(f"{BDL}/data/by-variable/259889?unit-level=6&year={yr}&page-size=100&page={page}&format=json&lang=pl")
        if d is None: log.write(f"PL {yr} gave up at page {page}\n"); break
        for r in d.get("results", []):
            for x in r.get("values", []):
                if x.get("val") is not None: vals.setdefault(r["id"], {})[str(x.get("year", yr))] = x["val"]; got += 1
        if not d.get("links", {}).get("next"): break
        page += 1; time.sleep(4)
    log.write(f"PL {yr}: {got}\n"); log.flush()
    json.dump(vals, open(f"{OUT}/pl_bdl_259889_2017_2023.json", "w"))
    time.sleep(20)
log.close()
