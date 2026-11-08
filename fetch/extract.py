# Temporary: DGEEC "Regiões em Números 2023/2024 - Educação": follow the flyer's link and get its files.
import html, io, json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/pt_dgeec2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) school-board research project; github.com/amaar-a1", "Accept": "*/*"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=200):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.geturl(), r.headers.get("Content-Type", ""), r.headers.get("Content-Disposition", ""), r.read()
try:
    final, ct, cd, b = get("https://www.dgeec.medu.pt/l/Z9on6")
    log.write(f"short link -> {final} {ct} {len(b)}\n")
    t = b.decode("utf-8", "ignore")
    open(f"{OUT}/page.html", "w").write(t)
    ids = sorted(set(re.findall(r"api/ficheiros/([0-9a-f]{24})", t)))
    others = sorted(set(re.findall(r'(https?://[^"\'\s<>]+|/api/[^"\'\s<>]+)', t)))[:80]
    log.write(f"file ids {ids}\nother urls {others}\n")
    # the site may be a client-side app: try its API for the page
    m = re.search(r"/p/([A-Za-z0-9_-]+)|pagina[=/]([A-Za-z0-9_-]+)", final)
    for i in ids[:30]:
        try:
            _, ct2, cd2, f = get(f"https://www.dgeec.medu.pt/api/ficheiros/{i}", 300)
            name = (re.search(r'filename="?([^";]+)', cd2) or [None, i])[1]
            open(f"{OUT}/{re.sub(r'[^A-Za-z0-9_.-]', '_', name)[-90:]}", "wb").write(f)
            log.write(f"  {i}: {name} {ct2} {len(f)}\n")
        except Exception as e: log.write(f"  {i}: ERR {str(e)[:80]}\n")
        time.sleep(1)
except Exception: log.write(traceback.format_exc()[-800:])
log.close()
