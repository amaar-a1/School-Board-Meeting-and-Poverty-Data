# Temporary: br_yt_a councils on YouTube.
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/br_yt_a"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.2 * 3600), "EXTRA_Q_BR": "câmara municipal de {} {region} sessão ordinária"}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "BR:0/6", "BR:1/6", "BR:2/6"], capture_output=True, text=True, timeout=20500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
