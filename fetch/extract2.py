# Round 63: census population, second pass. Sri Lanka: the Department of Census and Statistics' 2012 census pages
# for each district (and its census pages' spreadsheets/PDF tables). Uruguay: INE's 2023 census page and the files
# it links. Ecuador: INEC's population projections by canton (and the files it links).
import os, re, json, urllib.request, urllib.parse, time, html
OUT = "fetch/out/c63"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=180):
    try:
        b = urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%#;,+@~"), headers=UA), timeout=timeout).read()
        if name and len(b) < 45e6: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:160]} {url}\n")
    finally: log.flush(); time.sleep(1.2)
safe = lambda s: re.sub(r"[^\w.-]+", "_", s)[-90:]
def links(page, b):
    return sorted(set(urllib.parse.urljoin(page, html.unescape(x)) for x in re.findall(r'(?:href|src)="([^"]+)"', (b or b"").decode("utf-8", "ignore"))))
def crawl(tag, p, pat, follow=None, maxdl=25):
    b = get(f"{tag}_page_{safe(urllib.parse.urlparse(p).path or 'home')}.html", p); n = 0
    for l in links(p, b):
        if re.search(r"\.(xlsx?|csv|zip|pdf)(\?|$)", l, re.I):
            log.write(f"  {tag} LINK {l}\n")
            if n < maxdl and re.search(pat, l, re.I): n += 1; get(f"{tag}_" + safe(os.path.basename(urllib.parse.urlparse(l).path)), l)
        elif follow and re.search(follow, l, re.I): log.write(f"  {tag} page-link {l}\n")
    return b
# Sri Lanka
base = "http://www.statistics.gov.lk/Population/StaticalInformation/CPH2011"
for d in ["Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "NuwaraEliya", "Galle", "Matara", "Hambanthota", "Jaffna", "Mannar", "Vavuniya", "Mulativu",
          "Kilinochchi", "Batticaloa", "Ampara", "Trincomalee", "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla", "Monaragala", "Ratnapura", "Kegalle"]:
    crawl("lka_" + d, f"{base}/{d}", r"pop|table|t[0-9]|cph", maxdl=4)
crawl("lka_final", f"{base}/CensusPopulationHousing2012-FinalReport", r".", maxdl=10)
crawl("lka_2024", "https://www.statistics.gov.lk/Censuses", r"census|pop|2024|2012", follow=r"census|2024", maxdl=10)
# Uruguay
crawl("ury", "https://www.ine.gub.uy/instituto-nacional-estadistica/censos2023pvh", r"pobla|depart|censo|resultado", follow=r"censo|resultado|2023", maxdl=20)
# Ecuador
crawl("ecu", "https://www.ecuadorencifras.gob.ec/proyecciones-poblacionales/", r"proyecc|canton|cant", maxdl=10)
log.close()
