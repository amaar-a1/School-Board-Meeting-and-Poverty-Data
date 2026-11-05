# Temporary: list two more island legislature channels.
import json, os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/isl2"; os.makedirs(OUT, exist_ok=True)
res = {}
for url in ("https://www.youtube.com/channel/UCSrOT5JzaIXcr1btNC9LaTQ", "https://www.youtube.com/channel/UCnSUlj13EVE449biHplmLlw"):
    vids = []
    for tab in ("/videos", "/streams"):
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", url + tab], capture_output=True, text=True, timeout=900)
        if r.returncode == 0: vids += [e.get("title") or "" for e in json.loads(r.stdout).get("entries") or []]
        time.sleep(1)
    res[url] = vids
json.dump(res, open(f"{OUT}/titles.json", "w"), ensure_ascii=False)
