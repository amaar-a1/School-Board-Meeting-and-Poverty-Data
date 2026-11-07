# Temporary: (1) the 4 First Nations settlements (CSDTYPE "S-É") missed for an encoding mix-up; (2) look for borders
# of municipalities missing from the map in geoBoundaries' humanitarian and authoritative collections.
import json, os, re, subprocess, time, traceback, unicodedata, urllib.request, zipfile
OUT = "fetch/out/ca_reserves3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=900):
    err = None
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
        except Exception as e:
            err = e; time.sleep(10)
    raise err
def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True); return f"$ {cmd[:160]}\n{r.stdout[-1500:]}{r.stderr[-1500:]}"
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1200:]}\n\n")
    log.flush()
log.write(run("npm install -g mapshaper@0.6 >/dev/null 2>&1; mapshaper -v") + "\n")

def settlements():
    open("/tmp/csd.zip", "wb").write(get("https://github.com/amaar-a1/School-Board-Meeting-and-Poverty-Data/releases/download/statcan-csd-2021/lcsd000b21a_e.zip"))
    zipfile.ZipFile("/tmp/csd.zip").extractall("/tmp/csd")
    shp = [os.path.join(dp, f) for dp, _, fs in os.walk("/tmp/csd") for f in fs if f.endswith(".shp")][0]
    out = [run(f"mapshaper -i {shp} encoding=latin1 -filter \"(PRUID == '35' || PRUID == '48') && CSDTYPE.indexOf('S-') === 0\" -proj wgs84 "
               f"-join fetch/ca_rest.geojson point-method fields=id -filter \"id == 'CA-ON-REST' || id == 'CA-AB-REST'\" "
               f"-each \"area_km2 = Math.round(this.area / 1e5) / 10\" -simplify 4% keep-shapes -o {OUT}/ca_rest_settlements.geojson format=geojson precision=0.0001")]
    g = json.load(open(f"{OUT}/ca_rest_settlements.geojson"))
    out.append("; ".join(f"{f['properties']['CSDNAME']} ({f['properties']['CSDTYPE']}, {f['properties']['id']})" for f in g["features"]))
    return "\n".join(out)
step("Canada: First Nations settlements", settlements)

def norm(s):
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())
def borders():
    miss = json.load(open("fetch/missing_borders.json"))
    out = []
    for cc, iso, adm in (("PE", "PER", "ADM3"), ("MX", "MEX", "ADM2"), ("ES", "ESP", "ADM3"), ("ES", "ESP", "ADM4")):
        for coll in ("gbHumanitarian", "gbAuthoritative", "gbOpen"):
            try:
                meta = json.loads(get(f"https://www.geoboundaries.org/api/current/{coll}/{iso}/{adm}/", 120))
                u = meta.get("simplifiedGeometryGeoJSON") or meta.get("gjDownloadURL")
                g = json.loads(get(u))
                names = {}
                for f in g["features"]: names.setdefault(norm(f["properties"].get("shapeName")), []).append(f)
                found = [{"id": did, "name": n, "region": reg, "features": names[norm(n)]} for did, n, reg in miss[cc] if norm(n) in names]
                json.dump(found, open(f"{OUT}/new_{cc}_{coll}_{adm}.json", "w"), ensure_ascii=False)
                out.append(f"{cc} {coll} {adm}: year {meta.get('boundaryYearRepresented')} ({str(meta.get('boundarySource'))[:80]}), {len(g['features'])} features; "
                           f"{len(found)} of {len(miss[cc])} missing found by name: {[x['name'] for x in found][:20]}")
            except Exception as e:
                out.append(f"{cc} {coll} {adm}: {str(e)[:120]}")
    return "\n".join(out)
step("Borders for municipalities missing from the map", borders)
log.close()
