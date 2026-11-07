# Temporary: first-level region borders (geoBoundaries ADM1) for Finland and the Netherlands, to give each
# municipality its region (maakunta / provincie) for the site's region menu.
import json, os, time, urllib.request
OUT = "fetch/out/adm1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for c in ("FIN", "NLD"):
    u = f"https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/{c}/ADM1/geoBoundaries-{c}-ADM1_simplified.geojson"
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r: b = r.read()
            g = json.loads(b); open(f"{OUT}/gb_{c}_ADM1.geojson", "wb").write(b)
            log.write(f"{c}: {len(b)} bytes, {len(g['features'])} features: {sorted(f['properties']['shapeName'] for f in g['features'])}\n"); break
        except Exception as e:
            log.write(f"{c} try {a}: {e}\n"); time.sleep(20)
log.close()
