# Temporary: Iceland part 5: YouTube again, with correct names and a second query.
import os, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
OUT = "fetch/out/is5"; os.makedirs(OUT, exist_ok=True)
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", f"{OUT}/yt", "IS"], capture_output=True, text=True, timeout=12000,
                   env={**os.environ, "NORDIC_DATA": "fetch/is", "EXTRA_Q_IS": "{} sveitarstjórnarfundur|{} fundur bæjarstjórnar"})
open(f"{OUT}/yt_log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
