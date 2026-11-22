# Round 26: all ages (district population, 2025), as round 25: India school-age children by district: WorldPop R2025A age structures (2025, 1 km, constrained),
# summed over each district border (fetch/in_geo.json, the site's full-detail India districts).
import os, json, subprocess, sys, zipfile, urllib.request
OUT = "fetch/out/in26"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "a")
def say(*a): log.write(" ".join(map(str, a)) + "\n"); log.flush()
try:
    import numpy, rasterio
except ImportError:   # install, then start again so the new packages are on the path
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", "rasterio", "numpy"], capture_output=True, text=True)
    say("pip", r.returncode, r.stdout[-1500:], r.stderr[-1500:]); log.close()
    os.execv(sys.executable, [sys.executable] + sys.argv)
import numpy as np, rasterio
from rasterio import features
URL = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2015_2030/R2025A/2025/IND/v1/1km_ua/ind_agesex_structures_2025_CN_1km_R2025A_UA_v1.zip"
z = "/tmp/ind.zip"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"})
with urllib.request.urlopen(req, timeout=1800) as r, open(z, "wb") as f:
    while True:
        b = r.read(1 << 22)
        if not b: break
        f.write(b)
zf = zipfile.ZipFile(z); names = zf.namelist(); say("files:", names)
geo = json.load(open("fetch/in_geo.json", encoding="utf-8"))
ids = [f["properties"]["id"] for f in geo["features"]]
res = {i: {} for i in ids}
for grp in ["00", "01"] + [f"{a:02d}" for a in range(5, 85, 5)]:
    for sex in ("f", "m"):
        n = next((x for x in names if f"_{sex}_{grp}_" in x.lower() and x.endswith(".tif")), None)
        if not n: say("missing", sex, grp); continue
        p = zf.extract(n, "/tmp/wp")
        with rasterio.open(p) as src:
            a = src.read(1).astype("float64"); a[(a < 0) | ~np.isfinite(a)] = 0
            if src.nodata is not None: a[a == src.nodata] = 0
            if grp == "00" and sex == "f":
                lab = features.rasterize(((f["geometry"], k + 1) for k, f in enumerate(geo["features"])), out_shape=a.shape, transform=src.transform, fill=0, dtype="int32")
                # Coastal cells whose centre is in the sea (Mumbai's, Chennai's): to the district whose border touches them.
                lab2 = features.rasterize(((f["geometry"], k + 1) for k, f in enumerate(geo["features"])), out_shape=a.shape, transform=src.transform, fill=0, dtype="int32", all_touched=True)
                lab = np.where(lab == 0, lab2, lab)
            s = np.bincount(lab.ravel(), weights=a.ravel(), minlength=len(ids) + 1)
            for k, i in enumerate(ids): res[i][f"{sex}{grp}"] = round(float(s[k + 1]), 1)
            say(n, "India total", round(float(s[1:].sum())), "outside districts", round(float(s[0])))
        os.remove(p)
json.dump({"source": URL, "districts": res}, open(f"{OUT}/in_ages_2025.json", "w"), indent=0)
say("done", len(res))
