# Temporary: Italian town councils (comuni of 3,000+ people) on YouTube (four shards in parallel).
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/it_yt"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.3 * 3600), "EXTRA_Q_IT": "{} seduta consiglio comunale"}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "IT:0/4", "IT:1/4", "IT:2/4", "IT:3/4"], capture_output=True, text=True, timeout=20500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
