# Round 28: Malaysia enrolment and borders; Indonesia (World Bank INDO-DAPOER, source 45); third-country probes.
import os, json, urllib.request, urllib.parse, time
OUT = "fetch/out/c28"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, keep=True, limit=60e6, timeout=180):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if keep and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n   {b[:300]!r}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
# Malaysia
get("my_enrol.json", "https://api.data.gov.my/data-catalogue?id=enrolment_school_district&limit=100000")
for n in ["schools_district", "teachers_district", "enrolment_school_state"]:
    get(f"my_{n}.json", f"https://api.data.gov.my/data-catalogue?id={n}&limit=3")
get("my_district.geojson", "https://raw.githubusercontent.com/dosm-malaysia/data-open/main/datasets/geodata/administrative_2_district.geojson")
get("my_gb_adm2.json", "https://www.geoboundaries.org/api/current/gbOpen/MYS/ADM2/")
# Indonesia: INDO-DAPOER
b = get("wb45_ind.json", "https://api.worldbank.org/v2/sources/45/indicators?format=json&per_page=3000")
get("wb45_cty.json", "https://api.worldbank.org/v2/sources/45/country?format=json&per_page=2000")
try:
    inds = json.loads(b)[1]
    pick = [i for i in inds if any(w in i["name"].lower() for w in ("poverty", "poor", "students", "pupils", "enrol", "population, total", "total population"))]
    json.dump([(i["id"], i["name"]) for i in pick], open(f"{OUT}/wb45_pick.json", "w"), indent=0)
    for i in pick[:40]:
        get(f"wb45_{i['id']}.json", f"https://api.worldbank.org/v2/sources/45/country/all/series/{i['id']}/time/all?format=json&per_page=20000", timeout=300)
except Exception as e: log.write(f"pick ERR {e}\n")
get("id_gb_adm2.json", "https://www.geoboundaries.org/api/current/gbOpen/IDN/ADM2/")
# Third-country probes via HDX
pk = {}
for q in ["rwanda district poverty", "sri lanka poverty divisional secretariat", "ghana district poverty 2021", "bangladesh upazila poverty", "uganda district poverty", "mongolia soum poverty", "vietnam province poverty"]:
    b = get("hdx_" + q.replace(" ", "_") + ".json", "https://data.humdata.org/api/3/action/package_search?rows=15&q=" + urllib.parse.quote(q), keep=False)
    try:
        for p in json.loads(b)["result"]["results"]:
            pk[p["name"]] = {"title": p["title"], "res": [(r["name"], r.get("format"), r.get("size"), r["url"]) for r in p["resources"]][:12]}
    except Exception: pass
json.dump(pk, open(f"{OUT}/hdx.json", "w"), indent=1)
log.close()
