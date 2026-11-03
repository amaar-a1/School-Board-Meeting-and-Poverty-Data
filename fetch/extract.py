# Temporary: download Canadian school board borders that are openly published, plus Statistics
# Canada's low-income table, and summarise them (no large files are committed).
import io, json, os, subprocess, time, urllib.parse, urllib.request, zipfile
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
os.makedirs("/tmp/ca", exist_ok=True); os.makedirs("fetch/out/canada", exist_ok=True)
log = {}
def get(url, path, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r, open(path, "wb") as f:
                f.write(r.read()); return True
        except Exception as e:
            log.setdefault("errors", []).append(f"{url[:120]}: {e}"); time.sleep(20)
    return False
# Statistics Canada low-income table (CSD level)
if get("https://www150.statcan.gc.ca/n1/tbl/csv/98100103-eng.zip", "/tmp/ca/98100103.zip"):
    z = zipfile.ZipFile("/tmp/ca/98100103.zip"); log["statcan_files"] = [(i.filename, i.file_size) for i in z.infolist()]
    with z.open([n for n in z.namelist() if not n.endswith("MetaData.csv")][0]) as f:
        head = [f.readline().decode("utf-8-sig") for _ in range(4)]
    log["statcan_head"] = head
# BC (WFS GeoJSON)
get("https://openmaps.gov.bc.ca/geo/pub/WHSE_TANTALIS.TA_SCHOOL_DISTRICTS_SVW/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=WHSE_TANTALIS.TA_SCHOOL_DISTRICTS_SVW&outputFormat=application/json&srsName=EPSG:4326", "/tmp/ca/bc.geojson")
# Quebec (shapefile zip)
get("https://www.donneesquebec.ca/recherche/dataset/37d944eb-335b-40fe-8d80-835ff77bc5cb/resource/2ded8ebe-5e71-4dff-91de-896b4150e19c/download", "/tmp/ca/qc.zip")
# Manitoba (ArcGIS feature service)
get("https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Manitoba_School_Divisions/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson", "/tmp/ca/mb.geojson")
# New Brunswick and Alberta / Ontario catalogue lookups
for key, url in {"nb_catalog": "https://gnb.socrata.com/api/catalog/v1?q=school%20district%20boundaries&limit=10",
                 "ab_catalog": "https://open.alberta.ca/api/3/action/package_search?q=%22Education%20-%20Authorities%20Public%22&rows=3",
                 "on_catalog": "https://data.ontario.ca/api/3/action/package_search?q=%22Board%20service%20area%22&rows=2",
                 "sk_catalog": "https://open.canada.ca/data/api/3/action/package_search?q=Saskatchewan%20school%20division%20boundaries&rows=10"}.items():
    time.sleep(10)
    if get(url, f"/tmp/ca/{key}.json"):
        try:
            j = json.load(open(f"/tmp/ca/{key}.json"))
            if "results" in j and isinstance(j["results"], list) and j["results"] and "resource" in j["results"][0]:
                log[key] = [(r["resource"]["name"], r["resource"]["id"], r.get("link")) for r in j["results"]]
            else:
                log[key] = [{"title": p["title"], "res": [(x.get("format"), x.get("name"), x.get("url")) for x in p.get("resources", [])][:10]} for p in j["result"]["results"]]
        except Exception as e:
            log[key] = f"parse error {e}"
# Summaries of each border file (names and counts), using mapshaper
subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
if os.path.exists("/tmp/ca/qc.zip"):
    zipfile.ZipFile("/tmp/ca/qc.zip").extractall("/tmp/ca/qc"); log["qc_files"] = [os.path.join(dp, f)[8:] for dp, _, fs in os.walk("/tmp/ca/qc") for f in fs if f.endswith(".shp")]
for name, path in [("bc", "/tmp/ca/bc.geojson"), ("mb", "/tmp/ca/mb.geojson")] + [(f"qc_{os.path.basename(p)}", "/tmp/ca/" + p) for p in log.get("qc_files", [])]:
    if os.path.exists(path):
        r = subprocess.run(f"mapshaper -i '{path}' -info", shell=True, capture_output=True, text=True)
        log[f"info_{name}"] = (r.stdout + r.stderr)[-2500:]
json.dump(log, open("fetch/out/canada/step1.json", "w"), indent=1)
