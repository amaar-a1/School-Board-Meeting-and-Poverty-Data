# Temporary: Polish council sessions on YouTube again for the 191 gminy of 30,000+ people (council channels preferred,
# Polish case forms of names), in two shards.
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/pl2_yt"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5 * 3600), "EXTRA_Q_PL2": "Rada Miasta {} sesja|{} sesja rady miejskiej transmisja"}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "PL2:0/2", "PL2:1/2"], capture_output=True, text=True, timeout=19000, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
