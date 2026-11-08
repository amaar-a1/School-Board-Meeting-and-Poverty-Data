# Temporary: the remaining small islands and territories: GISCO borders, CBS tables on the Caribbean Netherlands,
# and YouTube searches for each place's council or legislature (with the full video list of matching channels).
import json, os, re, subprocess, sys, traceback, urllib.parse, urllib.request
OUT = "fetch/out/isl2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
try:
    g = json.loads(get("https://gisco-services.ec.europa.eu/distribution/v2/countries/geojson/CNTR_RG_01M_2024_4326.geojson"))
    keep = [f for f in g["features"] if f["properties"].get("CNTR_ID") in ("BQ", "CX", "CC", "GI", "PN", "TK", "SJ", "NZ")]
    json.dump({"type": "FeatureCollection", "features": keep}, open(f"{OUT}/gisco_isl.geojson", "w"))
    log.write(f"gisco {[f['properties'].get('CNTR_ID') for f in keep]}\n")
    if not any(f["properties"].get("CNTR_ID") == "BQ" for f in keep):
        log.write("ids sample " + str(sorted({f['properties'].get('CNTR_ID') for f in g['features']}))[:3000] + "\n")
except Exception: log.write(traceback.format_exc()[-800:])
try:
    cat = json.loads(get("https://opendata.cbs.nl/ODataCatalog/Tables?$format=json&$filter=" + urllib.parse.quote("substringof('Caribisch',Title)")))
    json.dump([{k: t.get(k) for k in ("Identifier", "Title", "Period", "Modified")} for t in cat["value"]], open(f"{OUT}/cbs_catalog.json", "w"), indent=0, ensure_ascii=False)
    log.write(f"cbs {len(cat['value'])}\n")
except Exception: log.write(traceback.format_exc()[-800:])
log.flush()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
Q = {"BON": ["eilandsraad Bonaire vergadering", "Island Council Bonaire meeting", "Bonaire eilandsraad openbare vergadering"],
     "STA": ["Statia Island Council meeting", "Sint Eustatius Island Council public meeting"],
     "SAB": ["Saba Island Council meeting", "Saba Island Council public meeting"],
     "CXR": ["Shire of Christmas Island council meeting", "Christmas Island shire ordinary council meeting"],
     "CCK": ["Shire of Cocos Keeling Islands council meeting"],
     "GIB": ["Gibraltar Parliament session", "Gibraltar Parliament budget debate", "GBC Parliament live Gibraltar"],
     "SJM": ["Longyearbyen lokalstyre møte", "Longyearbyen lokalstyre"],
     "CHT": ["Chatham Islands Council meeting"],
     "PCN": ["Pitcairn Island Council meeting"],
     "TKL": ["General Fono Tokelau", "Tokelau General Fono meeting"]}
PLACE = {"BON": r"bonaire|bon\b|oob", "STA": r"statia|eustatius", "SAB": r"saba", "CXR": r"christmas", "CCK": r"cocos",
         "GIB": r"gibraltar|gbc", "SJM": r"longyearbyen|svalbard", "CHT": r"chatham", "PCN": r"pitcairn", "TKL": r"tokelau"}
res = {}
for k, qs in Q.items():
    res[k] = {"search": [], "channels": {}}
    for q in qs:
        try:
            r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"ytsearch40:{q}"], capture_output=True, text=True, timeout=300)
            for e in json.loads(r.stdout).get("entries", []):
                res[k]["search"].append([q, e.get("channel"), e.get("channel_id"), e.get("title")])
        except Exception as e: log.write(f"{k} {q} ERR {str(e)[:100]}\n")
    chans = {cid: name for _, name, cid, _ in res[k]["search"] if cid and name and re.search(PLACE[k], name, re.I)}
    for cid, name in list(chans.items())[:6]:
        try:
            r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"https://www.youtube.com/channel/{cid}/videos"], capture_output=True, text=True, timeout=600)
            res[k]["channels"][cid] = {"name": name, "titles": [e.get("title") for e in json.loads(r.stdout).get("entries", [])]}
            r = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"https://www.youtube.com/channel/{cid}/streams"], capture_output=True, text=True, timeout=600)
            if r.stdout: res[k]["channels"][cid]["streams"] = [e.get("title") for e in json.loads(r.stdout).get("entries", [])]
        except Exception as e: log.write(f"{k} {cid} ERR {str(e)[:100]}\n")
    log.write(f"{k}: {len(res[k]['search'])} results, channels {list(chans.values())}\n"); log.flush()
    json.dump(res, open(f"{OUT}/yt.json", "w"), ensure_ascii=False)
log.close()
