# Round 57: Italy's detailed municipal changes. ISTAT's page of municipal codes, saved with every file it links
# (the list of suppressed municipalities and the changes since 1991), and Wikidata's dissolved Italian municipalities
# (ISTAT code P635) as a cross-check (one query a minute: the service is rate-limiting).
import os, re, json, urllib.request, urllib.parse, time, html, gzip, shutil
OUT = "fetch/out/c57"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=300, headers=None):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=timeout).read()
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url}\n")
    finally: log.flush(); time.sleep(1.5)
seen = set()
for p in ("https://www.istat.it/classificazioni-e-strumenti/codici-dei-comuni-delle-province-e-delle-regioni/",
          "https://www.istat.it/classificazione/codici-dei-comuni-delle-province-e-delle-regioni/"):
    b = get("it_page_%d.html" % len(seen), p)
    if not b: continue
    for l in sorted(set(urllib.parse.urljoin(p, html.unescape(x)) for x in re.findall(r'href="([^"]+)"', b.decode("utf-8", "ignore")))):
        log.write(f"  link {l}\n")
        if re.search(r"\.(zip|xlsx?|csv)$", l, re.I) and l not in seen:
            seen.add(l); get("it_" + os.path.basename(urllib.parse.urlparse(l).path)[-90:], l)
for u in ("https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-soppressi.zip",
          "https://www.istat.it/storage/codici-unita-amministrative/Variazioni-amministrative-e-territoriali-dal-1991.zip",
          "https://www.istat.it/storage/codici-unita-amministrative/Elenco-codici-statistici-e-denominazioni-al-01_01_2025.zip"):
    if u not in seen: get("it_" + os.path.basename(u), u)
time.sleep(65)
Q = """SELECT ?old ?oldLabel ?code ?end ?new ?newLabel ?newcode WHERE {
  ?old wdt:P635 ?code . OPTIONAL { ?old wdt:P576 ?end } OPTIONAL { ?old wdt:P1366 ?new . OPTIONAL { ?new wdt:P635 ?newcode } }
  FILTER(BOUND(?end) || BOUND(?new))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". } }"""
get("wd_it.json", "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(Q), headers={"Accept": "application/sparql-results+json"})
for f in os.listdir(OUT):
    p = f"{OUT}/{f}"
    if os.path.getsize(p) > 50e6 and not f.endswith(".gz"):
        with open(p, "rb") as a, gzip.open(p + ".gz", "wb") as b2: shutil.copyfileobj(a, b2)
        os.remove(p)
log.close()
