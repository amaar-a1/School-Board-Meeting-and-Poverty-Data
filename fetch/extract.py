# Temporary: simplified borders for Chile (comunas) and Colombia (municipios, departamentos).
import json, os, subprocess, urllib.request
OUT = "fetch/out/clph4"; os.makedirs(OUT, exist_ok=True)
subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research script)"}
for iso, lvl, src in (("CHL", "ADM3", "fetch/out/clph1/gb_CHL_ADM3_simplified.geojson"), ("COL", "ADM2", "fetch/out/clph2/gb_COL_ADM2_simplified.geojson"), ("COL", "ADM1", None)):
    if src is None:
        j = json.loads(urllib.request.urlopen(urllib.request.Request(f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/{lvl}/", headers=UA), timeout=120).read())
        src = f"/tmp/{iso}_{lvl}.geojson"
        open(src, "wb").write(urllib.request.urlopen(urllib.request.Request(j["simplifiedGeometryGeoJSON"], headers=UA), timeout=300).read())
    pct = "8%" if lvl != "ADM1" else "5%"
    subprocess.run(f"mapshaper -i {src} -simplify {pct} keep-shapes -o {OUT}/{iso}_{lvl}.geojson precision=0.0001", shell=True)
