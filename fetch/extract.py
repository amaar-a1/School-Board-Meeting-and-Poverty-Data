# Temporary: is there room for Oroncoy (La Mar, Ayacucho, Peru)? Compare the old district borders of La Mar with the
# newer ones (geoBoundaries gbHumanitarian PER ADM3, from IGN): area in the old ones the newer ones don't cover.
import json, os, subprocess, time, traceback, urllib.request
OUT = "fetch/out/pe_oroncoy"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=600):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True); return f"$ {cmd[:200]}\n{r.stdout[-2500:]}{r.stderr[-2500:]}"
try:
    log.write(run("npm install -g mapshaper@0.6 >/dev/null 2>&1; mapshaper -v") + "\n")
    meta = json.loads(get("https://www.geoboundaries.org/api/current/gbHumanitarian/PER/ADM3/"))
    open("/tmp/per3.geojson", "wb").write(get(meta["gjDownloadURL"]))   # full resolution
    log.write(f"source {meta.get('boundarySource')} {meta.get('boundaryYearRepresented')}\n")
    log.write(run("mapshaper -i fetch/pe_lamar_old.geojson -dissolve -o /tmp/old_union.json format=geojson"))
    # newer districts whose interior point lies in La Mar's old area
    log.write(run("mapshaper -i /tmp/per3.geojson -clip /tmp/old_union.json -each 'a=this.area' -filter 'a > 1e6' -o /tmp/new_in.json format=geojson"))
    g = json.load(open("/tmp/new_in.json"))
    log.write("newer districts overlapping La Mar: " + ", ".join(sorted({f['properties'].get('shapeName', '') for f in g['features']})) + "\n")
    log.write(run("mapshaper -i /tmp/new_in.json -dissolve -o /tmp/new_union.json format=geojson"))
    log.write(run("mapshaper -i /tmp/old_union.json -erase /tmp/new_union.json -explode -each 'km2=Math.round(this.area/1e6)' -filter 'km2 >= 5' "
                  f"-o {OUT}/gap.geojson format=geojson precision=0.0001"))
    gap = json.load(open(f"{OUT}/gap.geojson"))
    log.write(f"gaps of 5+ km2: {[f['properties'] for f in gap['features']]}\n")
except Exception:
    log.write(traceback.format_exc()[-1500:])
log.close()
