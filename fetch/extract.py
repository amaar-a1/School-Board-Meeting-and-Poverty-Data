# Temporary: first run of the monthly refresh (data-prep/refresh_youtube.py from claude/features-and-gaps).
import os, shutil, subprocess, sys
subprocess.run("git fetch -q origin claude/features-and-gaps && git checkout FETCH_HEAD -- data-prep", shell=True, check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp", "openpyxl"], check=True)
os.makedirs("fetch/out/refresh", exist_ok=True)
r = subprocess.run([sys.executable, "data-prep/refresh_youtube.py"], capture_output=True, text=True, timeout=19000)
open("fetch/out/refresh/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
shutil.copy("data-prep/inputs/youtube_titles.json", "fetch/out/refresh/youtube_titles.json")
subprocess.run("git checkout HEAD -- data-prep 2>/dev/null; git rm -rq --cached data-prep 2>/dev/null; rm -rf data-prep", shell=True)
