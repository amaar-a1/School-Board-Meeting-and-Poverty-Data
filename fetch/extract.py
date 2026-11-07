# Temporary: Statistics Finland's municipality-to-region correspondence (kunta -> maakunta), for the site's region menu.
import json, os, time, urllib.request
OUT = "fetch/out/fi_regions"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "application/json"}
log = open(f"{OUT}/log.txt", "w")
for date in ("20260101", "20250101", "20240101"):
    u = (f"https://data.stat.fi/api/classifications/v2/correspondenceTables/kunta_1_{date}%23maakunta_1_{date}/maps"
         "?content=data&meta=max&lang=en&format=json")
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120) as r: b = r.read()
        d = json.loads(b)
        json.dump(d, open(f"{OUT}/kunta_maakunta_{date}.json", "w"), ensure_ascii=False)
        log.write(f"{date}: {len(b)} bytes, {len(d)} entries; first {json.dumps(d[:1], ensure_ascii=False)[:600]}\n")
        break
    except Exception as e:
        log.write(f"{date}: {e}\n"); time.sleep(5)
log.close()
