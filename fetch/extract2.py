# Round 55: Mexico, CONAPO's "Reconstrucción y proyecciones de la población de los municipios de México 1990-2040":
# the page, the files it links (the interactive PDF's national database), and links inside that PDF.
import os, re, json, urllib.request, urllib.parse, time, html, gzip, shutil
OUT = "fetch/out/c55"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=900):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url}\n")
    finally: log.flush(); time.sleep(1.5)
page = "https://www.gob.mx/conapo/documentos/reconstruccion-y-proyecciones-de-la-poblacion-de-los-municipios-de-mexico-1990-2040"
b = get("mx_page.html", page)
links = sorted(set(urllib.parse.urljoin(page, html.unescape(x)) for x in re.findall(r'href="([^"]+)"', b.decode("utf-8", "ignore")))) if b else []
log.write("  links " + json.dumps([l for l in links if re.search(r"\.(pdf|xlsx?|csv|zip)$|conapo|attachment", l, re.I)]) + "\n")
for l in links:
    if re.search(r"\.(xlsx?|csv|zip)$", l, re.I) or (re.search(r"\.pdf$", l, re.I) and re.search(r"attachment|conapo", l, re.I)):
        d = get("mx_" + os.path.basename(urllib.parse.urlparse(l).path)[-90:], l)
        if d and l.lower().endswith(".pdf"):   # an interactive PDF: the URIs it opens
            uris = sorted(set(re.findall(rb"/URI\s*\((https?://[^)]+)\)", d)))
            log.write(f"  pdf uris {[u.decode('latin-1') for u in uris][:60]}\n")
            for u in [u.decode("latin-1") for u in uris]:
                if re.search(r"(nacional|national).*\.(xlsx?|csv|zip)$|\.(zip)$", u, re.I): get("mx_" + os.path.basename(urllib.parse.urlparse(u).path)[-90:], u)
for f in os.listdir(OUT):
    p = f"{OUT}/{f}"
    if os.path.getsize(p) > 50e6 and not f.endswith(".gz"):
        with open(p, "rb") as a, gzip.open(p + ".gz", "wb") as b2: shutil.copyfileobj(a, b2)
        os.remove(p)
log.close()
