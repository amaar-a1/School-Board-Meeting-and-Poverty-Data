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
# Find the 2021 Census tables by census subdivision on www150 (titles via the WDS API).
ids = [98100002] + list(range(98100021, 98100031))
meta = json.loads(urllib.request.urlopen(urllib.request.Request("https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata", data=json.dumps([{"productId": i} for i in ids]).encode(), headers={**UA, "Content-Type": "application/json"}), timeout=120).read())
titles = {m["object"]["productId"]: m["object"]["cubeTitleEn"] for m in meta if m.get("status") == "SUCCESS"}
log.write("titles " + json.dumps(titles) + "\n")
age_id = 98100022
log.write(f"age table {age_id}\n")
def table(pid):
    z = zipfile.ZipFile(fetch(f"https://www150.statcan.gc.ca/n1/tbl/csv/{pid}-eng.zip", f"{W}/{pid}.zip"))
    nm = [n for n in z.namelist() if not n.endswith("MetaData.csv")][0]
    rd = csv.reader(io.TextIOWrapper(z.open(nm), encoding="utf-8-sig")); head = next(rd)
    log.write(f"{pid} head {head}\n")
    return rd, head, {h: i for i, h in enumerate(head)}
pop, kids, land = {}, {}, {}
rd, head, col = table(age_id)
age = [h for h in head if h.startswith("Age")][0]; val = [h for h in head if "Total - Gender" in h][0]
cy = [h for h in head if h.startswith("Census year")]
want = {str(a) for a in range(5, 18)}
for r in rd:
    if len(r) < len(head): continue
    dg = r[col["DGUID"]]
    if dg[4:9] != "A0005" or (cy and not r[col[cy[0]]].startswith("2021")): continue
    try: v = float(r[col[val]])
    except ValueError: continue
    a = r[col[age]].strip(); u = dg[-7:]
    if a.startswith("Total"): pop[u] = v
    elif a in want: kids[u] = kids.get(u, 0) + v
# Land area (98-10-0002-01, population and dwelling counts)
rd, head, col = table(98100002)
for r in rd:
    if len(r) < len(head): continue
    dg = r[col["DGUID"]]
    if dg[4:9] != "A0005": continue
    for h in head:
        if "land area" in h.lower() and "2021" in h:
            try: land[dg[-7:]] = float(r[col[h]])
            except ValueError: pass
        if h.endswith("Population, 2021 [1]") and dg[-7:] not in pop:
            try: pop[dg[-7:]] = float(r[col[h]])
            except ValueError: pass
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
json.dump({"boards": boards, "fn": fn, "source": "Statistics Canada, 2021 Census tables by census subdivision (age in single years; population and dwelling counts 98-10-0002-01); 2021 CSD cartographic boundaries"}, open(f"{OUT}/canada_pop.json", "w"), indent=0)
log.write(f"boards with pop {len(boards)}; fn {len(fn)}, with kids {sum(1 for x in fn.values() if x['kids_5_17'])}\n"); log.close()
# rerun 1794264999

# rerun 2

# rerun 3

# rerun 4

# rerun 5

# rerun 6
