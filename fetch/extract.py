# Temporary: Oroncoy's border (spelt "Oronccoy" in geoBoundaries gbHumanitarian PER ADM3, from IGN).
import json, os, subprocess, urllib.request
OUT = "fetch/out/pe_oroncoy2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(u, t=600):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
subprocess.run("npm install -g mapshaper@0.6 >/dev/null 2>&1", shell=True)
meta = json.loads(get("https://www.geoboundaries.org/api/current/gbHumanitarian/PER/ADM3/"))
open("/tmp/per3.geojson", "wb").write(get(meta["simplifiedGeometryGeoJSON"]))
r = subprocess.run(f"mapshaper -i /tmp/per3.geojson -filter \"shapeName == 'Oronccoy'\" -each \"km2=Math.round(this.area/1e6)\" -o {OUT}/oronccoy.geojson format=geojson precision=0.0001",
                   shell=True, capture_output=True, text=True)
open(f"{OUT}/log.txt", "w").write(r.stdout + r.stderr)
