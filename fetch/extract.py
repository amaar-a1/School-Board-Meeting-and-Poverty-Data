# Temporary: INSEE page the user linked (poverty data for Saint-Pierre-et-Miquelon).
import os, re, html, time, urllib.request
OUT = "fetch/out/insee"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
log = []
for name, url in [("en", "https://www.insee.fr/en/statistiques/7758862?geo=BV2022-58264"),
                  ("fr", "https://www.insee.fr/fr/statistiques/7758862?geo=BV2022-58264")]:
    time.sleep(3)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
            h = r.read().decode("utf-8", "replace")
        open(f"{OUT}/{name}.html", "w").write(h)
        t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", re.sub(r"(?s)<(script|style).*?</\1>", " ", h))))
        open(f"{OUT}/{name}.txt", "w").write(t)
        log.append(f"ok {len(h)} {url}")
    except Exception as e:
        log.append(f"FAIL {url}: {e}")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
