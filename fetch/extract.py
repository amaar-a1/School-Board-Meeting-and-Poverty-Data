# Temporary: run the Canadian board build and save the (small) results.
import json, os, subprocess, sys, time, urllib.request
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "geopandas", "pyogrio"], check=True)
os.makedirs("fetch/out/canada", exist_ok=True)
r = subprocess.run([sys.executable, "fetch/build_canada.py", "/tmp/cawork", "/tmp/caout"], capture_output=True, text=True, timeout=3000)
open("fetch/out/canada/build_log.txt", "w").write(r.stdout[-20000:] + "\n--- stderr ---\n" + r.stderr[-20000:])
if os.path.exists("/tmp/caout/canada.csv"):
    os.replace("/tmp/caout/canada.csv", "fetch/out/canada/canada.csv")
if os.path.exists("/tmp/caout/canada_boards.geojson"):
    subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
    subprocess.run("mapshaper -i /tmp/caout/canada_boards.geojson name=canada -simplify 4% keep-shapes -o fetch/out/canada/canada.json format=topojson quantization=100000", shell=True)
# Look for Ontario and Saskatchewan board borders on their open-data hubs (one polite try each).
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
tries = {
    "ontario_data": "https://data.ontario.ca/api/3/action/package_search?q=%22school%20board%22&rows=10",
    "ontario_geohub": "https://geohub.lio.gov.on.ca/api/search/v1/collections/all/items?q=school%20board&limit=20",
    "sask_geohub": "https://geohub.saskatchewan.ca/api/search/v1/collections/all/items?q=school%20division&limit=20",
    "ontario_agol": "https://www.arcgis.com/sharing/rest/search?f=json&num=30&q=%22school%20board%22%20ontario%20boundary%20type:%22Feature%20Service%22",
    "sask_agol": "https://www.arcgis.com/sharing/rest/search?f=json&num=30&q=%22school%20division%22%20saskatchewan%20type:%22Feature%20Service%22",
}
for name, url in tries.items():
    time.sleep(5)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as resp:
            open(f"fetch/out/canada/search_{name}.json", "wb").write(resp.read())
    except Exception as e:
        open("fetch/out/canada/search_errors.txt", "a").write(f"{name}: {e}\n")
# run 2
