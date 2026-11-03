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
# Ontario board service areas (retry the catalogue politely)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
for attempt in range(4):
    try:
        time.sleep(30)
        with urllib.request.urlopen(urllib.request.Request("https://data.ontario.ca/api/3/action/package_search?q=%22Board%20service%20area%22&rows=3", headers=UA), timeout=120) as resp:
            res = json.load(resp)["result"]["results"]
        info = [{"title": p["title"], "resources": [(x.get("format"), x.get("name"), x.get("url")) for x in p.get("resources", [])]} for p in res]
        json.dump(info, open("fetch/out/canada/ontario_service_area.json", "w"), indent=1)
        for p in info:
            if p["title"] == "Board service area":
                for fmt, name, url in p["resources"]:
                    if (fmt or "").upper() in ("CSV", "XLSX", "TXT") and url:
                        time.sleep(10)
                        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as f2:
                            open("fetch/out/canada/ontario_" + os.path.basename(url.split("?")[0])[-60:], "wb").write(f2.read())
        break
    except Exception as e:
        open("fetch/out/canada/ontario_error.txt", "a").write(f"{e}\n")
