# Temporary: rerun the Canadian board build (shapes for every board).
import os, subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "geopandas", "pyogrio"], check=True)
os.makedirs("fetch/out/canada", exist_ok=True)
r = subprocess.run([sys.executable, "fetch/build_canada.py", "/tmp/cawork", "/tmp/caout"], capture_output=True, text=True, timeout=3600)
open("fetch/out/canada/build_log.txt", "w").write(r.stdout[-20000:] + "\n--- stderr ---\n" + r.stderr[-20000:])
if os.path.exists("/tmp/caout/canada.csv"):
    os.replace("/tmp/caout/canada.csv", "fetch/out/canada/canada.csv")
if os.path.exists("/tmp/caout/canada_boards.geojson"):
    subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
    subprocess.run("mapshaper -i /tmp/caout/canada_boards.geojson name=canada -simplify 4% keep-shapes -o fetch/out/canada/canada.json format=topojson quantization=100000", shell=True)
# run rest
# run rest 2
# run rest 3
