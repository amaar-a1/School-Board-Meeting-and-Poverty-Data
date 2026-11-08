# Temporary: Polish council sessions on YouTube, every gmina (four shards in parallel).
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/pl_yt"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.3 * 3600), "EXTRA_Q_PL": "{} sesja rady gminy|{} sesja rady miejskiej"}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "PL:0/4", "PL:1/4", "PL:2/4", "PL:3/4"], capture_output=True, text=True, timeout=20500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
