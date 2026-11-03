# Temporary: download Canadian school board enrolment files (provincial open data).
import json, os, re, time, urllib.request
OUT = "fetch/out/enrol"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
log = []
def get(url, name=None, limit=60_000_000):
    time.sleep(3)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
            data = r.read(limit + 1)
        if len(data) > limit:
            log.append(f"too big: {url}"); return None
        if name:
            open(f"{OUT}/{name}", "wb").write(data)
        log.append(f"ok {len(data)} {url} -> {name}")
        return data
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None

def ckan(base, pid, prefix, want=lambda r: True, keep=3):
    d = get(f"{base}/api/3/action/package_show?id={pid}")
    if not d:
        return
    res = json.loads(d)["result"]["resources"]
    open(f"{OUT}/{prefix}_resources.json", "w").write(json.dumps([(r.get("name"), r.get("format"), r.get("url")) for r in res], indent=1))
    picked = [r for r in res if want(r)][:keep]
    for i, r in enumerate(picked):
        ext = (r.get("format") or "bin").lower().split("/")[-1][:5]
        get(r["url"], f"{prefix}_{i}.{ext}")

# Ontario: enrolment by grade, by board (elementary and secondary)
for n in ["enrolment_by_grade_elementary_schools_en.xlsx", "enrolment_by_grade_secondary_schools_en.xlsx"]:
    get(f"https://files.ontario.ca/opendata/{n}", "on_" + n)
for pid in ["enrolment-by-grade-in-elementary-schools", "enrolment-by-grade-in-secondary-schools", "ontario-public-schools-enrolment"]:
    ckan("https://data.ontario.ca", pid, "on_" + pid[:30], want=lambda r: (r.get("format") or "").upper() in ("XLSX", "CSV"), keep=2)
# British Columbia: BC Schools - Student Headcount by Grade
ckan("https://catalogue.data.gov.bc.ca", "7114187e-305c-4a79-acbb-3294ba0f53c8", "bc", want=lambda r: (r.get("format") or "").lower() in ("csv", "xlsx"), keep=2)
# Alberta: School Authority Student Population
ckan("https://open.alberta.ca", "e5ada449-0242-47a4-ab46-181216dec8ca", "ab", want=lambda r: "authority" in (r.get("name") or "").lower() or "authority" in (r.get("url") or "").lower(), keep=3)
# Manitoba: enrolment report (PDF)
for y in (2025, 2024):
    get(f"https://www.edu.gov.mb.ca/k12/finance/sch_enrol/enrolment_{y}.pdf", f"mb_enrolment_{y}.pdf")
# Quebec: enrolment by school service centre (PDF)
get("https://cdn-contenu.quebec.ca/cdn-contenu/education/indicateurs-statistiques/Previsions_effectif_scolaire/Faits_saillants/evolution-effectif-scolaire.pdf", "qc_evolution.pdf")
# Nova Scotia: find the enrolment dataset on the Socrata portal
d = get("https://data.novascotia.ca/api/catalog/v1?q=enrolment%20school&limit=10")
if d:
    items = json.loads(d).get("results", [])
    open(f"{OUT}/ns_catalog.json", "w").write(json.dumps([(i["resource"]["name"], i["resource"]["id"]) for i in items], indent=1))
    for i in items:
        if re.search(r"enrol", i["resource"]["name"], re.I) and re.search(r"RCE|school", i["resource"]["name"], re.I):
            get(f"https://data.novascotia.ca/api/views/{i['resource']['id']}/rows.csv?accessType=DOWNLOAD", f"ns_{i['resource']['id']}.csv"); break
# New Brunswick: enrolment by school by grade (federal open data mirror of NB's file)
ckan("https://open.canada.ca/data", "712e7355-91d7-7b4f-9d46-1e7b5561cd95", "nb", want=lambda r: (r.get("format") or "").upper() in ("CSV", "XLSX"), keep=2)
# Saskatchewan: look for a provincial enrolment table
d = get("https://open.canada.ca/data/api/3/action/package_search?q=saskatchewan%20school%20division%20enrolment&rows=10")
if d:
    open(f"{OUT}/sk_search.json", "w").write(json.dumps([(p["title"], p["id"], [(r.get("format"), r.get("url")) for r in p["resources"]][:4]) for p in json.loads(d)["result"]["results"]], indent=1))
open(f"{OUT}/log.txt", "w").write("\n".join(log))
