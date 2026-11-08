# Temporary: Philippine city and municipal councils' sessions on YouTube (four shards).
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/ph_yt"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.2 * 3600), "EXTRA_Q_PH": "Sangguniang Panlungsod {} {region} session"}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "PH:0/4", "PH:1/4", "PH:2/4", "PH:3/4"], capture_output=True, text=True, timeout=19500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
