# Temporary: list every video title on the Nordic/Dutch channels that had a loose match, for a strict recount.
import json, os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/nordic_yt2"; os.makedirs(OUT, exist_ok=True)
res = {}
for url in json.load(open("fetch/yt_channels.json")):
    titles = []
    for tab in ("/videos", "/streams"):
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", url + tab], capture_output=True, text=True, timeout=600)
        if r.returncode == 0:
            titles += [e.get("title") or "" for e in json.loads(r.stdout).get("entries") or []]
        time.sleep(1)
    res[url] = titles
    json.dump(res, open(f"{OUT}/titles.json", "w"), ensure_ascii=False)
