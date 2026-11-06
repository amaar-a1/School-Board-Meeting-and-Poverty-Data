# Temporary: Spanish municipal councils (5,000+ people) on YouTube.
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/es_yt"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.2 * 3600), "EXTRA_Q_ES": "{} pleno municipal {region}"}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "ES:0/2", "ES:1/2"], capture_output=True, text=True, timeout=20500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
