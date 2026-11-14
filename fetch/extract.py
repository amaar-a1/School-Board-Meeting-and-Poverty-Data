# Temporary: (1) New Zealand regional and unitary councils' meeting recordings on YouTube; (2) Sweden: Kolada v3 KPIs
# on pupils in independent (fristående) schools by home municipality.
import json, os, re, subprocess, sys, time, urllib.parse, urllib.request
OUT = "fetch/out/nz_se4"; os.makedirs(OUT, exist_ok=True)
try:
    import yt_dlp  # noqa
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
COUNCILS = {"NZ-MWT": ["Horizons Regional Council"], "NZ-TNMW": ["Nelson City Council", "Marlborough District Council"]}
def yt(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "--ignore-errors", "--no-warnings", "--playlist-end", "1500", "-J", *a], capture_output=True, text=True, timeout=300)
    try: return json.loads(r.stdout) or {}
    except Exception: return {"_err": r.stderr[-300:]}
res = {}
for area, names in COUNCILS.items():
    for name in names:
      try:
        s = yt(f"ytsearch15:{name} council meeting")
        if "_err" in s: log.write(f"ERR search {name} {s['_err']}\n"); time.sleep(5); continue
        key = re.sub(r"[^a-z]", "", name.lower().replace("council", ""))
        KNOWN = {"Horizons Regional Council": "UCiOz0mER00FtKIvF0hAbB0Q", "Nelson City Council": "UCl2tDcl2hHFL_cx2f-Q-eQQ", "Marlborough District Council": "UCI0cwLPcK77Rvb8w0ljwd_Q"}
        chans = {}
        for e in [x for x in (s.get("entries") or []) if x]:
            ch = (e.get("channel") or e.get("uploader") or ""); cid = e.get("channel_id")
            if cid and key[:10] in re.sub(r"[^a-z]", "", ch.lower()) and not re.search(r"universit|college|school", ch, re.I): chans[cid] = ch
        chans = {k: v for k, v in chans.items() if "MA " not in v and "WMCT" not in v}   # Marlborough, Massachusetts
        if name in KNOWN: chans.setdefault(KNOWN[name], name)
        log.write(f"{area} {name}: channels {chans}\n"); log.flush()
        titles = []
        for cid in list(chans)[:2]:
            for tab in ("videos", "streams"):
                try: d = yt(f"https://www.youtube.com/channel/{cid}/{tab}")
                except subprocess.TimeoutExpired: log.write(f"   timeout {cid} {tab}\n"); continue
                titles += [(e.get("title") or "", e.get("upload_date") or "", e.get("id")) for e in (d.get("entries") or []) if e]
                time.sleep(3)
        res.setdefault(area, []).append({"council": name, "channels": chans, "titles": titles})
        log.write(f"   {len(titles)} videos; sample {[t[0] for t in titles[:8]]}\n"); log.flush()
        json.dump(res, open(f"{OUT}/nz_council_videos.json", "w"), ensure_ascii=False)
        time.sleep(5)
      except Exception as ex: log.write(f"ERR {name} {ex!r}\n"); log.flush()
json.dump(res, open(f"{OUT}/nz_council_videos.json", "w"), ensure_ascii=False)
log.close()

# v2

# v3

# v4
