# Temporary: retry of the 728 Philippine searches YouTube refused (403) when four ran at once: one batch, one query each.
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/ph_yt2"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.2 * 3600)}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "PHR"], capture_output=True, text=True, timeout=19500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
