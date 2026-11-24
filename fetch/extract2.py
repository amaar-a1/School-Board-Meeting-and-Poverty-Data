# Round 34: real enrollment by district: India (data.gov.in), Indonesia (Kemendikdasmen statistics), Paraguay (datos.gov.py).
import os, re, json, urllib.request, urllib.parse, time, http.cookiejar, html
OUT = "fetch/out/c34"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(name, url, keep=True, limit=150e6, timeout=120):
    try:
        b = op.open(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if keep and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n   {b[:200]!r}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
def links(b, pat):
    s = (b or b"").decode("utf-8", "ignore")
    return sorted(set(html.unescape(u) for u in re.findall(r'(?:href|src)="([^"]+)"', s) if re.search(pat, u, re.I)))
# India
for n, u in [("in_dgi_search.html", "https://www.data.gov.in/search?title=udise%20district"),
             ("in_dgi_api.json", "https://www.data.gov.in/backend/dms/v1/ogdp/catalog/search?query=udise%20enrolment%20district&format=json"),
             ("in_dgi_cat.html", "https://www.data.gov.in/catalog/unified-district-information-system-education-plus-udise"),
             ("in_udise_reports.html", "https://udiseplus.gov.in/#/en/publication")]:
    b = get(n, u)
    for l in links(b, r"\.(csv|xlsx?|pdf|json)(\?|$)|resource|catalog")[:40]: log.write(f"  LINK {l}\n")
# Indonesia
for n, u in [("id_stat_home.html", "https://statistik.data.kemendikdasmen.go.id/"), ("id_stat_old.html", "https://statistik.data.kemdikbud.go.id/"),
             ("id_pub.html", "https://statistik.data.kemendikdasmen.go.id/index.php/page/publikasi"), ("id_data_home.html", "https://data.kemendikdasmen.go.id/"),
             ("id_pdsp.html", "https://pdsp.kemendikdasmen.go.id/"), ("id_satudata.html", "https://satudata.kemendikdasmen.go.id/")]:
    b = get(n, u)
    for l in links(b, r"\.(pdf|xlsx?|csv)(\?|$)|publikasi|statistik|download|unduh")[:60]: log.write(f"  LINK {l}\n")
# Paraguay
for n, u in [("py_dgp_api.json", "https://www.datos.gov.py/api/3/action/package_search?q=matricula&rows=50"),
             ("py_dgp_api2.json", "https://www.datos.gov.py/api/3/action/package_search?q=ministerio%20de%20educacion&rows=50"),
             ("py_dgp_home.html", "https://www.datos.gov.py/")]:
    b = get(n, u)
# HDX
pk = {}
for q in ["india school enrolment district udise", "indonesia number of students district", "paraguay matricula escolar", "paraguay education district"]:
    b = get("hdx_" + re.sub(r"\W+", "_", q) + ".json", "https://data.humdata.org/api/3/action/package_search?rows=15&q=" + urllib.parse.quote(q), keep=False)
    try:
        for p in json.loads(b)["result"]["results"]:
            pk[p["name"]] = {"title": p["title"], "res": [(r["name"], r.get("format"), r.get("size"), r["url"]) for r in p["resources"]][:10]}
    except Exception: pass
json.dump(pk, open(f"{OUT}/hdx.json", "w"), indent=1)
log.close()
