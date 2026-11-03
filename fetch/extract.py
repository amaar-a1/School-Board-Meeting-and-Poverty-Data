# Temporary: run the Canadian board build, then count board meetings on YouTube.
import os, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "geopandas", "pyogrio", "yt-dlp"], check=True)
os.environ["PATH"] = os.path.expanduser("~/.local/bin") + os.pathsep + os.environ["PATH"]
os.makedirs("fetch/out/canada", exist_ok=True)
r = subprocess.run([sys.executable, "fetch/build_canada.py", "/tmp/cawork", "/tmp/caout"], capture_output=True, text=True, timeout=3600)
open("fetch/out/canada/build_log.txt", "w").write(r.stdout[-20000:] + "\n--- stderr ---\n" + r.stderr[-20000:])
if os.path.exists("/tmp/caout/canada.csv"):
    os.replace("/tmp/caout/canada.csv", "fetch/out/canada/canada.csv")
if os.path.exists("/tmp/caout/canada_boards.geojson"):
    subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
    subprocess.run("mapshaper -i /tmp/caout/canada_boards.geojson name=canada -simplify 4% keep-shapes -o fetch/out/canada/canada.json format=topojson quantization=100000", shell=True)
try:
    r = subprocess.run([sys.executable, "fetch/canada_youtube.py", "fetch/out/canada/canada.csv", "fetch/out/canada/canada_youtube.csv"],
                       capture_output=True, text=True, timeout=12000)
    open("fetch/out/canada/youtube_log.txt", "w").write(r.stdout[-30000:] + "\n--- stderr ---\n" + r.stderr[-10000:])
except subprocess.TimeoutExpired as e:
    open("fetch/out/canada/youtube_log.txt", "w").write("timed out\n" + str(e.stdout)[-30000:])
