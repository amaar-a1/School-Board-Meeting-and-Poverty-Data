# Round 29: Indonesia (World Bank INDO-DAPOER via the indicator API; geoBoundaries borders from GitHub); Thailand probes.
import os, json, urllib.request, urllib.parse, time
OUT = "fetch/out/c29"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, keep=True, limit=80e6, timeout=240):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if keep and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n   {b[:300]!r}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
for ind in ["SI.POV.NAPR.ZS", "SP.POP.TOTL", "SE.PRM.NENR.ZS"]:
    get(f"wb45_{ind}.json", f"https://api.worldbank.org/v2/country/all/indicator/{ind}?source=45&format=json&per_page=30000")
get("wb45_countries.json", "https://api.worldbank.org/v2/country?source=45&format=json&per_page=2000")
b = get("wb45_ind.json", "https://api.worldbank.org/v2/indicator?source=45&format=json&per_page=3000")
try:
    for i in json.loads(b)[1]:
        n = i["name"].lower()
        if any(w in n for w in ("number of students", "students", "pupils", "enrol")) and not "rate" in n:
            log.write(f"IND {i['id']} {i['name']}\n")
except Exception as e: log.write(f"ind ERR {e}\n")
for a in ["ADM2", "ADM1"]:
    get(f"id_gb_{a}.geojson", f"https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/IDN/{a}/geoBoundaries-IDN-{a}_simplified.geojson")
# Thailand: data.go.th (CKAN), NSO
get("th_ckan.json", "https://data.go.th/api/3/action/package_search?q=" + urllib.parse.quote("สัดส่วนคนจน จังหวัด") + "&rows=20")
get("th_ckan_en.json", "https://data.go.th/api/3/action/package_search?q=poverty%20province&rows=20")
get("th_nesdc2.html", "https://www.nesdc.go.th/ewt_news.php?nid=5313")
log.close()
