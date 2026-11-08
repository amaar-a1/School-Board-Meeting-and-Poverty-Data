# Temporary: DGEEC "Regiões em Números 2024/2025" (ReNE2025): every region's XLSX volume (zip), saved as is.
import json, os, re, time, traceback, urllib.request
OUT = "fetch/out/pt_rene2"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
try:
    links = [l[0] for l in json.load(open("fetch/out/pt_dgeec4/browse.json"))["links"] if "ficheiros" in (l[0] or "")]
    for href in links[:40]:
        try:
            with urllib.request.urlopen(urllib.request.Request(href, headers=UA), timeout=300) as r:
                cd = r.headers.get("Content-Disposition", ""); name = (re.search(r'filename="?([^";]+)', cd) or [None, ""])[1]
                if name.startswith("ReNE2025") and name.endswith("_XLSX.zip"):
                    b = r.read(); open(f"{OUT}/{name}", "wb").write(b); log.write(f"got {name} {len(b)}\n")
                else: log.write(f"skip {name}\n")
        except Exception as e: log.write(f"ERR {href} {str(e)[:60]}\n")
        log.flush(); time.sleep(0.5)
except Exception: log.write(traceback.format_exc()[-800:])
log.close()
