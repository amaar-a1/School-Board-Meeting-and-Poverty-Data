# Round 30: Indonesia children and population by regency (WorldPop R2025A 2025, 1 km, summed over geoBoundaries ADM2);
# Indonesia's school census (Dapodik) at its 2025 address; third-country probes (Thailand, Kazakhstan, Mongolia, Paraguay, Ghana).
import os, json, subprocess, sys, zipfile, urllib.request, urllib.parse, time, http.cookiejar
OUT = "fetch/out/c30"; os.makedirs(OUT, exist_ok=True)
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
    get("id_dapo_nat.json", "https://dapo.kemendikdasmen.go.id/rekap/progres?id_level_wilayah=0&kode_wilayah=000000&semester_id=20251")
    get("id_dapo_home.html", "https://dapo.kemendikdasmen.go.id/")
    get("th_nesdc.html", "https://www.nesdc.go.th/main.php?filename=PovertyData")
    get("th_nesdc_en.html", "https://www.nesdc.go.th/nesdb_en/main.php?filename=social_dev_report")
    get("kz_taldau.json", "https://taldau.stat.gov.kz/ru/Api/GetIndexData/703974?period=7&dics=67")
    get("kz_stat.html", "https://stat.gov.kz/en/industries/labor-and-income/stat-life/")
    get("mn_1212.html", "https://www.1212.mn/en/statistic/statcate/573054/table-view/DT_NSO_0600_031V1")
    get("py_ine.html", "https://www.ine.gov.py/vt/publicacion.php?publicacion=2")
    get("gh_mpi.html", "https://statsghana.gov.gh/gssmain/fileUpload/pressrelease/2021%20PHC%20Multidimensional%20Poverty%20Report.pdf", keep=False)
try:
    import numpy, rasterio
except ImportError:
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", "rasterio", "numpy"], capture_output=True, text=True)
    say("pip", r.returncode); log.close(); os.execv(sys.executable, [sys.executable] + sys.argv)
import numpy as np, rasterio
from rasterio import features
URL = "https://data.worldpop.org/GIS/AgeSex_structures/Global_2015_2030/R2025A/2025/IDN/v1/1km_ua/idn_agesex_structures_2025_CN_1km_R2025A_UA_v1.zip"
z = "/tmp/idn.zip"
with urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=1800) as r, open(z, "wb") as f:
    while True:
        b = r.read(1 << 22)
        if not b: break
        f.write(b)
zf = zipfile.ZipFile(z); names = zf.namelist()
geo = json.load(open("fetch/out/c29/id_gb_ADM2.geojson", encoding="utf-8"))
ids = [f["properties"]["shapeID"] for f in geo["features"]]
res = {i: {} for i in ids}
lab = None
for grp in ["00", "01"] + [f"{a:02d}" for a in range(5, 85, 5)]:
    for sex in ("f", "m"):
        n = next((x for x in names if f"_{sex}_{grp}_" in x.lower() and x.endswith(".tif")), None)
        if not n: say("missing", sex, grp); continue
        p = zf.extract(n, "/tmp/wp")
        with rasterio.open(p) as src:
            a = src.read(1).astype("float64"); a[(a < 0) | ~np.isfinite(a)] = 0
            if src.nodata is not None: a[a == src.nodata] = 0
            if lab is None:
                shapes = [(f["geometry"], k + 1) for k, f in enumerate(geo["features"])]
                lab = features.rasterize(shapes, out_shape=a.shape, transform=src.transform, fill=0, dtype="int32")
                lab2 = features.rasterize(shapes, out_shape=a.shape, transform=src.transform, fill=0, dtype="int32", all_touched=True)
                lab = np.where(lab == 0, lab2, lab)
            s = np.bincount(lab.ravel(), weights=a.ravel(), minlength=len(ids) + 1)
            for k, i in enumerate(ids): res[i][f"{sex}{grp}"] = round(float(s[k + 1]), 1)
            say(n, "total", round(float(s[1:].sum())), "outside", round(float(s[0])))
        os.remove(p)
json.dump({"source": URL, "districts": res}, open(f"{OUT}/idn_ages_2025.json", "w"), indent=0)
say("done", len(res))
