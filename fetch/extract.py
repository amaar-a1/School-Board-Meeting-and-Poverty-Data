# Temporary: Ireland (local authority boundaries, Census 2022 economic status, ETB YouTube channels).
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request
OUT = "fetch/out/ie"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "*/*"}
log = []
def get(url, name=None):
    time.sleep(2)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url} -> {name}"); return d
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None
def esri(url, name):
    feats, off = [], 0
    while True:
        d = get(f"{url}/query?where=1%3D1&outFields=*&outSR=4326&f=geojson&resultOffset={off}&resultRecordCount=200&maxAllowableOffset=0.002")
        if not d: break
        j = json.loads(d); feats += j.get("features", [])
        if len(j.get("features", [])) < 200: break
        off += 200
    json.dump({"type": "FeatureCollection", "features": feats}, open(f"{OUT}/{name}", "w"))
    log.append(f"{name}: {len(feats)} features")
# Local authority boundaries (31): search ArcGIS for Tailte Eireann / CSO local authority boundaries
d = get("https://www.arcgis.com/sharing/rest/search?" + urllib.parse.urlencode({"q": "Local Authority Boundaries Ireland Tailte Eireann", "f": "json", "num": 20}))
cands = [(r["title"], r["owner"], r["url"]) for r in (json.loads(d)["results"] if d else []) if r["type"] == "Feature Service" and r.get("url")]
json.dump(cands, open(f"{OUT}/la_search.json", "w"), indent=1)
for t, o, u in cands:
    if re.search(r"local authorit", t, re.I) and not re.search(r"electoral area|lea", t, re.I):
        esri(u.rstrip("/") + "/0", "ie_local_authorities.geojson"); log.append(f"LA layer: {t} ({o})"); break
# Census 2022: population aged 15+ by principal economic status (SAP theme 8.1), find the county / local authority version
d = get("https://data.gov.ie/api/3/action/package_search?" + urllib.parse.urlencode({"q": "SAP2022T8T1", "rows": 30}))
if d:
    res = json.loads(d)["result"]["results"]
    json.dump([(p["title"], p["name"], [(r.get("format"), r.get("url")) for r in p["resources"]][:3]) for p in res], open(f"{OUT}/sap_search.json", "w"), indent=1)
    for p in res:
        code = p["title"].split(" ")[0]
        if code.startswith("SAP2022T8T1") and re.search(r"(CTY|COUNTY|LA|ADM)", code[11:]) and "LEA" not in code:
            get(f"https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/{code}/CSV/1.0/en", f"ie_{code}.csv")
    get("https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/SAP2022T8T1LEA22/CSV/1.0/en", "ie_SAP2022T8T1LEA22.csv")
# ETB YouTube channels and board meetings
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
def yt(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=600)
    return json.loads(r.stdout) if r.returncode == 0 else {}
ETBS = ["City of Dublin ETB", "Dublin and Dun Laoghaire ETB", "Cavan and Monaghan ETB", "Cork ETB", "Donegal ETB", "Galway and Roscommon ETB",
        "Kerry ETB", "Kildare and Wicklow ETB", "Kilkenny and Carlow ETB", "Laois and Offaly ETB", "Limerick and Clare ETB", "Longford and Westmeath ETB",
        "Louth and Meath ETB", "Mayo Sligo and Leitrim ETB", "Tipperary ETB", "Waterford and Wexford ETB"]
res = {}
for e in ETBS:
    chans = {}
    for q in (f"{e} board meeting", f"{e} Education and Training Board"):
        for v in yt(f"ytsearch10:{q}").get("entries") or []:
            if v.get("channel_url"): chans[v["channel_url"]] = v.get("channel")
        time.sleep(1)
    key = [w for w in re.findall(r"[a-z]+", e.lower()) if w not in ("and", "etb", "of", "city")]
    pick = [(u, c) for u, c in chans.items() if c and ("etb" in c.lower() or "education and training" in c.lower()) and all(k[:5] in c.lower() for k in key[:1])]
    info = {"candidates": chans, "picked": pick[:1]}
    if pick:
        titles = [x.get("title") for x in (yt(pick[0][0] + "/videos").get("entries") or [])]
        info["meeting_titles"] = [t for t in titles if t and re.search(r"board meeting|meeting of the board|board of", t, re.I)]
        info["n_videos"] = len(titles)
    res[e] = info
json.dump(res, open(f"{OUT}/etb_youtube.json", "w"), indent=1, ensure_ascii=False)
open(f"{OUT}/log.txt", "w").write("\n".join(log))
