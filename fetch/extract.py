# Temporary: Croatia, geostat.gov.hr (DZS spatial statistics portal): the app page and its scripts, to find the data service.
import os, re, urllib.parse, urllib.request
OUT = "fetch/out/hr4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120) as r: return r.read(), r.geturl()
try:
    b, final = get("https://geostat.gov.hr/?lang=en"); open(f"{OUT}/index.html", "wb").write(b); log.write(f"ok index {len(b)} {final}\n")
    for s in re.findall(rb'src="([^"]+\.js[^"]*)"', b)[:40]:
        u = urllib.parse.urljoin(final, s.decode())
        try:
            j, _ = get(u); n = re.sub(r"[^A-Za-z0-9.]", "_", os.path.basename(urllib.parse.urlparse(u).path))[:60]
            open(f"{OUT}/{n}", "wb").write(j); log.write(f"js {u} {len(j)}\n")
        except Exception as e: log.write(f"ERR {u} {e}\n")
except Exception as e: log.write(f"ERR index {str(e)[:200]}\n")
for u in ("https://geostat.gov.hr/geoserver/wfs?service=WFS&request=GetCapabilities", "https://geostat.gov.hr/geoserver/ows?service=WMS&request=GetCapabilities"):
    try: b, _ = get(u); open(f"{OUT}/{'wfs' if 'WFS' in u else 'wms'}_caps.xml", "wb").write(b); log.write(f"ok {u} {len(b)}\n")
    except Exception as e: log.write(f"ERR {u} {str(e)[:120]}\n")
log.close()
