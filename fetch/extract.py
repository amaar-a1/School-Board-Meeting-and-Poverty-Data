# Temporary: (1) which current commune each orphaned French border piece (an old commune merged into another) lies in,
# from geo.api.gouv.fr; (2) borders of municipalities still missing from the map (Mexico, Spain) from OpenStreetMap
# (Overpass API), searched within their state or province.
import json, os, subprocess, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/gaps1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=180, data=None):
    err = None
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA, data=data), timeout=t) as r: return r.read()
        except Exception as e:
            err = e; time.sleep(5 + 10 * a)
    raise err
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1200:]}\n\n")
    log.flush()

def orphans():
    pts = json.load(open("fetch/fr_orphans.json")); res = {}; miss = []
    for p in pts:
        try:
            d = json.loads(get(f"https://geo.api.gouv.fr/communes?lat={p['lat']}&lon={p['lon']}&fields=code,nom", 60))
            if d: res[p["code"]] = {"code": d[0]["code"], "nom": d[0]["nom"]}
            else: miss.append(p["code"])
        except Exception as e:
            miss.append(p["code"])
        time.sleep(0.12)
    json.dump(res, open(f"{OUT}/fr_orphan_to_commune.json", "w"), ensure_ascii=False)
    return f"{len(res)} of {len(pts)} placed; not placed: {miss[:30]}"
step("France: orphaned pieces -> current commune", orphans)

subprocess.run("npm install -g osmtogeojson >/dev/null 2>&1", shell=True)
WANT = [("MX-17034", "Coatetelco", "MX-MOR", 6), ("MX-07125", "Honduras de la Sierra", "MX-CHP", 6), ("MX-17036", "Hueyapan", "MX-MOR", 6),
        ("MX-02006", "San Quintín", "MX-BCN", 6), ("MX-04012", "Seybaplaya", "MX-CAM", 6), ("MX-17035", "Xoxocotla", "MX-MOR", 6),
        ("ES-41904", "El Palmar de Troya", "ES-SE", 8), ("ES-18077", "Fornes", "ES-GR", 8), ("ES-14901", "Fuente Carreteros", "ES-CO", 8),
        ("ES-14902", "La Guijarrosa", "ES-CO", 8), ("ES-21902", "La Zarza-Perrunal", "ES-H", 8), ("ES-11903", "San Martín del Tesorillo", "ES-CA", 8),
        ("ES-18916", "Torrenueva Costa", "ES-GR", 8), ("ES-48916", "Usansolo", "ES-BI", 8)]
def osm():
    out, feats = [], []
    for did, name, iso, lvl in WANT:
        q = (f'[out:json][timeout:120];area["ISO3166-2"="{iso}"]->.a;'
             f'rel(area.a)["boundary"="administrative"]["admin_level"="{lvl}"]["name"~"^{name}$",i];out geom;')
        try:
            raw = get("https://overpass-api.de/api/interpreter", 240, urllib.parse.urlencode({"data": q}).encode())
            open("/tmp/o.json", "wb").write(raw)
            r = subprocess.run("osmtogeojson /tmp/o.json", shell=True, capture_output=True, text=True)
            g = json.loads(r.stdout)
            polys = [f for f in g["features"] if f["geometry"]["type"] in ("Polygon", "MultiPolygon")]
            for f in polys:
                f["properties"] = {"id": did, "NAME": name, "osm": f["properties"].get("id"), "osm_name": f["properties"].get("name") or f["properties"].get("tags", {}).get("name")}
            feats += polys[:1]
            out.append(f"{did} {name}: {len(polys)} polygon(s) {[p['properties']['osm'] for p in polys]}")
        except Exception as e:
            out.append(f"{did} {name}: ERR {str(e)[:150]}")
        time.sleep(3)
    json.dump({"type": "FeatureCollection", "features": feats}, open(f"{OUT}/osm_missing.geojson", "w"), ensure_ascii=False)
    return "\n".join(out)
step("OpenStreetMap: missing municipalities", osm)
log.close()
