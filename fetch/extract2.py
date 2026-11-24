# Round 37: probing official sources for the next countries (published pages and open-data APIs only).
import os, re, json, urllib.request, urllib.parse, time, http.cookiejar, html
OUT = "fetch/out/c37"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(name, url, keep=True, limit=80e6, timeout=120):
    try:
        b = op.open(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if keep and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
def links(name, b, pat):
    s = (b or b"").decode("utf-8", "ignore")
    for u, t in re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
        t = re.sub(r"<[^>]+>|\s+", " ", html.unescape(t)).strip()
        if re.search(pat, u + " " + t, re.I): log.write(f"  {name} LINK {t[:100]} | {html.unescape(u)[:200]}\n")
P = [("rw_eicv7.html", "https://www.statistics.gov.rw/publication/eicv7-poverty-profile-report", r"\.(xlsx?|pdf)|district|table"),
     ("rw_stats.html", "https://www.statistics.gov.rw/statistical-publications/subject/household-surveys-%28eicv%29", r"eicv"),
     ("lk_dcs.html", "http://www.statistics.gov.lk/Poverty/StaticalInformation", r"\.(xlsx?|pdf|csv)|DS|divisional"),
     ("lk_dcs2.html", "http://www.statistics.gov.lk/Poverty/StaticalInformation/PovertyIndicators-DSDivision", r"\.(xlsx?|pdf|csv)"),
     ("bd_bbs.html", "https://bbs.gov.bd/site/page/d1e4e6b5-4f8e-4e0a-9c7d-7e4e4e8e4e8e", r"poverty|map"),
     ("bd_wb.html", "https://www.worldbank.org/en/news/press-release/2024/11/24/bangladesh-poverty-maps", r"\.(xlsx?|pdf)|map"),
     ("cz_mpsv.html", "https://data.mpsv.cz/web/data/vypisy-dat", r"hmotn|davk|živob|zivob"),
     ("cz_mpsv_api.json", "https://data.mpsv.cz/od/soubory/", r""),
     ("mn_open.html", "https://opendata.1212.mn/en/", r"pover|ядуу"),
     ("bo_ine.html", "https://www.ine.gob.bo/index.php/censos-y-banco-de-datos/censos/", r"nbi|pobreza|municip"),
     ("do_one.html", "https://www.one.gob.do/datos-y-estadisticas/", r"pobreza|mapa")]
for n, u, pat in P:
    b = get(n, u)
    if pat: links(n, b, pat)
pk = {}
for q in ["rwanda district poverty eicv", "sri lanka poverty headcount ds division", "bangladesh poverty map 2022 upazila", "czech municipality social benefits",
          "mongolia soum poverty", "bolivia municipal poverty nbi", "dominican republic municipal poverty map"]:
    b = get("hdx.json", "https://data.humdata.org/api/3/action/package_search?rows=12&q=" + urllib.parse.quote(q), keep=False)
    try:
        for p in json.loads(b)["result"]["results"]:
            pk[p["name"]] = {"q": q, "title": p["title"], "res": [(r["name"], r.get("format"), r.get("size"), r["url"]) for r in p["resources"]][:8]}
    except Exception: pass
json.dump(pk, open(f"{OUT}/hdx.json", "w"), indent=1)
log.close()
