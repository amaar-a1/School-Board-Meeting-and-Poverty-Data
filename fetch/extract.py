# Temporary: Poland's pupils by school from the education ministry's SIO, published on dane.gov.pl
# ("Uczniowie szkół w roku 2025" and the school list as of 30.09.2025), saved as they come.
import json, os, traceback, urllib.request
OUT = "fetch/out/pl_sio"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for rid in ("1254005", "1254769"):
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://api.dane.gov.pl/1.4/resources/{rid}", headers=UA), timeout=120) as r: m = json.loads(r.read())
        a = m["data"]["attributes"]; json.dump(a, open(f"{OUT}/meta_{rid}.json", "w"), ensure_ascii=False, indent=1)
        url = a.get("download_url") or a.get("file_url") or a.get("link")
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r:
            b = r.read(); ext = os.path.splitext(url.split("?")[0])[1] or "." + (a.get("format") or "bin")
            open(f"{OUT}/res_{rid}{ext}", "wb").write(b)
        log.write(f"{rid} {a.get('title')} {a.get('format')} {len(b)} {url}\n")
    except Exception: log.write(f"{rid} " + traceback.format_exc()[-600:] + "\n")
log.close()
