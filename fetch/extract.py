# Temporary: world fetch part 4: Germany fixes and pupil indicators.
import json, os, time, urllib.parse, urllib.request
OUT = "fetch/out/w4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, text/csv, */*"}
log = []
def get(url, name=None):
    time.sleep(1.2)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:220]}"); return d
    except Exception as e:
        log.append(f"FAIL {url[:220]}: {e}"); return None
WW = "https://www.wegweiser-kommune.de/data-api/rest"
for t in ("Berlin", "Hamburg", "Weiden", "Dillingen", "Neumarkt", "Regen", "Eisenach"):
    get(f"{WW}/region/list?" + urllib.parse.urlencode({"search": t}), f"de_fix_{t}.json")
for t in ("Schüler", "Schul", "Bildung", "Kinder", "Bevölkerung"):
    get(f"{WW}/indicator/list?" + urllib.parse.urlencode({"search": t}), f"de_ind_{t}.json")
get(f"{WW}/topic/list", "de_topics.json")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
