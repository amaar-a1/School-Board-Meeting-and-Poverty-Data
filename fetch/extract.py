# Temporary: UK/Ireland part 3: convert ODS to CSV, England school register, Ireland census unemployment, NI enrolment.
import datetime, json, os, re, subprocess, sys, time, urllib.parse, urllib.request
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pandas", "odfpy", "openpyxl"], check=True)
import site, importlib; site.addsitedir(site.getusersitepackages()); importlib.invalidate_caches()
import pandas as pd
OUT = "fetch/out/ukie3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "*/*"}
log = []
def get(url, name=None, limit=200_000_000):
    time.sleep(2)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            d = r.read(limit + 1)
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url} -> {name}"); return d
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None
# ODS files from the last run -> one CSV per sheet
for f in ["fetch/out/ukie2/dwp_cilif_2022_2025.ods", "fetch/out/ukie2/wales_schools-census-results-january-2025.ods"]:
    try:
        x = pd.ExcelFile(f, engine="odf")
        for s in x.sheet_names:
            pd.read_excel(x, s, header=None).to_csv(f"{OUT}/{os.path.basename(f)[:20]}__{re.sub(r'\W+', '_', s)[:40]}.csv", index=False, header=False)
        log.append(f"converted {f}: {x.sheet_names}")
    except Exception as e:
        log.append(f"convert failed {f}: {e}")
# England: Get Information about Schools (all establishments), state-funded pupil counts by local authority
day = datetime.date.today()
for back in range(0, 8):
    d = (day - datetime.timedelta(days=back)).strftime("%Y%m%d")
    raw = get(f"https://ea-edubase-api-prod.azurewebsites.net/edubase/downloads/public/edubasealldata{d}.csv")
    if raw:
        g = pd.read_csv(__import__("io").BytesIO(raw), encoding="latin-1", low_memory=False)
        keep = [c for c in g.columns if c in ("LA (code)", "LA (name)", "EstablishmentStatus (name)", "TypeOfEstablishment (name)", "EstablishmentTypeGroup (name)", "NumberOfPupils", "PhaseOfEducation (name)", "CensusDate")]
        g[keep].to_csv(f"{OUT}/gias_{d}.csv", index=False)
        log.append(f"GIAS columns kept: {keep}")
        break
# Ireland: Census 2022 principal economic status by county (CSO PxStat), found through data.gov.ie
d = get("https://data.gov.ie/api/3/action/package_search?" + urllib.parse.urlencode({"q": "census 2022 principal economic status county", "rows": 15}))
if d:
    res = json.loads(d)["result"]["results"]
    open(f"{OUT}/ie_census_search.json", "w").write(json.dumps([(p["title"], p["name"], [(r.get("format"), r.get("url")) for r in p["resources"]][:2]) for p in res], indent=1))
    for p in res:
        if re.search(r"economic status", p["title"], re.I) and re.search(r"county|administrative", p["title"], re.I):
            for r in p["resources"]:
                if (r.get("format") or "").upper() == "CSV":
                    get(r["url"], "ie_" + p["name"][:40] + ".csv"); break
            break
get("https://www.pobal.ie/wp-content/uploads/2024/01/hp-deprivation-index-scores-2022.csv", "ie_pobal_2022.csv")
# Ireland: post-primary enrolment by school (data.gov.ie)
d = get("https://data.gov.ie/api/3/action/package_search?" + urllib.parse.urlencode({"q": "post primary schools enrolment 2024", "rows": 15, "sort": "metadata_modified desc"}))
if d:
    open(f"{OUT}/ie_pp_search.json", "w").write(json.dumps([(p["title"], p["name"], [(r.get("format"), r.get("url")) for r in p["resources"]][:3]) for p in json.loads(d)["result"]["results"]], indent=1))
# Northern Ireland: school enrolments summary
for page in ["https://www.education-ni.gov.uk/publications/school-enrolments-northern-ireland-summary-data",
             "https://www.education-ni.gov.uk/articles/school-enrolments-overview"]:
    h = get(page, "ni_" + page.rstrip("/").split("/")[-1] + ".html")
    for f in re.findall(rb'href="([^"]+\.(?:xlsx|ods|csv))"', h or b"")[:3]:
        get(urllib.parse.urljoin("https://www.education-ni.gov.uk", f.decode()), "ni_" + os.path.basename(f.decode())[:50])
open(f"{OUT}/log.txt", "w").write("\n".join(log))
