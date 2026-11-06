# Temporary: simplified borders for Mexico (municipios, estados) and Brazil (municípios, estados).
import json, os, subprocess, urllib.request
OUT = "fetch/out/mxbr1"; os.makedirs(OUT, exist_ok=True)
subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research script)"}
for iso, lvl, pct in (("MEX", "ADM2", "6%"), ("MEX", "ADM1", "3%"), ("BRA", "ADM2", "4%"), ("BRA", "ADM1", "2%")):
    j = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/{lvl}/", headers=UA), timeout=120).read())
    src = f"/tmp/{iso}_{lvl}.geojson"
    open(src, "wb").write(urllib.request.urlopen(urllib.request.Request(j["simplifiedGeometryGeoJSON"], headers=UA), timeout=600).read())
    subprocess.run(f"mapshaper -i {src} -simplify {pct} keep-shapes -o {OUT}/{iso}_{lvl}.geojson precision=0.0001", shell=True)
    print(iso, lvl, os.path.getsize(f"{OUT}/{iso}_{lvl}.geojson"), flush=True)
