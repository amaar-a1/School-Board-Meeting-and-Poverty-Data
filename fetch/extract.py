# Temporary: mx_yt councils on YouTube.
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/mx_yt"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.2 * 3600), "EXTRA_Q_MX": "ayuntamiento de {} {region} sesión de cabildo"}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "MX:0/2", "MX:1/2"], capture_output=True, text=True, timeout=20500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
