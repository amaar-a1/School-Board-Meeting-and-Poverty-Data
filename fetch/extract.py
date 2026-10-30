# Temporary: download Census cartographic school district boundaries and simplify them for a web map.
import os, subprocess, urllib.request, zipfile
os.makedirs("/tmp/geo", exist_ok=True); os.makedirs("fetch/out/map", exist_ok=True)
log = open("fetch/out/map/log.txt", "w")
def get(name):
    for year in (2024, 2023):
        url = f"https://www2.census.gov/geo/tiger/GENZ{year}/shp/cb_{year}_us_{name}_500k.zip"
        path = f"/tmp/geo/{name}.zip"
        try:
            urllib.request.urlretrieve(url, path)
            d = f"/tmp/geo/{name}"
            zipfile.ZipFile(path).extractall(d)
            shp = [f for f in os.listdir(d) if f.endswith(".shp")][0]
            log.write(f"{name}: {url}\n")
            return f"{d}/{shp}"
        except Exception as e:
            log.write(f"{name} {year} failed: {e}\n")
paths = {n: get(n) for n in ("unsd", "elsd", "scsd", "state", "county")}
subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True, check=True)
def ms(args):
    r = subprocess.run("mapshaper " + args, shell=True, capture_output=True, text=True)
    log.write(f"$ mapshaper {args}\n{r.stdout[-2000:]}{r.stderr[-2000:]}\n")
for n in ("unsd", "elsd", "scsd"):
    ms(f"-i {paths[n]} -info")
    ms(f"-i {paths[n]} name={n} -filter-fields GEOID,NAME -simplify 6% keep-shapes -o fetch/out/map/{n}.json format=topojson quantization=100000")
ms(f"-i {paths['state']} -filter 'STATEFP==\"60\"||STATEFP==\"66\"||STATEFP==\"69\"||STATEFP==\"72\"' "
   "-each 'GEOID = STATEFP==\"66\" ? \"6600002\" : STATEFP==\"69\" ? \"6900002\" : STATEFP==\"72\" ? \"7200030\" : \"6000030\"' "
   "-filter-fields GEOID,NAME -o /tmp/geo/terr_a.json format=geojson")
ms(f"-i {paths['county']} -filter 'STATEFP==\"78\"' -each 'GEOID = COUNTYFP==\"010\" ? \"7800002\" : \"7800030\"' "
   "-dissolve GEOID -o /tmp/geo/terr_b.json format=geojson")
ms("-i /tmp/geo/terr_a.json /tmp/geo/terr_b.json combine-files -merge-layers force name=territories "
   "-filter-fields GEOID,NAME -simplify 15% keep-shapes -o fetch/out/map/territories.json format=topojson quantization=100000")
log.close()
for f in os.listdir("fetch/out/map"):
    print(f, os.path.getsize(f"fetch/out/map/{f}"))
