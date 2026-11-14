# Temporary: (1) New Zealand regional and unitary councils' meeting recordings on YouTube; (2) Sweden: Kolada v3 KPIs
# on pupils in independent (fristående) schools by home municipality.
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request
OUT = "fetch/out/nz_se2"; os.makedirs(OUT, exist_ok=True)
try:
    import yt_dlp  # noqa
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
for q in ["fristående grundskola folkbokförda", "fristående grundskola hemkommun", "elever fristående andel"]:
    try:
        d = json.loads(get("https://api.kolada.se/v3/kpi?title=" + urllib.parse.quote(q)))
        for k in d.get("values", [])[:40]: log.write(f"SE kpi {k['id']} | {k['title']}\n")
    except Exception as e: log.write(f"ERR SE {q} {e}\n")
COUNCILS = {"NZ-NTL": ["Northland Regional Council"], "NZ-AUK": ["Auckland Council"], "NZ-WKO": ["Waikato Regional Council"],
            "NZ-BOP": ["Bay of Plenty Regional Council"], "NZ-GIS-HKB": ["Gisborne District Council", "Hawke's Bay Regional Council"],
            "NZ-TKI": ["Taranaki Regional Council"], "NZ-MWT": ["Horizons Regional Council"], "NZ-WGN": ["Greater Wellington Regional Council"],
            "NZ-TNMW": ["Tasman District Council", "Nelson City Council", "Marlborough District Council", "West Coast Regional Council"],
            "NZ-CAN": ["Environment Canterbury"], "NZ-OTA": ["Otago Regional Council"], "NZ-STL": ["Environment Southland"]}
def yt(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "--ignore-errors", "--no-warnings", "--playlist-end", "1500", "-J", *a], capture_output=True, text=True, timeout=300)
    try: return json.loads(r.stdout)
    except Exception: return {"_err": r.stderr[-300:]}
res = {}
for area, names in COUNCILS.items():
    for name in names:
        s = yt(f"ytsearch15:{name} council meeting")
        if "_err" in s: log.write(f"ERR search {name} {s['_err']}\n"); time.sleep(5); continue
        key = re.sub(r"[^a-z]", "", name.lower().replace("council", ""))
        chans = {}
        for e in s.get("entries", []):
            ch = (e.get("channel") or e.get("uploader") or ""); cid = e.get("channel_id")
            if cid and key[:10] in re.sub(r"[^a-z]", "", ch.lower()) and not re.search(r"universit|college|school", ch, re.I): chans[cid] = ch
        log.write(f"{area} {name}: channels {chans}\n")
        titles = []
        for cid in list(chans)[:2]:
            for tab in ("videos", "streams"):
                try: d = yt(f"https://www.youtube.com/channel/{cid}/{tab}")
                except subprocess.TimeoutExpired: log.write(f"   timeout {cid} {tab}\n"); continue
                titles += [(e.get("title") or "", e.get("upload_date") or "", e.get("id")) for e in d.get("entries", []) or []]
                time.sleep(3)
        res.setdefault(area, []).append({"council": name, "channels": chans, "titles": titles})
        log.write(f"   {len(titles)} videos; sample {[t[0] for t in titles[:8]]}\n"); log.flush()
        json.dump(res, open(f"{OUT}/nz_council_videos.json", "w"), ensure_ascii=False)
        time.sleep(5)
json.dump(res, open(f"{OUT}/nz_council_videos.json", "w"), ensure_ascii=False)
log.close()

# v2
