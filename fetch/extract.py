# Temporary: French town councils of communes with 2,000-9,999 people on YouTube (four shards in parallel).
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/fr2_yt"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.3 * 3600), "EXTRA_Q_FR2": "{} conseil municipal séance"}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "FR2:0/4", "FR2:1/4", "FR2:2/4", "FR2:3/4"], capture_output=True, text=True, timeout=20500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
