# Round 41: Rwanda EICV7 report files (poverty profile, main indicators, education report) and census 2022 district profiles.
import os, re, urllib.request, urllib.parse, time, http.cookiejar, html
OUT = "fetch/out/c41"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(name, url, keep=True, timeout=600):
    try:
        b = op.open(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%#"), headers=UA), timeout=timeout).read()
        if keep: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
R = "https://statistics.gov.rw"
E = "/data-sources/surveys/EICV/integrated-household-living-conditions-survey-7-eicv-7/"
for tag, p in [("pov", E + "eicv7-poverty-profile-report-202324"), ("main", "/statistical-publications/poverty-and-social-protection/eicv7-main-indicators-report-202324"),
               ("edu", E + "eicv7-thematic-report-education-202324"), ("census", "/fifth-population-and-housing-census-2022/rphc5-district-profiles")]:
    b = get(tag + ".html", R + p)
    s = (b or b"").decode("utf-8", "ignore"); n = 0
    for u in sorted(set(html.unescape(x) for x in re.findall(r'href="([^"]+\.(?:pdf|xlsx?|csv)[^"]*)"', s, re.I))):
        log.write(f"  {tag} FILE {u}\n")
        if n < (3 if tag != "census" else 2): get(f"{tag}_{n}" + os.path.splitext(u.split("?")[0])[1][:5], urllib.parse.urljoin(R, u)); n += 1
log.close()
