# Temporary: inspect Ontario's official school board boundary file; search again for Saskatchewan.
import json, os, subprocess, sys, time, urllib.request, zipfile
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "geopandas", "pyogrio"], check=True)
import geopandas as gpd, pyogrio
os.makedirs("fetch/out/canada", exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
out = []
try:
    urllib.request.urlretrieve("https://ws.gisetl.lrc.gov.on.ca/fmedatadownload/Packages/SchoolBoardBoundaries.zip", "/tmp/on.zip")
    z = zipfile.ZipFile("/tmp/on.zip"); out.append(str([(i.filename, i.file_size) for i in z.infolist()]))
    z.extractall("/tmp/on")
    for root, _, files in os.walk("/tmp/on"):
        for f in files:
            p = os.path.join(root, f)
            if f.lower().endswith((".shp", ".gdb", ".gpkg")) or root.lower().endswith(".gdb"):
                src = root if root.lower().endswith(".gdb") else p
                for lyr in pyogrio.list_layers(src):
                    g = gpd.read_file(src, layer=lyr[0])
                    out.append(f"{src} {lyr} n={len(g)} crs={g.crs}\n{g.drop(columns='geometry').head(80).to_string()[:12000]}")
                if root.lower().endswith(".gdb"): break
            elif f.lower().endswith((".txt", ".xml", ".csv")) and os.path.getsize(p) < 200000:
                out.append(f"--- {p}\n" + open(p, errors="replace").read()[:3000])
except Exception as e:
    out.append(f"ontario error: {e!r}")
for name, url in {
    "sask_agol2": "https://www.arcgis.com/sharing/rest/search?f=json&num=30&q=saskatchewan%20%22school%20divisions%22",
    "sask_agol3": "https://www.arcgis.com/sharing/rest/search?f=json&num=30&q=saskatchewan%20school%20division%20boundaries",
}.items():
    time.sleep(5)
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120))
        out.append(name + "\n" + "\n".join(f" - {i['title'][:70]} | {i['owner']} | {i['type']} | {i.get('url')}" for i in d.get("results", [])))
    except Exception as e:
        out.append(f"{name} error {e}")
open("fetch/out/canada/ontario_inspect.txt", "w").write("\n\n".join(out))
