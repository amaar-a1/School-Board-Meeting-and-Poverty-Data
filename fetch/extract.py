# Temporary: Iceland: municipal borders, Statistics Iceland tables, unemployment, YouTube.
import csv, json, os, subprocess, sys, time, urllib.parse, urllib.request
OUT = "fetch/out/is1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, text/html, */*"}
log = []
def get(url, name=None):
    time.sleep(1.5)
    try:
        d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=900).read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:200]}"); return d
    except Exception as e:
        body = ""
        try: body = e.read().decode()[:300]
        except Exception: pass
        log.append(f"FAIL {url[:200]}: {e} {body}"); return None
d = get("https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_2023_4326.geojson")
names = []
if d:
    feats = [f for f in json.loads(d)["features"] if f["properties"].get("CNTR_CODE") == "IS"]
    json.dump({"type": "FeatureCollection", "features": feats}, open("/tmp/lau_IS.geojson", "w"))
    names = [(f["properties"]["LAU_ID"], f["properties"]["LAU_NAME"]) for f in feats]
    log.append(f"LAU IS: {len(feats)}")
    subprocess.run("npm install -g mapshaper >/dev/null 2>&1", shell=True)
    subprocess.run(f"mapshaper -i /tmp/lau_IS.geojson -simplify 3% keep-shapes -o {OUT}/lau_IS.geojson precision=0.0001", shell=True)
HG = "https://px.hagstofa.is/pxis/api/v1/is/"
for q in ("grunnskól", "nemendur", "lágtekju", "tekjulág", "fátækt", "atvinnulaus", "mannfjöldi sveitarfélög"):
    get(HG + "?" + urllib.parse.urlencode({"query": q}), f"hg_search_{q.split()[0]}.json")
get("https://px.hagstofa.is/pxis/api/v1/is/Samfelag/skolamal", "hg_skolamal.json")
get("https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi", "hg_mannfjoldi.json")
get("https://vinnumalastofnun.is/maelabord-og-toelfraedi/manadarlegar-atvinnuleysistolur", "vmst.html")
get("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_li02?geo=IS&age=Y_LT18&sinceTimePeriod=2015", "es_is_child.json")
get("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_li41?geo=IS&geo=IS00&sinceTimePeriod=2015", "es_is_region.json")
# YouTube: each municipality's council meetings
if names:
    os.makedirs("fetch/is", exist_ok=True)
    with open("fetch/is/iceland.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["District", "District ID"]); [w.writerow([n, f"IS-{i}"]) for i, n in names]
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
    r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", f"{OUT}/yt", "IS"], capture_output=True, text=True, timeout=12000,
                       env={**os.environ, "NORDIC_DATA": "fetch/is"})
    open(f"{OUT}/yt_log.txt", "w").write(r.stdout[-20000:] + "\n---\n" + r.stderr[-3000:])
open(f"{OUT}/log.txt", "w").write("\n".join(log))
