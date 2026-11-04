# Temporary: count Nordic and Dutch municipal education-committee meetings on YouTube.
import os, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
os.makedirs("fetch/out/nordic_yt", exist_ok=True)
try:
    r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", "fetch/out/nordic_yt"], capture_output=True, text=True, timeout=19000,
                       env={**os.environ, "NORDIC_DATA": "fetch/nordic"})
    out, err = r.stdout, r.stderr
except subprocess.TimeoutExpired as e:
    out, err = (e.stdout or b"").decode(errors="ignore") if isinstance(e.stdout, bytes) else (e.stdout or ""), "timed out"
open("fetch/out/nordic_yt/youtube_log.txt", "w").write(out[-40000:] + "\n--- stderr ---\n" + err[-5000:])
