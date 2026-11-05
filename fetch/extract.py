# Temporary: Chilean and Colombian municipal councils on YouTube.
import os, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/lat_yt"; os.makedirs(OUT, exist_ok=True)
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "CL", "CO"], capture_output=True, text=True, timeout=20000,
                   env={**os.environ, "NORDIC_DATA": "fetch/lat", "EXTRA_Q_CL": "municipalidad de {} concejo", "EXTRA_Q_CO": "concejo municipal {} plenaria"})
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
