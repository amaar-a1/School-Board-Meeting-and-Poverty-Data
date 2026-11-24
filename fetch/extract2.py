# Round 35: Indonesia's ministry data portal (Portal Data Kemendikdasmen): dataset lists, APIs, school data site.
import os, re, json, urllib.request, urllib.parse, time, http.cookiejar, html
OUT = "fetch/out/c35"; os.makedirs(OUT, exist_ok=True)
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
B = "https://data.kemendikdasmen.go.id"
pages = {"ds.html": B + "/dataset", "dsstat.html": "https://statistik.data.kemendikdasmen.go.id/dataset/dataset-statistik",
         "ds_q.html": B + "/dataset?q=peserta+didik+kabupaten", "ckan.json": B + "/api/3/action/package_search?q=peserta%20didik&rows=50",
         "ckan2.json": B + "/api/3/action/package_list", "sekolah.html": "https://sekolah.data.kemendikdasmen.go.id/",
         "jendela.html": "https://jendela.data.kemendikdasmen.go.id/", "referensi.html": "https://referensi.data.kemendikdasmen.go.id/"}
for n, u in pages.items():
    b = get(n, u)
    s = (b or b"").decode("utf-8", "ignore")
    for l in sorted(set(html.unescape(x) for x in re.findall(r'(?:href|src)="([^"]+)"', s)))[:120]: log.write(f"  LINK {l}\n")
    # JavaScript bundles: API paths inside them
    for js in sorted(set(re.findall(r'src="([^"]+\.js)"', s)))[:6]:
        jb = get(n + "_" + re.sub(r"\W", "_", js)[-40:] + ".js", urllib.parse.urljoin(u, js), keep=False)
        for a in sorted(set(re.findall(r'["\'`](/?(?:api|v\d)/[^"\'`\s]{3,80})["\'`]', (jb or b"").decode("utf-8", "ignore"))))[:60]: log.write(f"  API {a}\n")
        for a in sorted(set(re.findall(r'https?://[a-z0-9.-]*kemendikdasmen[^"\'`\s]{0,80}', (jb or b"").decode("utf-8", "ignore"))))[:30]: log.write(f"  HOST {a}\n")
log.close()
