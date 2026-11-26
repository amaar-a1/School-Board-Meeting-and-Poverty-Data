# Round 65: Peru's census population by district. 2017: INEI's "Resultados definitivos" publications page and what
# it links; 2007: the census's statistical tables (tabulados) and what they link; 2025: the gob.pe page of the
# first results, for any spreadsheet attached. Pages are followed one level where they look like table indexes.
import os, re, urllib.request, urllib.parse, time, html, gzip
OUT = "fetch/out/c65"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=300):
    try:
        b = urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%#;,+@~"), headers=UA), timeout=timeout).read()
        if name:
            if len(b) > 45e6: gzip.open(f"{OUT}/{name}.gz", "wb").write(b)
            else: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:160]} {url}\n")
    finally: log.flush(); time.sleep(1.2)
safe = lambda s: re.sub(r"[^\w.-]+", "_", s)[-90:]
def links(page, b):
    return sorted(set(urllib.parse.urljoin(page, html.unescape(x)) for x in re.findall(r'(?:href|src)="([^"]+)"', (b or b"").decode("utf-8", "ignore"))))
seen, n = set(), {"dl": 0}
def crawl(tag, p, depth=0):
    if p in seen or len(seen) > 120: return
    seen.add(p)
    b = get(f"{tag}_page_{len(seen)}.html", p)
    for l in links(p, b):
        txt = l.lower()
        if re.search(r"\.(xlsx?|csv|zip|pdf)(\?|$)", txt):
            log.write(f"  {tag} LINK {l}\n")
            if n["dl"] < 40 and re.search(r"distrit|poblaci|pob_|cuadro|c0?1|resultado|definitiv|tomo|lib1|libro", txt):
                n["dl"] += 1; get(f"{tag}_" + safe(os.path.basename(urllib.parse.urlparse(l).path)), l)
        elif depth < 1 and urllib.parse.urlparse(l).netloc == urllib.parse.urlparse(p).netloc and re.search(r"tabul|cuadro|public|resultado|distrit|poblaci", txt):
            log.write(f"  {tag} follow {l}\n"); crawl(tag, l, depth + 1)
crawl("pe2017", "http://censo2017.inei.gob.pe/publicaciones/")
crawl("pe2007", "https://censos.inei.gob.pe/cpv2007/tabulados/")
crawl("pe2025", "https://www.gob.pe/institucion/inei/informes-publicaciones/8200490-peru-crecimiento-y-distribucion-de-la-poblacion-primeros-resultados")
log.close()
