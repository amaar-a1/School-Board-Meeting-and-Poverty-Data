# Round 40: Rwanda EICV7 (2023/24): survey page, its reports and tables, district poverty.
import os, re, urllib.request, urllib.parse, time, http.cookiejar, html
OUT = "fetch/out/c40"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(name, url, keep=True, timeout=300):
    try:
        b = op.open(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%#"), headers=UA), timeout=timeout).read()
        if keep: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
R = "https://statistics.gov.rw"
seen, n = set(), 0
for name, p in [("eicv7.html", "/data-sources/surveys/EICV/integrated-household-living-conditions-survey-7-eicv-7"),
                ("pov.html", "/statistical-publications/poverty-and-social-protection")]:
    b = get(name, R + p)
    s = (b or b"").decode("utf-8", "ignore")
    for u, t in re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
        t = re.sub(r"<[^>]+>|\s+", " ", html.unescape(t)).strip(); u = html.unescape(u)
        if re.search(r"eicv|poverty|district|thematic|tables|\.(pdf|xlsx?)", u + " " + t, re.I) and "cloudflare" not in u:
            log.write(f"  {name} LINK {t[:90]} | {u[:200]}\n")
            if re.search(r"\.(pdf|xlsx?)(\?|$)", u, re.I) and u not in seen and n < 12 and re.search(r"eicv.?7|2023|2024", u + t, re.I):
                seen.add(u); get(f"f{n}" + os.path.splitext(u.split("?")[0])[1][:5], urllib.parse.urljoin(R, u)); n += 1
log.close()
