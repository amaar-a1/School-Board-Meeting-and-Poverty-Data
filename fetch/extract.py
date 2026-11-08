# Temporary: Australian councils' meetings on YouTube (two shards).
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/au_yt"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.2 * 3600)}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "AU:0/3", "AU:1/3", "AU:2/3"], capture_output=True, text=True, timeout=19500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
