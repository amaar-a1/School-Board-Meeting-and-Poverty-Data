# Temporary: current borders of 47 French communes formed by recent mergers (geo.api.gouv.fr), missing from the
# older commune borders file.
import json, os, time, traceback, urllib.request
OUT = "fetch/out/fr_new_communes"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
feats = []
for c in json.load(open("fetch/fr_missing_codes.json")):
    try:
        u = f"https://geo.api.gouv.fr/communes?code={c}&format=geojson&geometry=contour&fields=nom,code"
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r: d = json.loads(r.read())
        fs = d.get("features", [])
        feats += fs
        log.write(f"{c}: {len(fs)} feature(s) {[f['properties'].get('nom') for f in fs]}\n")
    except Exception:
        log.write(f"{c}: ERR {traceback.format_exc()[-300:]}\n")
    time.sleep(0.3)
json.dump({"type": "FeatureCollection", "features": feats}, open(f"{OUT}/fr_new_communes.geojson", "w"))
log.write(f"total {len(feats)}\n"); log.close()
