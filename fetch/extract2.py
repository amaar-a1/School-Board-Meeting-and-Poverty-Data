# Round 64: Sri Lanka's 2012 census final report (gzipped: over 100 MB) and the 2024 census page and its files.
import os, re, urllib.request, urllib.parse, time, html, gzip
OUT = "fetch/out/c64"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=600, gz=False):
    try:
        b = urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%#;,+@~"), headers=UA), timeout=timeout).read()
        if name:
            if gz: gzip.open(f"{OUT}/{name}.gz", "wb").write(b)
            elif len(b) < 45e6: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:160]} {url}\n")
    finally: log.flush(); time.sleep(1.2)
get("lka_2012_final.pdf", "https://www.statistics.gov.lk/Resource/en/Population/CPH_2011/CensusPopulationHousing2012-FinalReport.pdf", gz=True)
p = "https://www.statistics.gov.lk/Population/StaticalInformation/CPH2024"
b = get("lka_2024_page.html", p)
for l in sorted(set(urllib.parse.urljoin(p, html.unescape(x)) for x in re.findall(r'(?:href|src)="([^"]+)"', (b or b"").decode("utf-8", "ignore")))):
    if re.search(r"\.(xlsx?|csv|pdf)(\?|$)", l, re.I):
        log.write(f"  LINK {l}\n")
        if re.search(r"pop|prelim|district|census|report", l, re.I): get("lka_2024_" + re.sub(r"[^\w.-]+", "_", os.path.basename(urllib.parse.urlparse(l).path))[-80:], l, gz=True)
log.close()
