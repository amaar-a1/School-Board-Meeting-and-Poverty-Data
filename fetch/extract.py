# Temporary: Canadian boards' population and land area, and First Nations reserves' children 5-17 (2021 Census).
import csv, io, json, os, subprocess, sys, urllib.request, zipfile
try:
    import geopandas as gpd
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "geopandas", "pyogrio"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
OUT = "fetch/out/ca_pop1"; os.makedirs(OUT, exist_ok=True); W = "/tmp/ca"; os.makedirs(W, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def fetch(u, p):
    if not os.path.exists(p):
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=900) as r, open(p, "wb") as f: f.write(r.read())
    return p
# Census Profile 2021, census subdivisions (98-401-X2021006): population, ages 5-17, land area.
zp = fetch("https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=006", f"{W}/prof.zip")
z = zipfile.ZipFile(zp); log.write("zip " + json.dumps(z.namelist()) + "\n")
pop, kids, land = {}, {}, {}
seen = {}
for name in [n for n in z.namelist() if n.lower().endswith(".csv") and "geo_starting_row" not in n.lower()]:
    rd = csv.reader(io.TextIOWrapper(z.open(name), encoding="latin-1")); head = next(rd); col = {h: i for i, h in enumerate(head)}
    log.write(f"{name} head {head[:16]}\n")
    for r in rd:
        if len(r) < len(head): continue
        dg = r[col["DGUID"]]
        if dg[4:9] != "A0005": continue
        cid = int(r[col["CHARACTERISTIC_ID"]]); nm = r[col["CHARACTERISTIC_NAME"]].strip()
        if cid > 40: continue
        try: v = float(r[col["C1_COUNT_TOTAL"]])
        except ValueError: continue
        u = dg[-7:]
        if len(seen) < 45: seen.setdefault(cid, nm)
        if cid == 1: pop[u] = v
        elif nm.startswith("Land area"): land[u] = v
        elif nm in ("5 to 9 years", "10 to 14 years", "15", "16", "17"): kids[u] = kids.get(u, 0) + v
log.write("chars " + json.dumps(seen) + "\n")
log.write(f"CSDs pop {len(pop)} kids {len(kids)} land {len(land)}\n")
csd = gpd.read_file("zip://" + fetch("https://github.com/amaar-a1/School-Board-Meeting-and-Poverty-Data/releases/download/statcan-csd-2021/lcsd000b21a_e.zip", f"{W}/csd.zip")).to_crs(3347)
csd["geometry"] = csd.geometry.make_valid().buffer(0); csd["area"] = csd.geometry.area
csd["pop"] = csd.CSDUID.map(lambda u: pop.get(u, 0))
b = gpd.read_file("fetch/in/canada_boards.topojson").set_crs(4326, allow_override=True).to_crs(3347)
b["geometry"] = b.geometry.make_valid().buffer(0)
log.write(f"boards {len(b)} cols {list(b.columns)}\n")
inter = gpd.overlay(csd[["CSDUID", "pop", "area", "geometry"]], b[["id", "geometry"]], how="intersection", keep_geom_type=True)
inter["share"] = inter.geometry.area / inter["area"]
inter["land"] = inter.geometry.area / 1e6
# Wood Buffalo: almost everyone lives in Fort McMurray (as in build_canada.py)
agg = inter.assign(p=inter["pop"] * inter.share).groupby("id")[["p", "land"]].sum()
boards = {i: {"pop": round(r.p), "land_km2": round(r.land, 1)} for i, r in agg.iterrows()}
fn = {}
for f in json.load(open("fetch/in/canada_fn.geojson"))["features"]:
    i = f["properties"]["id"]; u = i[-7:]
    sub = csd[csd.CSDUID == u]
    fn[i] = {"csd": u, "pop": pop.get(u), "kids_5_17": kids.get(u), "land_km2": land.get(u) or (round(float(sub.area.sum()) / 1e6, 2) if len(sub) else None)}
json.dump({"boards": boards, "fn": fn, "source": "Statistics Canada, Census Profile 2021, census subdivisions (98-401-X2021006); 2021 CSD cartographic boundaries"}, open(f"{OUT}/canada_pop.json", "w"), indent=0)
log.write(f"boards with pop {len(boards)}; fn {len(fn)}, with kids {sum(1 for x in fn.values() if x['kids_5_17'])}\n"); log.close()
# rerun 1794264999

# rerun 2

# rerun 3

# rerun 4
