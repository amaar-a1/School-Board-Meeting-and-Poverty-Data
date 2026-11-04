# Temporary: islands' legislatures on YouTube.
import os, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
r = subprocess.run([sys.executable, "fetch/islands_youtube.py", "fetch/out/isl1"], capture_output=True, text=True, timeout=15000)
open("fetch/out/isl1/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
