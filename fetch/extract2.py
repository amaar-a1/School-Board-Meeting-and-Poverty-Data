# Round 54 (Denmark retried after a connection reset; the rest of round 53 kept for reference): earlier years from sources the site already uses: Japan's municipal pupils (e-Stat SSDS 0000020205,
# E2501 and E3501), Colombia's municipal education statistics (datos.gov.co nudc-7mev, every year), Taiwan's pupils by
# county (Ministry of Education open data, every year in each file), Norway's pupils (SSB 11980, every year), Sweden's
# pupils (Kolada N15835, 2015-2024), Denmark's pupils (LABY23) and child poverty (LABY07), every year.
import os, re, json, urllib.request, urllib.parse, time, gzip, shutil
OUT = "fetch/out/c54"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, data=None, timeout=600, ctype="application/json"):
    try:
        req = urllib.request.Request(url, data=data.encode() if isinstance(data, str) else data, headers={**UA, **({"Content-Type": ctype} if data else {})})
        b = urllib.request.urlopen(req, timeout=timeout).read()
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url[:150]}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url[:150]}\n")
    finally: log.flush(); time.sleep(1.5)
# Denmark: LABY23 (pupils) and LABY07 (children in relative poverty), every year
for t in ("LABY23", "LABY07"):
    info = get(f"dk_{t}_info.json", f"https://api.statbank.dk/v1/tableinfo/{t}?lang=en&format=JSON")
    if not info: continue
    vs = json.loads(info)["variables"]
    log.write(f"  DK {t} vars {[(v['id'], len(v['values']), [x['text'] for x in v['values'][:3]]) for v in vs]}\n")
    body = {"table": t, "format": "CSV", "lang": "en", "variables": [{"code": v["id"], "values": ["*"]} for v in vs]}
    get(f"dk_{t}_all.csv", "https://api.statbank.dk/v1/data", data=json.dumps(body))
for f in os.listdir(OUT):
    p = f"{OUT}/{f}"
    if os.path.getsize(p) > 50e6 and not f.endswith(".gz"):
        with open(p, "rb") as a, gzip.open(p + ".gz", "wb") as b: shutil.copyfileobj(a, b)
        os.remove(p)
log.close()
