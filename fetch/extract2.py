# Round 51: Brazil's municipal population estimates (IBGE SIDRA 6579, year by year), Colombia's municipal projections
# 2018-2042 (DANE), Mexico's municipal projections (CONAPO, via datos.gob.mx), and earlier poverty reports for Kenya
# (KNBS) and Sri Lanka (DCS Poverty Indicators).
import os, re, json, urllib.request, urllib.parse, time, html, gzip, shutil
OUT = "fetch/out/c51"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def raw(url, timeout=600): return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
def get(name, url, timeout=600):
    try:
        b = raw(url, timeout)
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url}\n")
    finally: log.flush(); time.sleep(1.5)
def links(b, base, pat):
    t = b.decode("utf-8", "ignore")
    return sorted(set(urllib.parse.urljoin(base, html.unescape(x)) for x in re.findall(r'href="([^"]+)"', t) if re.search(pat, x, re.I)))
# Brazil
br = {}
for y in list(range(2001, 2022)) + [2024, 2025]:
    b = get(None, f"https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/{y}", timeout=300)
    if b:
        try:
            for r in json.loads(b)[1:]: br.setdefault(r["D1C"], {})[str(y)] = r["V"]
        except Exception as e: log.write(f"BR {y} parse {e}\n")
json.dump(br, open(f"{OUT}/br_pop_estimates.json", "w")); log.write(f"BR {len(br)} municipalities\n")
# Colombia
get("co_PPED-AreaMun-2018-2042_VP.xlsx", "https://www.dane.gov.co/files/censo2018/proyecciones-de-poblacion/Municipal/PPED-AreaMun-2018-2042_VP.xlsx", timeout=1200)
# Mexico: CONAPO municipal projections, from datos.gob.mx
for q in ("proyecciones poblacion municipios", "conapo municipios"):
    b = get(f"mx_search_{q.split()[0]}.json", "https://datos.gob.mx/busca/api/3/action/package_search?rows=20&q=" + urllib.parse.quote(q))
    try:
        for p in json.loads(b)["result"]["results"]:
            for r in p.get("resources", []):
                u = r.get("url") or ""
                log.write(f"  MX {p.get('name')} | {r.get('name')} | {u}\n")
                if re.search(r"munic", (p.get("name", "") + r.get("name", "") + u), re.I) and re.search(r"\.(csv|zip|xlsx)$", u, re.I) and re.search(r"conapo|proyec", u + p.get("name", ""), re.I):
                    get("mx_" + os.path.basename(urllib.parse.urlparse(u).path)[-80:], u, timeout=1200)
    except Exception as e: log.write(f"MX ERR {e}\n")
# Kenya: KNBS poverty reports
for q in ("poverty report", "Kenya Poverty Report 2021", "Kenya Poverty Report 2020"):
    b = get(f"ke_search_{len(q)}.html", "https://www.knbs.or.ke/?s=" + urllib.parse.quote(q))
    if not b: continue
    for l in links(b, "https://www.knbs.or.ke/", r"poverty"):
        log.write(f"  KE {l}\n")
        if l.lower().endswith(".pdf"): get("ke_" + os.path.basename(urllib.parse.urlparse(l).path)[-80:], l)
        elif "knbs.or.ke" in l and re.search(r"poverty-report|basic-report", l, re.I):
            b2 = get(None, l)
            if b2:
                for l2 in links(b2, l, r"\.pdf$"):
                    if re.search(r"poverty", l2, re.I): log.write(f"    KE pdf {l2}\n"); get("ke_" + os.path.basename(urllib.parse.urlparse(l2).path)[-80:], l2)
# Sri Lanka: DCS poverty indicators (2016 and 2012/13 district figures)
for page in ("http://www.statistics.gov.lk/Poverty/StaticalInformation/", "http://www.statistics.gov.lk/Poverty/StaticalInformation/PovertyIndicators-2016",
             "http://www.statistics.gov.lk/Poverty/StaticalInformation/PovertyIndicators"):
    b = get(f"lk_page_{len(page)}.html", page)
    if not b: continue
    for l in links(b, page, r"pover|\.pdf"):
        log.write(f"  LK {l}\n")
        if l.lower().endswith(".pdf") and re.search(r"pov|indicator", l, re.I): get("lk_" + os.path.basename(urllib.parse.urlparse(l).path)[-80:], l)
for f in os.listdir(OUT):
    p = f"{OUT}/{f}"
    if os.path.getsize(p) > 50e6 and not f.endswith(".gz"):
        with open(p, "rb") as a, gzip.open(p + ".gz", "wb") as b: shutil.copyfileobj(a, b)
        os.remove(p)
log.close()
