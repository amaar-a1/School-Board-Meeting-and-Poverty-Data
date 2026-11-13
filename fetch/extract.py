# Temporary: DepEd historical enrollment on data.gov.ph: find and fetch its resources.
import json, os, re, urllib.parse, urllib.request, html
OUT = "fetch/out/ph_deped1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read(), r.headers.get("Content-Type", "")
page = "https://data.gov.ph/index/public/dataset/Historical%20Enrollment%20Data/l6xdlzdg-ixdr-yuve-tw7k-0cgug0ceul10"
try:
    b, ct = get(page); t = b.decode("utf-8", "replace"); open(f"{OUT}/page.html", "w").write(t)
    links = sorted(set(html.unescape(x) for x in re.findall(r'(?:href|src|data-url)="([^"]+)"', t)))
    log.write(f"page {len(t)} {ct}\n" + "\n".join(l for l in links if re.search(r"download|resource|\.csv|\.xlsx?|api|storage", l, re.I)) + "\n")
    log.write("API-like: " + json.dumps(sorted(set(re.findall(r'["\'](/[a-z_/]*api[^"\']{0,120})["\']', t)))[:30]) + "\n")
except Exception as e: log.write(f"ERR page {e}\n")
log.close()
