# Round 58: Dutch municipal changes from CBS: the "gemeentelijke indelingen per jaar" page and the files it links
# (each year's municipalities, and the list of mergers), saved with the page.
import os, re, json, urllib.request, urllib.parse, time, html, gzip, shutil
OUT = "fetch/out/c58"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=300):
    try:
        b = urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%#;,+"), headers=UA), timeout=timeout).read()
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url}\n")
    finally: log.flush(); time.sleep(1.5)
pages = ["https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/overig/gemeentelijke-indelingen-per-jaar",
         "https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/overig/gemeentelijke-indelingen-per-jaar/indeling-per-jaar",
         "https://www.cbs.nl/nl-nl/onze-diensten/methoden/classificaties/overig/gemeentelijke-herindelingen"]
seen = set()
for i, p in enumerate(pages):
    b = get(f"nl_page_{i}.html", p)
    if not b: continue
    for l in sorted(set(urllib.parse.urljoin(p, html.unescape(x)) for x in re.findall(r'href="([^"]+)"', b.decode("utf-8", "ignore")))):
        if "cbs.nl" not in l: continue
        log.write(f"  link {l}\n")
        if re.search(r"\.(xlsx?|csv|zip)(\?|$)", l, re.I) and l not in seen and re.search(r"indeling|herindel|gemeente", l, re.I):
            seen.add(l); get("nl_" + os.path.basename(urllib.parse.urlparse(l).path)[-90:], l)
        elif re.search(r"gemeentelijke-indelingen-per-jaar/|herindel", l, re.I) and l not in pages and len(pages) < 25:
            pages.append(l)
for f in os.listdir(OUT):
    p = f"{OUT}/{f}"
    if os.path.getsize(p) > 50e6 and not f.endswith(".gz"):
        with open(p, "rb") as a, gzip.open(p + ".gz", "wb") as b2: shutil.copyfileobj(a, b2)
        os.remove(p)
log.close()
