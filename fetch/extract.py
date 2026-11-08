# Temporary: Portuguese and Belgian council sessions on YouTube (Portugal in two shards, Belgium in Dutch and French).
import os, subprocess, sys, time
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/ptbe_yt"; os.makedirs(OUT, exist_ok=True)
env = {**os.environ, "NORDIC_DATA": "fetch/latam", "NORDIC_DEADLINE": str(time.time() + 5.2 * 3600),
       "EXTRA_Q_PT": "reunião de câmara {} {region}|{} assembleia municipal sessão", "EXTRA_Q_BENL": "{} gemeenteraad zitting", "EXTRA_Q_BEFR": "{} conseil communal séance"}
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "PT:0/2", "PT:1/2", "BENL:0/2", "BENL:1/2", "BEFR:0/2", "BEFR:1/2"], capture_output=True, text=True, timeout=19500, env=env)
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
