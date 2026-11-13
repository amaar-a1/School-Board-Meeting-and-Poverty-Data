# Temporary: data.gov.ph app bundle: find its data API, then the DepEd dataset's resources.
import json, os, re, urllib.request
OUT = "fetch/out/ph_deped2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
js = get("https://data.gov.ph/index/public/main.28614807276661d4.js").decode("utf-8", "replace")
urls = sorted(set(re.findall(r'https?://[a-zA-Z0-9./_-]+', js)))
log.write("urls " + json.dumps([u for u in urls if "w3.org" not in u and "angular" not in u][:60]) + "\n")
paths = sorted(set(re.findall(r'["`\'](/?(?:api|index|v\d)[a-zA-Z0-9/_${}.-]{2,80})["`\']', js)))
log.write("paths " + json.dumps(paths[:120]) + "\n")
for m in re.finditer(r'.{0,140}(dataset|resource)s?/?\$\{.{0,140}', js):
    log.write("ctx " + m.group(0)[:300] + "\n")
log.close()
