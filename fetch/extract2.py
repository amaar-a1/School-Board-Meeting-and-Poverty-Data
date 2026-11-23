# Round 27: probing sources for new countries (Indonesia, Malaysia, Thailand, Nepal): what downloads from here.
import os, json, urllib.request, urllib.parse, time
OUT = "fetch/out/c27"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, keep=True, limit=40e6):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        if keep and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n   {b[:300]!r}\n")
        return b
    except Exception as e:
        log.write(f"ERR {name} {e} {url}\n")
    finally:
        log.flush(); time.sleep(2)
# Malaysia: OpenDOSM / data.gov.my
for n in ["hies_district", "population_district", "hh_poverty_district", "hies_state"]:
    get(f"my_{n}.csv", f"https://storage.dosm.gov.my/hies/{n}.csv")
    get(f"my_api_{n}.json", f"https://api.data.gov.my/data-catalogue?id={n}&limit=2000")
get("my_pop_district.csv", "https://storage.dosm.gov.my/population/population_district.csv")
get("my_catalogue.json", "https://api.data.gov.my/data-catalogue?limit=1000&meta=true")
for q in ["schools", "enrolment", "sekolah", "students_district", "enrolment_school_district"]:
    get(f"my_api_{q}.json", f"https://api.data.gov.my/data-catalogue?id={q}&limit=5")
# Indonesia: Dapodik (students per regency), World Bank INDO-DAPOER, data.go.id
get("id_dapo_nat.json", "https://dapo.kemdikbud.go.id/rekap/progres?id_level_wilayah=0&kode_wilayah=000000&semester_id=20241")
get("id_dapo_jabar.json", "https://dapo.kemdikbud.go.id/rekap/progres?id_level_wilayah=1&kode_wilayah=020000&semester_id=20241")
get("id_dapo_sp.json", "https://dapo.kemdikbud.go.id/rekap/dataSekolah?id_level_wilayah=0&kode_wilayah=000000&semester_id=20241")
get("wb_sources.json", "https://api.worldbank.org/v2/sources?format=json&per_page=200")
get("id_satudata.json", "https://data.go.id/api/3/action/package_search?q=persentase%20penduduk%20miskin%20kabupaten&rows=20")
get("id_bps_page.html", "https://www.bps.go.id/id/statistics-table/2/NjIxIzI=/persentase-penduduk-miskin--p0--menurut-kabupaten-kota.html")
# Thailand, Nepal
get("th_nesdc.html", "https://www.nesdc.go.th/main.php?filename=PovertyData")
# HDX searches for all four
pk = {}
for q in ["indonesia poverty district", "indonesia regency poverty", "malaysia district poverty", "thailand province poverty", "nepal district poverty", "nepal multidimensional poverty district", "indonesia school enrollment district"]:
    b = get("hdx_" + q.replace(" ", "_") + ".json", "https://data.humdata.org/api/3/action/package_search?rows=15&q=" + urllib.parse.quote(q), keep=False)
    try:
        for p in json.loads(b)["result"]["results"]:
            pk[p["name"]] = {"title": p["title"], "res": [(r["name"], r.get("format"), r.get("size"), r["url"]) for r in p["resources"]][:12]}
    except Exception: pass
json.dump(pk, open(f"{OUT}/hdx.json", "w"), indent=1)
log.close()
