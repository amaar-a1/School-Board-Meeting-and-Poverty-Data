# Round 61: older and census-only population over time.
# 1. Eurostat GISCO LAU 2011-2015 (each LAU's population and name, where the file has them), to extend Europe's
#    municipal series back before 2016.
# 2. Eurostat's NUTS history (the correspondence tables between NUTS versions), for Germany's district reforms.
# 3. HDX Common Operational Datasets, population statistics (cod-ps-<iso3>), for countries whose site has one year.
import os, re, json, urllib.request, urllib.parse, time, html, gzip, shutil
OUT = "fetch/out/c61"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=600):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url}\n")
    finally: log.flush(); time.sleep(1.5)
# 1
for y in range(2011, 2016):
    b = get(None, f"https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_{y}_4326.geojson", timeout=1200)
    if not b: continue
    try:
        feats = json.loads(b)["features"]; props = feats[0]["properties"]; log.write(f"  LAU {y} props {list(props)}\n")
        out = {}
        for f in feats:
            p = f["properties"]
            pop = next((p[k] for k in p if re.fullmatch(r"POP_?\d{4}|POP", k) and p[k] not in (None, "")), None)
            out.setdefault(p.get("CNTR_CODE"), {})[p.get("GISCO_ID") or p.get("LAU_ID") or p.get("LAU_CODE")] = [pop, p.get("LAU_NAME") or p.get("LAU_LABEL")]
        json.dump(out, open(f"{OUT}/lau_pop_{y}.json", "w")); log.write(f"  LAU {y}: {sum(1 for v in out.values() for x in v.values() if x[0] is not None)} with population\n")
    except Exception as e: log.write(f"  LAU {y} ERR {e}\n")
# 2
p = "https://ec.europa.eu/eurostat/web/nuts/history"
b = get("nuts_history.html", p)
for l in sorted(set(urllib.parse.urljoin(p, html.unescape(x)) for x in re.findall(r'href="([^"]+)"', (b or b"").decode("utf-8", "ignore")))):
    if re.search(r"\.(xlsx?|zip|csv)(\?|$)", l, re.I):
        log.write(f"  link {l}\n"); get("nuts_" + re.sub(r"[^\w.-]+", "_", urllib.parse.urlparse(l).path)[-80:], l)
# 3
for iso in ("ken", "phl", "zaf", "per", "ecu", "cri", "ury", "rwa", "lka", "kor", "isr", "nzl", "irl", "ind", "hrv", "twn", "can"):
    b = get(None, f"https://data.humdata.org/api/3/action/package_show?id=cod-ps-{iso}")
    try: res = json.loads(b)["result"]["resources"]
    except Exception: continue
    for r in res:
        u = r.get("url") or ""
        log.write(f"  {iso} RES {r.get('format')} {r.get('name')} {r.get('size')} {u}\n")
        if re.search(r"csv|xlsx?", (r.get("format") or "") + u, re.I) and (r.get("size") or 0) < 60e6:
            get(f"hdx_{iso}_" + re.sub(r"[^\w.-]+", "_", r.get("name") or os.path.basename(u))[-80:], u)
for f in os.listdir(OUT):
    q = f"{OUT}/{f}"
    if os.path.getsize(q) > 50e6 and not f.endswith(".gz"):
        with open(q, "rb") as a, gzip.open(q + ".gz", "wb") as b2: shutil.copyfileobj(a, b2)
        os.remove(q)
log.close()
