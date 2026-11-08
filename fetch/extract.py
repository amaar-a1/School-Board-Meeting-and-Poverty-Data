# Temporary: Flemish pupils by municipality, via the Statistical Yearbook of Flemish Education's data page.
import html, json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/bep4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) school-board research project; github.com/amaar-a1", "Accept": "*/*", "Accept-Language": "nl,en"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=180):
    err = None
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.geturl(), r.read()
        except Exception as e: err = e; time.sleep(10 * (a + 1))
    raise err
seen, queue = set(), ["https://www.vlaanderen.be/Data/14217517-283c-4597-a487-6548284b5092", "https://onderwijs.vlaanderen.be/Data/14217517-283c-4597-a487-6548284b5092",
                      "https://www.vlaanderen.be/onderwijsprofessionals/regelgeving-data-en-onderzoek/data-en-onderzoek/data/dataloep"]
got = 0
while queue and len(seen) < 25:
    u = queue.pop(0)
    if u in seen: continue
    seen.add(u)
    try:
        final, b = get(u)
        if b[:2] == b"PK" or b[:4] == b"\xd0\xcf\x11\xe0":
            fn = re.sub(r"[^A-Za-z0-9_.-]", "_", final.split("/")[-1])[-80:] or f"file{got}"
            open(f"{OUT}/vl_{fn}", "wb").write(b); got += 1; log.write(f"FILE {final} {len(b)}\n"); continue
        t = b.decode("utf-8", "ignore")
        title = (re.search(r"<title>(.*?)</title>", t, re.S) or [None, ""])[1].strip()[:100]
        ls = sorted({(html.unescape(h), re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()[:90]) for h, x in re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>', t, re.S)
                     if re.search(r"\.xlsx|\.xls|\.zip|\.csv|jaarboek|basisonderwijs|leerling|/Data/|download", h + x, re.I)})
        log.write(f"PAGE {final} [{title}] {ls[:40]}\n")
        for h, x in ls:
            v = urllib.parse.urljoin(final, h)
            if re.search(r"\.xlsx|\.xls|\.zip|/Data/|download|jaarboek", v + x, re.I) and v not in seen and ("vlaanderen.be" in v): queue.append(v)
    except Exception as e: log.write(f"ERR {u} {str(e)[:100]}\n")
    log.flush(); time.sleep(1)
log.close()
