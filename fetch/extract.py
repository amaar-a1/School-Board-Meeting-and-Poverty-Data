# Temporary: (1) First Nations reserves and settlements inside Canada's "Rest of Ontario/Alberta" map areas, from
# the 2021 census subdivision borders (this repo's statcan-csd-2021 release); (2) newer borders for municipalities
# that have none on the map (Peru, Mexico, Spain, Brazil), from geoBoundaries' current releases.
import json, os, re, subprocess, sys, time, traceback, unicodedata, urllib.request
OUT = "fetch/out/ca_reserves"; os.makedirs(OUT, exist_ok=True)
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
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1200:]}\n\n")
    log.flush()
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "geopandas", "pyogrio", "shapely"], capture_output=True)

def reserves():
    import geopandas as gpd
    open("/tmp/csd.zip", "wb").write(get("https://github.com/amaar-a1/School-Board-Meeting-and-Poverty-Data/releases/download/statcan-csd-2021/lcsd000b21a_e.zip"))
    csd = gpd.read_file("zip:///tmp/csd.zip")
    out = [f"columns {list(csd.columns)}; types {csd.CSDTYPE.value_counts().head(20).to_dict()}"]
    csd = csd[csd.PRUID.isin(["35", "48"])].to_crs(3347)
    rest = gpd.read_file("fetch/ca_rest.geojson").to_crs(3347)
    rows = []
    for _, a in rest.iterrows():
        sub = csd[csd.intersects(a.geometry)].copy()
        sub["share"] = sub.geometry.intersection(a.geometry).area / sub.geometry.area
        sub = sub[sub.share >= 0.5]
        sub["rest"] = a["id"]
        rows.append(sub)
        out.append(f"{a['id']}: {len(sub)} subdivisions inside; types {sub.CSDTYPE.value_counts().to_dict()}")
    allc = gpd.GeoDataFrame(__import__("pandas").concat(rows), crs=3347)
    allc["area_km2"] = (allc.geometry.area / 1e6).round(1)
    keep = allc[allc.CSDTYPE.isin(["IRI", "S-É", "TI", "IGD", "NL"])].copy()   # reserves, settlements, other First Nations lands
    keep["geometry"] = keep.geometry.simplify(300)
    keep = keep.to_crs(4326)
    keep[["CSDUID", "CSDNAME", "CSDTYPE", "PRUID", "rest", "area_km2", "share", "geometry"]].to_file(f"{OUT}/ca_rest_first_nations.geojson", driver="GeoJSON")
    others = allc[~allc.index.isin(keep.index)]
    out.append(f"kept {len(keep)} First Nations lands; left in the merged areas: {others.CSDTYPE.value_counts().to_dict()}")
    out.append("sample: " + "; ".join(f"{r.CSDNAME} ({r.CSDTYPE}, {r.area_km2} km²)" for r in keep.head(15).itertuples()))
    return "\n".join(out)
step("Canada: First Nations lands in the Rest-of areas", reserves)

def norm(s):
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())
def borders():
    miss = json.load(open("fetch/missing_borders.json"))
    out = []
    for cc, iso, adm in (("PE", "PER", "ADM3"), ("MX", "MEX", "ADM2"), ("ES", "ESP", "ADM3"), ("BR", "BRA", "ADM2")):
        try:
            meta = json.loads(get(f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/{adm}/", 120))
            u = meta.get("simplifiedGeometryGeoJSON") or meta.get("gjDownloadURL")
            g = json.loads(get(u))
            names = {}
            for f in g["features"]: names.setdefault(norm(f["properties"].get("shapeName")), []).append(f)
            found = []
            for did, n, reg in miss[cc]:
                fs = names.get(norm(n), [])
                if fs: found.append({"id": did, "name": n, "region": reg, "features": fs})
            json.dump(found, open(f"{OUT}/new_{cc}.json", "w"), ensure_ascii=False)
            out.append(f"{cc}: geoBoundaries {meta.get('boundaryYearRepresented')} ({meta.get('boundarySource')}), {len(g['features'])} features; "
                       f"found {len(found)} of {len(miss[cc])} missing by name: {[x['name'] for x in found]}")
        except Exception:
            out.append(f"{cc}: ERR {traceback.format_exc()[-400:]}")
    return "\n".join(out)
step("Newer borders (geoBoundaries current)", borders)
log.close()
