# Temporary: Switzerland (BFS tables), microstates (World Bank, Eurostat), parliaments on YouTube.
import json, os, re, subprocess, sys, time, urllib.request
OUT = "fetch/out/ch1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, */*"}
log = []
def get(url, name=None, data=None):
    time.sleep(1.2)
    try:
        h = dict(UA)
        if data: h["Content-Type"] = "application/json"
        d = urllib.request.urlopen(urllib.request.Request(url, headers=h, data=data), timeout=600).read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:200]}"); return d
    except Exception as e:
        body = ""
        try: body = e.read().decode()[:300]
        except Exception: pass
        log.append(f"FAIL {url[:200]}: {e} {body}"); return None
# BFS PxWeb: list every table, keep social assistance and pupils
d = get("https://www.pxweb.bfs.admin.ch/api/v1/de/", "bfs_root.json")
tables = []
if d:
    for x in json.loads(d):
        tables.append(x)
    hits = [x for x in tables if re.search(r"sozialhilfe|lernende|schüler|bildungsinstitution|armut", x.get("text", ""), re.I)]
    json.dump(hits, open(f"{OUT}/bfs_hits.json", "w"), ensure_ascii=False, indent=0)
    for x in hits[:40]:
        get(f"https://www.pxweb.bfs.admin.ch/api/v1/de/{x['id']}/{x['id']}.px", f"bfs_meta_{x['id']}.json")
# Microstates
for ind in ("SE.PRM.ENRL", "SE.SEC.ENRL", "SI.POV.NAHC", "SL.UEM.TOTL.ZS", "SP.POP.TOTL", "SP.POP.0014.TO.ZS"):
    get(f"https://api.worldbank.org/v2/country/LUX;LIE;MCO;AND;SMR;CHE/indicator/{ind}?format=json&per_page=2000&date=2010:2025", f"wb_{ind}.json")
get("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_li02?geo=LU&geo=CH&age=Y_LT18&sinceTimePeriod=2018", "es_lu_ch.json")
get("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_li41?geo=CH01&geo=CH02&geo=CH03&geo=CH04&geo=CH05&geo=CH06&geo=CH07&sinceTimePeriod=2018", "es_ch_regions.json")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
r = subprocess.run([sys.executable, "fetch/islands_youtube.py", f"{OUT}/yt", "europe"], capture_output=True, text=True, timeout=12000)
open(f"{OUT}/yt_log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
