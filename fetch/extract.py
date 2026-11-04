# Temporary: UK and Ireland data files (child poverty, enrolment, boundaries).
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/ukie2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "*/*"}
log = []
def get(url, name=None, limit=80_000_000):
    time.sleep(2)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            d = r.read(limit + 1)
        if len(d) > limit: log.append(f"too big {url}"); return None
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url} -> {name}"); return d
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None
def links(page, pat, base):
    h = get(page)
    return [urllib.parse.urljoin(base, x.decode()) for x in re.findall(rb'href="([^"]+)"', h or b"") if re.search(pat, x.decode(), re.I)]
def esri(url, name):
    feats, off = [], 0
    while True:
        d = get(f"{url}/query?where=1%3D1&outFields=*&outSR=4326&f=geojson&resultOffset={off}&resultRecordCount=500")
        if not d: break
        j = json.loads(d); feats += j.get("features", [])
        if len(j.get("features", [])) < 500: break
        off += 500
    json.dump({"type": "FeatureCollection", "features": feats}, open(f"{OUT}/{name}", "w"))
    log.append(f"{name}: {len(feats)} features")
# UK child poverty (DWP, all four nations, local authority level)
get("https://assets.publishing.service.gov.uk/media/69b809619d8b52961a62b49a/children-in-low-income-families-local-area-statistics-2022-2025.ods", "dwp_cilif_2022_2025.ods")
# UK boundaries: counties and unitary authorities (education authorities), December 2024, generalised
esri("https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Counties_and_Unitary_Authorities_December_2024_Boundaries_UK_BUC/FeatureServer/0", "uk_ctyua_2024.geojson")
# England: school census (Explore Education Statistics release files)
d = get("https://content.explore-education-statistics.service.gov.uk/api/publications/school-pupils-and-their-characteristics/releases/2025-26", "ees_release.json")
if d:
    rel = json.loads(d)
    files = [f for f in rel.get("downloadFiles", []) + [x.get("file", {}) for x in rel.get("dataSets", [])] if isinstance(f, dict)]
    open(f"{OUT}/ees_files.json", "w").write(json.dumps(files, indent=1)[:200000])
    rid = rel.get("id")
    if rid:
        get(f"https://content.explore-education-statistics.service.gov.uk/api/releases/{rid}/files", "ees_all_files.zip", limit=300_000_000)
# Scotland: pupil census supplementary statistics (spreadsheets)
for u in links("https://www.gov.scot/publications/pupil-census-supplementary-statistics/", r"\.xlsx|\.ods|supplementary", "https://www.gov.scot")[:4]:
    if re.search(r"\.(xlsx|ods)$", u): get(u, "scot_" + os.path.basename(u)[:60])
# Wales: schools' census results
for u in links("https://www.gov.wales/schools-census-results-january-2025", r"\.(xlsx|ods|csv)", "https://www.gov.wales")[:3]:
    get(u, "wales_" + os.path.basename(u)[:60])
# Northern Ireland: school enrolments
for u in links("https://www.education-ni.gov.uk/topics/school-enrolments", r"enrolment", "https://www.education-ni.gov.uk")[:6]:
    if "publications" in u:
        for f in links(u, r"\.(xlsx|ods|csv)$", "https://www.education-ni.gov.uk")[:2]:
            get(f, "ni_" + os.path.basename(f)[:60])
        break
# Ireland: counties, Pobal HP Deprivation Index 2022 (by small area / ED), post-primary school list with enrolment
esri("https://services6.arcgis.com/MmUrOQU5v1he9gfS/arcgis/rest/services/Counties_OSi_Ireland/FeatureServer/0", "ie_counties.geojson")
get("https://www.pobal.ie/wp-content/uploads/2024/01/hp-deprivation-index-scores-2022.csv", "ie_pobal_2022.csv")
for u in links("https://www.gov.ie/en/department-of-education/collections/data-on-individual-schools/", r"post-primary|data-on-individual", "https://www.gov.ie")[:3]:
    for f in links(u, r"\.(xlsx|csv)$", "https://www.gov.ie")[:2]:
        get(f, "ie_" + os.path.basename(f)[:60])
open(f"{OUT}/log.txt", "w").write("\n".join(log))
