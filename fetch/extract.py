# Round 21: India: UDISE+ JavaScript bundles (to find its data API), data.gov.in again, NITI 2021 baseline already fetched.
import os, re, json, urllib.request, urllib.parse, time
OUT = "fetch/out/in21"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(n, u, data=None, hdr=None):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}, data=data), timeout=300).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); log.flush(); return b
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n"); log.flush()
    finally: time.sleep(1.5)
for n, u in [("udise_main.js", "https://udiseplus.gov.in/main-V5QGT5CV.js"), ("udise_dash_main.js", "https://dashboard.udiseplus.gov.in/report2026/static/js/main.5f37f069.js")]:
    b = get(n, u)
    if b:
        t = b.decode("utf-8", "replace")
        hosts = sorted(set(re.findall(r'https?://[a-zA-Z0-9.\-]+(?:/[a-zA-Z0-9_\-./]*)?', t)))
        log.write(f"   urls in {n}: " + " ".join(h for h in hosts if "udise" in h or "api" in h)[:3000] + "\n")
        for m in sorted(set(re.findall(r'["\'`](/?[a-zA-Z0-9_\-]*(?:api|report|district|enrol|getData|dashboard)[a-zA-Z0-9_\-/]*)["\'`]', t)))[:200]: log.write(f"   path {m}\n")
for q in ["district wise enrolment", "UDISE district"]:
    get("dgi_" + re.sub(r"\W", "_", q) + ".html", "https://www.data.gov.in/search?title=" + urllib.parse.quote(q))
get("dgi_api.json", "https://api.data.gov.in/catalog?format=json&title=enrolment%20district&limit=20")
