# Round 38: Sri Lanka (DCS poverty by DS division, census 2024), Czechia (MPSV open data), Rwanda (NISR).
import os, re, json, urllib.request, urllib.parse, time, http.cookiejar, html
OUT = "fetch/out/c38"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(name, url, keep=True, limit=120e6, timeout=180):
    try:
        b = op.open(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%#"), headers=UA), timeout=timeout).read()
        if keep and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
def files(base, b, pat, name, maxn=8):
    s = (b or b"").decode("utf-8", "ignore"); n = 0
    for u in sorted(set(html.unescape(x) for x in re.findall(r'(?:href|src)="([^"]+)"', s))):
        if re.search(pat, u, re.I):
            log.write(f"  {name} FILE {u}\n")
            if n < maxn: get(f"{name}_{n}" + os.path.splitext(u.split("?")[0])[1][:6], urllib.parse.urljoin(base, u)); n += 1
for n, u in [("lk_dsp", "https://www.statistics.gov.lk/Poverty/StaticalInformation/PovertyStatisticsDSDivision"),
             ("lk_pi19", "https://www.statistics.gov.lk/Poverty/StaticalInformation/PovertyIndicators-2019"),
             ("lk_cph", "https://www.statistics.gov.lk/Population/StaticalInformation/CPH2024"),
             ("lk_codes", "https://www.statistics.gov.lk/qlink/AdminDivCode")]:
    b = get(n + ".html", u)
    files(u, b, r"\.(pdf|xlsx?|csv)(\?|$)", n)
for d in ["nezamestnanost-v-obcich/", "skoly/", "catalog/"]:
    b = get("cz_" + d.strip("/") + ".html", "https://data.mpsv.cz/od/soubory/" + d)
    s = (b or b"").decode("utf-8", "ignore")
    for x in re.findall(r'href="([^"]+)"', s): log.write(f"  cz {d} {x}\n")
for n, u in [("rw1.html", "https://statistics.gov.rw/publication/eicv7-poverty-profile-report"), ("rw2.html", "http://www.statistics.gov.rw/"),
             ("rw3.html", "https://statistics.gov.rw/")]:
    b = get(n, u)
    files(u, b, r"eicv.*\.(pdf|xlsx?)|poverty.*\.(pdf|xlsx?)", n, 4)
log.close()
