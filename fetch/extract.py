# Temporary: count UK council education committee meetings on YouTube.
import os, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
os.makedirs("fetch/out/uk", exist_ok=True)
r = subprocess.run([sys.executable, "fetch/uk_youtube.py", "fetch/uk.csv", "fetch/out/uk/uk_youtube.csv"], capture_output=True, text=True, timeout=14000)
open("fetch/out/uk/youtube_log.txt", "w").write(r.stdout[-30000:] + "\n--- stderr ---\n" + r.stderr[-5000:])
