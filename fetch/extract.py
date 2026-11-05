# Temporary: poverty or unemployment figures for Saint-Barthélemy and Saint-Martin (IEDOM).
import os, re, time, urllib.request
OUT = "fetch/out/gap1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
log = []
def get(url, name):
    time.sleep(1.5)
    try:
        d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        open(f"{OUT}/{name}", "wb").write(d); log.append(f"ok {len(d)} {url}"); return d
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None
for slug in ("saint-martin", "saint-barthelemy"):
    d = get(f"https://www.iedom.fr/{slug}/", f"iedom_{slug}.html")
    if d:
        links = sorted(set(re.findall(rb'href="([^"]+\.pdf)"', d)))
        open(f"{OUT}/iedom_{slug}_pdfs.txt", "wb").write(b"\n".join(links))
        for l in [x for x in links if re.search(rb"rapport|ra_|annuel|panorama|tableau", x, re.I)][:3]:
            u = l.decode()
            if u.startswith("/"): u = "https://www.iedom.fr" + u
            get(u, f"{slug}_{os.path.basename(u)[:60]}")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
