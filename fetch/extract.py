# Temporary: Switzerland part 2: BFS table titles (themes 13 and 15), parliaments on YouTube.
import json, os, subprocess, sys, time, urllib.request
OUT = "fetch/out/ch2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json"}
root = json.load(open("fetch/out/ch1/bfs_root.json"))
titles = {}
for x in root:
    i = x["dbid"]
    if not (i.startswith("px-x-13") or i.startswith("px-x-15")): continue
    try:
        m = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://www.pxweb.bfs.admin.ch/api/v1/de/{i}/{i}.px", headers=UA), timeout=120).read())
        titles[i] = {"title": m.get("title"), "vars": [(v["code"], v["text"], v["valueTexts"][:6], len(v["values"])) for v in m["variables"]]}
    except Exception as e:
        titles[i] = {"error": str(e)[:100]}
    time.sleep(0.7)
json.dump(titles, open(f"{OUT}/bfs_titles.json", "w"), ensure_ascii=False, indent=0)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
r = subprocess.run([sys.executable, "fetch/islands_youtube.py", f"{OUT}/yt", "europe"], capture_output=True, text=True, timeout=12000)
open(f"{OUT}/yt_log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
