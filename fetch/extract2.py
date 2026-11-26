# Round 62: census population by municipality/district for countries whose site has one year: the Philippines,
# Peru, Ecuador, Costa Rica, South Africa, Kenya, Rwanda, Sri Lanka, Uruguay. Discovery through documented
# routes: HDX's CKAN search, the national CKAN portals, the PSA's PXWeb API, and each office's census pages (the
# spreadsheets they link are saved).
import os, re, json, urllib.request, urllib.parse, time, html, gzip, shutil, ssl
OUT = "fetch/out/c62"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
got = {"n": 0}
def get(name, url, timeout=180, keep=True):
    try:
        b = urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%#;,+@~"), headers=UA), timeout=timeout).read()
        if keep and name and len(b) < 45e6: open(f"{OUT}/{name}", "wb").write(b); got["n"] += 1
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:160]} {url}\n")
    finally: log.flush(); time.sleep(1.2)
safe = lambda s: re.sub(r"[^\w.-]+", "_", s)[-90:]
def links(page, b):
    return sorted(set(urllib.parse.urljoin(page, html.unescape(x)) for x in re.findall(r'href="([^"]+)"', (b or b"").decode("utf-8", "ignore"))))
WANT = re.compile(r"censo|census|poblaci|population|habitantes", re.I)
def ckan(base, q, tag, maxdl=8):
    b = get(None, f"{base}/api/3/action/package_search?rows=40&q=" + urllib.parse.quote(q))
    try: res = json.loads(b)["result"]["results"]
    except Exception: return
    n = 0
    for p in res:
        log.write(f"  {tag} PKG {p.get('name')} | {p.get('title')}\n")
        for r in p.get("resources", [])[:12]:
            u = r.get("url") or ""
            log.write(f"    RES {r.get('format')} | {r.get('name')} | {r.get('size')} | {u}\n")
            if n < maxdl and WANT.search((p.get("title") or "") + " " + (r.get("name") or "")) and re.search(r"csv|xls", (r.get("format") or "") + u, re.I) \
                    and (r.get("size") or 0) < 30e6:
                n += 1; get(f"{tag}_" + safe((r.get("name") or "") + "_" + os.path.basename(urllib.parse.urlparse(u).path)), u)
# HDX
for tag, q in [("phl", "philippines population census municipality"), ("per", "peru censo poblacion distrito"), ("ecu", "ecuador censo poblacion canton"),
               ("cri", "costa rica censo poblacion canton"), ("zaf", "south africa census population municipality"), ("ken", "kenya census 2009 population"),
               ("rwa", "rwanda census population district"), ("lka", "sri lanka census population district"), ("ury", "uruguay censo poblacion departamento")]:
    ckan("https://data.humdata.org", q, "hdx_" + tag, maxdl=4)
# national CKAN portals
for base, tag, qs in [("https://www.datosabiertos.gob.pe", "pe", ["censo 2017 poblacion distrito", "censo 2007 poblacion"]),
                      ("https://www.datosabiertos.gob.ec", "ec", ["censo poblacion canton"]),
                      ("https://catalogodatos.gub.uy", "uy", ["censo poblacion departamento"])]:
    for q in qs: ckan(base, q, tag)
# PSA PXWeb (OpenSTAT): the databases and their census folders
b = get("psa_db.json", "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB")
try:
    for d in json.loads(b)[:12]:
        log.write(f"  PSA DB {d}\n")
        b2 = get(None, f"https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/{d['id']}")
        for x in (json.loads(b2) if b2 else [])[:60]:
            log.write(f"    {d['id']} / {x}\n")
            if re.search(r"popul|census", x.get("text", ""), re.I) and x.get("type") == "l":
                b3 = get(None, f"https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/{d['id']}/{x['id']}")
                for t in (json.loads(b3) if b3 else [])[:60]: log.write(f"      {x['id']} / {t}\n")
except Exception as e: log.write(f"  PSA ERR {e}\n")
# office pages: save the page and the spreadsheets it links (population/census ones)
pages = [("cri", "https://inec.cr/estadisticas-fuentes/censos/censo-2011"), ("cri", "https://inec.cr/estadisticas-fuentes/censos/censo-2022"),
         ("cri", "https://admin.inec.cr/sites/default/files/media/repoblaccenso2011-01.xlsx"),
         ("rwa", "https://www.statistics.gov.rw/statistical-publications/subject/population-size-and-population-characteristics"),
         ("rwa", "https://www.statistics.gov.rw/publication/main_indicators_2022"),
         ("lka", "http://www.statistics.gov.lk/Population/StaticalInformation/CPH2011"),
         ("lka", "https://www.statistics.gov.lk/Census/Population"),
         ("ury", "https://www.gub.uy/instituto-nacional-estadistica/datos-y-estadisticas/estadisticas/temas/poblacion-hogares"),
         ("ury", "https://www.ine.gub.uy/censos-2011"),
         ("ecu", "https://www.censoecuador.gob.ec/resultados-censo/"),
         ("ecu", "https://www.ecuadorencifras.gob.ec/base-de-datos-censo-de-poblacion-y-vivienda/"),
         ("zaf", "https://census.statssa.gov.za/"), ("zaf", "https://www.statssa.gov.za/?page_id=3836"),
         ("ken", "https://www.knbs.or.ke/2009-kenya-population-and-housing-census-reports/"),
         ("per", "https://www.inei.gob.pe/estadisticas/censos/"),
         ("phl", "https://psa.gov.ph/population-and-housing/node/164811"), ("phl", "https://psa.gov.ph/content/2020-census-population-and-housing-2020-cph-population-counts-declared-official-president")]
for tag, p in pages:
    b = get(f"{tag}_page_" + safe(urllib.parse.urlparse(p).path or "home") + (".xlsx" if p.endswith(".xlsx") else ".html"), p)
    if not b or p.endswith(".xlsx"): continue
    n = 0
    for l in links(p, b):
        if re.search(r"\.(xlsx?|csv|zip)(\?|$)", l, re.I):
            log.write(f"  {tag} LINK {l}\n")
            if n < 15 and WANT.search(l + " "):
                n += 1; get(f"{tag}_" + safe(os.path.basename(urllib.parse.urlparse(l).path)), l)
        elif re.search(r"censo|census|poblaci|population", l, re.I): log.write(f"  {tag} page-link {l}\n")
log.write(f"saved {got['n']}\n"); log.close()
