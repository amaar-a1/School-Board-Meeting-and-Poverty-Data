# Round 56: municipal mergers, to add former municipalities up on today's borders in the population and enrollment
# histories. France: INSEE's COG "mouvements des communes" (via data.gouv.fr's catalogue). Italy: ISTAT's
# "Variazioni amministrative e territoriali dei comuni dal 1991". Netherlands: CBS's municipal changes (via its
# OData catalogue). Wikidata (dissolved municipalities and what replaced them) for all three as a cross-check.
import os, re, json, urllib.request, urllib.parse, time, html, gzip, shutil
OUT = "fetch/out/c56"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=300, headers=None):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=timeout).read()
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url}\n")
    finally: log.flush(); time.sleep(1.5)
def links(page, b):
    return sorted(set(urllib.parse.urljoin(page, html.unescape(x)) for x in re.findall(r'href="([^"]+)"', b.decode("utf-8", "ignore")))) if b else []

# France
for q in ("code officiel géographique 2025", "code officiel geographique"):
    b = get(None, "https://www.data.gouv.fr/api/1/datasets/?page_size=20&q=" + urllib.parse.quote(q))
    if not b: continue
    for d in json.loads(b).get("data", []):
        for r in d.get("resources", []):
            u = r.get("url") or ""
            log.write(f"  res {d.get('title')} | {r.get('title')} | {u}\n")
            if re.search(r"mvt|mouvement", (r.get("title") or "") + u, re.I) and re.search(r"\.(csv|zip)$", u, re.I):
                get("fr_" + os.path.basename(urllib.parse.urlparse(u).path)[-80:], u)
for p in ("https://www.insee.fr/fr/information/8377162", "https://www.insee.fr/fr/information/7766585", "https://www.insee.fr/fr/information/2560452"):
    b = get(None, p)
    for l in links(p, b):
        if re.search(r"mvt|mouvement", l, re.I) and re.search(r"\.(csv|zip)$", l, re.I): get("fr_" + os.path.basename(urllib.parse.urlparse(l).path)[-80:], l)
        elif re.search(r"/information/\d+$", l) and re.search(r"cog|code", l, re.I): log.write(f"  insee link {l}\n")

# Italy
get("it_variazioni.zip", "https://www.istat.it/storage/codici-unita-amministrative/Variazioni-amministrative-e-territoriali-dei-comuni-dal-1991.zip")
for p in ("https://www.istat.it/classificazioni-e-strumenti/codici-dei-comuni-delle-province-e-delle-regioni/",
          "https://www.istat.it/it/archivio/6789"):
    b = get(None, p)
    for l in links(p, b):
        if re.search(r"variaz|soppress", l, re.I) and re.search(r"\.(zip|xlsx?|csv)$", l, re.I): get("it_" + os.path.basename(urllib.parse.urlparse(l).path)[-80:], l)

# Netherlands: CBS's catalogue, tables about municipal changes ("herindeling", "gemeentelijke indeling")
b = get("nl_catalog.json", "https://opendata.cbs.nl/ODataCatalog/Tables?$format=json&$select=Identifier,Title,Period&$filter=" +
        urllib.parse.quote("substringof('herindeling',tolower(Title)) or substringof('gemeentelijke indeling',tolower(Title)) or substringof('gemeentegrenzen',tolower(Title))"))
if b:
    for t in json.loads(b).get("value", [])[:15]:
        log.write(f"  cbs {t}\n")
        get(f"nl_{t['Identifier']}.json", f"https://opendata.cbs.nl/ODataApi/odata/{t['Identifier']}/TypedDataSet?$format=json")
        get(f"nl_{t['Identifier']}_regions.json", f"https://opendata.cbs.nl/ODataApi/odata/{t['Identifier']}/RegioS?$format=json")

# Wikidata: dissolved municipalities with their code, end date and successor (with its code)
Q = """SELECT ?old ?oldLabel ?code ?end ?new ?newLabel ?newcode WHERE {
  ?old wdt:%(p)s ?code . ?old p:%(p)s ?st . OPTIONAL { ?old wdt:P576 ?end } OPTIONAL { ?old wdt:P1366 ?new . OPTIONAL { ?new wdt:%(p)s ?newcode } }
  FILTER(BOUND(?end) || BOUND(?new))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "%(l)s,en". } }"""
for cc, p, l in (("nl", "P382", "nl"), ("fr", "P374", "fr"), ("it", "P635", "it")):
    get(f"wd_{cc}.json", "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(Q % {"p": p, "l": l}),
        headers={"Accept": "application/sparql-results+json"})

for f in os.listdir(OUT):
    p = f"{OUT}/{f}"
    if os.path.getsize(p) > 50e6 and not f.endswith(".gz"):
        with open(p, "rb") as a, gzip.open(p + ".gz", "wb") as b2: shutil.copyfileobj(a, b2)
        os.remove(p)
log.close()
