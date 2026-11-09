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
# Ages by CSD (98-10-0020-01): total population and children 5-17, both genders.
z = zipfile.ZipFile(fetch("https://www150.statcan.gc.ca/n1/tbl/csv/98100020-eng.zip", f"{W}/age.zip"))
name = [n for n in z.namelist() if not n.endswith("MetaData.csv")][0]
rd = csv.reader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig")); head = next(rd)
log.write("head " + json.dumps(head) + "\n")
col = {h: i for i, h in enumerate(head)}
age = [h for h in head if h.startswith("Age")][0]
val = [h for h in head if "Total - Gender" in h][0]
cy = [h for h in head if h.startswith("Census year")][0]
log.write(f"age {age} value {val}\n")
pop, kids, ages = {}, {}, set()
want = {f"{a} years" for a in range(5, 18)}
for r in rd:
    if len(r) < len(head): continue
    dg = r[col["DGUID"]]
    if dg[4:9] != "A0005" or not r[col[cy]].startswith("2021"): continue
    a = r[col[age]]; ages.add(a)
    try: v = float(r[col[val]])
    except ValueError: continue
    u = dg[-7:]
    if a.startswith("Total"): pop[u] = v
    elif a.split(" (")[0].replace(" year", " years").replace("yearss","years") in want or a in want: kids[u] = kids.get(u, 0) + v
log.write(f"ages sample {sorted(ages)[:40]}\nCSDs pop {len(pop)} kids {len(kids)}\n")
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
    fn[i] = {"csd": u, "pop": pop.get(u), "kids_5_17": kids.get(u), "land_km2": round(float(sub.area.sum()) / 1e6, 2) if len(sub) else None}
json.dump({"boards": boards, "fn": fn, "source": "Statistics Canada table 98-10-0020-01 (2021 Census, age by CSD); 2021 CSD cartographic boundaries"}, open(f"{OUT}/canada_pop.json", "w"), indent=0)
log.write(f"boards with pop {len(boards)}; fn {len(fn)}, with kids {sum(1 for x in fn.values() if x['kids_5_17'])}\n"); log.close()
# rerun 1794264999

# rerun 2
