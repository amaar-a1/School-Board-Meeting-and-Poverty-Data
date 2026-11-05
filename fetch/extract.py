# Temporary: IEDOM Guadeloupe publications (Saint-Martin and Saint-Barthélemy reports).
import os, re, time, urllib.request
OUT = "fetch/out/gap3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
log = []
def get(url, name=None):
    time.sleep(1.5)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180); d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {r.geturl()} <- {url}"); return d, r.geturl()
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None, url
_, base = get("https://www.iedom.fr/saint-martin/")
log.append("base " + base)
pages = [urllib.request.urljoin(base, x) for x in ("Publications", "Statistiques")]
found = set()
for u in pages:
    d, final = get(u, re.sub(r"\W+", "_", u)[-40:] + ".html")
    if not d: continue
    for l in re.findall(rb'href="([^"]+)"', d):
        l = l.decode(errors="ignore")
        if re.search(r"saint-martin|saint-barth|st-martin|st-barth|rapport", l, re.I): found.add(urllib.request.urljoin(final, l))
open(f"{OUT}/links.txt", "w").write("\n".join(sorted(found)))
for l in sorted(found):
    if re.search(r"(saint|st)-(martin|barth)", l, re.I) and len([x for x in os.listdir(OUT) if x.endswith(".pdf") or x.endswith(".bin")]) < 6:
        d, final = get(l)
        if d and d[:4] == b"%PDF": open(f"{OUT}/{re.sub(r'\W+', '_', l)[-50:]}.pdf", "wb").write(d)
        elif d:
            for p in re.findall(rb'href="([^"]+\.pdf)"', d)[:4]:
                pu = urllib.request.urljoin(final, p.decode(errors="ignore"))
                d2, _ = get(pu)
                if d2 and d2[:4] == b"%PDF": open(f"{OUT}/{re.sub(r'\W+', '_', pu)[-50:]}.pdf", "wb").write(d2)
open(f"{OUT}/log.txt", "w").write("\n".join(log))
