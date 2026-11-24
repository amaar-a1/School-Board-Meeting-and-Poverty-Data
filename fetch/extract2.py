# Round 42: Rwanda and Sri Lanka: geoBoundaries borders; WorldPop R2025A 2025 ages summed over districts; Sri Lanka MoE statistics page.
import os, re, json, subprocess, sys, zipfile, urllib.request, urllib.parse, time, http.cookiejar
OUT = "fetch/out/c42"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "a")
def say(*a): log.write(" ".join(map(str, a)) + "\n"); log.flush()
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(name, url, keep=True, limit=80e6, timeout=180):
    try:
        b = opener.open(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if keep and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        say(f"OK {name} {len(b)} {url}\n   {b[:300]!r}"); return b
    except Exception as e: say(f"ERR {name} {e} {url}")
    finally: time.sleep(2)
if not os.path.exists(f"{OUT}/.probed"):
    open(f"{OUT}/.probed", "w").write("1")
    for c in ("RWA", "LKA"):
        for a in ("ADM1", "ADM2"):
            get(f"{c.lower()}_gb_{a}.geojson", f"https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/{c}/{a}/geoBoundaries-{c}-{a}_simplified.geojson")
    b = get("lk_moe.html", "https://moe.gov.lk/statistics/")
    import html as H
    for u in sorted(set(H.unescape(x) for x in re.findall(r'href="([^"]+)"', (b or b"").decode("utf-8", "ignore")))):
        if re.search(r"census|statistic|\.pdf|\.xlsx?", u, re.I): say("  lk LINK", u)
try:
    import numpy, rasterio
except ImportError:
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", "rasterio", "numpy"], capture_output=True, text=True)
    say("pip", r.returncode); log.close(); os.execv(sys.executable, [sys.executable] + sys.argv)
import numpy as np, rasterio
from rasterio import features
def run(cc, geo_path, out_name):
    URL = f"https://data.worldpop.org/GIS/AgeSex_structures/Global_2015_2030/R2025A/2025/{cc}/v1/1km_ua/{cc.lower()}_agesex_structures_2025_CN_1km_R2025A_UA_v1.zip"
    z = f"/tmp/{cc}.zip"
    with urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=1800) as r, open(z, "wb") as f:
        while True:
            b = r.read(1 << 22)
            if not b: break
            f.write(b)
    zf = zipfile.ZipFile(z); names = zf.namelist()
    geo = json.load(open(geo_path, encoding="utf-8"))
    ids = [f["properties"]["shapeID"] for f in geo["features"]]
    res = {i: {} for i in ids}; lab = None
    for grp in ["00", "01"] + [f"{a:02d}" for a in range(5, 85, 5)]:
        for sex in ("f", "m"):
            n = next((x for x in names if f"_{sex}_{grp}_" in x.lower() and x.endswith(".tif")), None)
            if not n: say("missing", cc, sex, grp); continue
            p = zf.extract(n, "/tmp/wp")
            with rasterio.open(p) as src:
                a = src.read(1).astype("float64"); a[(a < 0) | ~np.isfinite(a)] = 0
                if src.nodata is not None: a[a == src.nodata] = 0
                if lab is None:
                    shapes = [(f["geometry"], k + 1) for k, f in enumerate(geo["features"])]
                    lab = features.rasterize(shapes, out_shape=a.shape, transform=src.transform, fill=0, dtype="int32")
                    lab2 = features.rasterize(shapes, out_shape=a.shape, transform=src.transform, fill=0, dtype="int32", all_touched=True)
                    lab = np.where(lab == 0, lab2, lab)
                s_ = np.bincount(lab.ravel(), weights=a.ravel(), minlength=len(ids) + 1)
                for k, i in enumerate(ids): res[i][f"{sex}{grp}"] = round(float(s_[k + 1]), 1)
            os.remove(p)
    json.dump({"source": URL, "districts": res}, open(f"{OUT}/{out_name}", "w"), indent=0)
    say("done", cc, len(res))
for cc in ("RWA", "LKA"):
    try: run(cc, f"{OUT}/{cc.lower()}_gb_ADM2.geojson", f"{cc.lower()}_ages_2025.json")
    except Exception as e: say("ERR", cc, e)
