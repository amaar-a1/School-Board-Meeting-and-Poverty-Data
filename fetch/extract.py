# Temporary: German district and city councils on YouTube (council and school-committee meetings).
import os, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/de_yt"; os.makedirs(OUT, exist_ok=True)
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT, "DE"], capture_output=True, text=True, timeout=19000,
                   env={**os.environ, "NORDIC_DATA": "fetch/de", "EXTRA_Q_DE": "{} Stadtrat Sitzung|{} Schulausschuss"})
open(f"{OUT}/log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
