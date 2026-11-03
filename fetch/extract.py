# Temporary: count Canadian board meetings on YouTube (second, third pass).
import os, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
os.environ["PATH"] = os.path.expanduser("~/.local/bin") + os.pathsep + os.environ["PATH"]
try:
    r = subprocess.run([sys.executable, "fetch/canada_youtube.py", "fetch/out/canada/canada.csv", "fetch/out/canada/canada_youtube.csv", "fetch/canada_channels.csv"],
                       capture_output=True, text=True, timeout=14000)
    open("fetch/out/canada/youtube_log.txt", "w").write(r.stdout[-30000:] + "\n--- stderr ---\n" + r.stderr[-10000:])
except subprocess.TimeoutExpired as e:
    open("fetch/out/canada/youtube_log.txt", "w").write("timed out\n" + str(e.stdout)[-30000:])
