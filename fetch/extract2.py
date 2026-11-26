# Round 60 (scheduled retry): enrollment by district through documented routes only.
# India: data.gov.in's catalogue and search pages for UDISE+ district enrolment, and the CSV/XLSX downloads they link
# (503 on 24 November). Paraguay: datos.gov.py's CKAN API (package_search, then each matching package's resources;
# a maintenance page on 24 November).
import os, re, json, urllib.request, urllib.parse, time, http.cookiejar, html
OUT = "fetch/out/c60"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(name, url, keep=True, limit=90e6, timeout=120):
    try:
        b = op.open(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if keep and name and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n   {b[:200]!r}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url}\n")
    finally: log.flush(); time.sleep(2)
def links(page, b, pat):
    s = (b or b"").decode("utf-8", "ignore")
    return sorted(set(urllib.parse.urljoin(page, html.unescape(u)) for u in re.findall(r'(?:href|src)="([^"]+)"', s) if re.search(pat, u, re.I)))
safe = lambda u: re.sub(r"[^\w.-]+", "_", urllib.parse.urlparse(u).path)[-80:]
# India
pages = ["https://www.data.gov.in/catalog/unified-district-information-system-education-plus-udise",
         "https://www.data.gov.in/search?title=udise%20district%20enrolment",
         "https://www.data.gov.in/search?title=district%20wise%20enrolment",
         "https://www.data.gov.in/sector/education"]
got = 0
for i, p in enumerate(pages):
    b = get(f"in_page_{i}.html", p)
    for l in links(p, b, r"\.(csv|xlsx?)(\?|$)|/resource/|/catalog/")[:60]:
        log.write(f"  LINK {l}\n")
        if re.search(r"\.(csv|xlsx?)(\?|$)", l, re.I) and re.search(r"enrol|udise|district", l, re.I) and got < 20:
            got += 1; get("in_" + safe(l), l)
# Paraguay
for q in ("matricula", "matriculados", "ministerio de educacion", "estudiantes por distrito"):
    b = get("py_search_" + re.sub(r"\W+", "_", q) + ".json", "https://www.datos.gov.py/api/3/action/package_search?rows=50&q=" + urllib.parse.quote(q))
    try: res = json.loads(b)["result"]["results"]
    except Exception: continue
    for pkg in res:
        log.write(f"  PKG {pkg.get('name')} | {pkg.get('title')}\n")
        if not re.search(r"matr[ií]cul|alumn|estudiant", (pkg.get("title") or "") + " " + (pkg.get("name") or ""), re.I): continue
        for r in pkg.get("resources", [])[:10]:
            u = r.get("url") or ""
            log.write(f"    RES {r.get('format')} {r.get('name')} {u}\n")
            if re.search(r"csv|xlsx?|zip", (r.get("format") or "") + u, re.I): get("py_" + safe(u), u)
log.close()
