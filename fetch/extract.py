# Temporary: World Factbook (Saint-Pierre-et-Miquelon) and source discovery for the UK and Ireland.
import json, os, time, urllib.parse, urllib.request
OUT = "fetch/out/ukie"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, */*"}
log = []
def get(url, name=None):
    time.sleep(2)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url}"); return d
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None
# Saint-Pierre-et-Miquelon: World Factbook (open JSON copy) and the page the user linked
get("https://raw.githubusercontent.com/factbook/factbook.json/master/north-america/sb.json", "factbook_spm.json")
get("https://relief.unboundmedicine.com/relief/view/The-World-Factbook/563198/all/Saint_Pierre_and_Miquelon?q=South", "factbook_spm_relief.html")
# UK: GOV.UK search for the statistics we need (attachments come from the content API)
for q, n in [("children in low income families local area statistics", "dwp_cilif"), ("schools pupils and their characteristics", "dfe_spc")]:
    d = get("https://www.gov.uk/api/search.json?" + urllib.parse.urlencode({"q": q, "count": 8, "fields": "title,link,public_timestamp"}), f"govuk_{n}.json")
    if d:
        for r in json.loads(d).get("results", [])[:3]:
            get("https://www.gov.uk/api/content" + r["link"], f"govuk_{n}_{r['link'].strip('/').replace('/', '_')[-60:]}.json")
# ONS boundaries: counties and unitary authorities (education authorities), UK, generalised
get("https://www.arcgis.com/sharing/rest/search?" + urllib.parse.urlencode({"q": "Counties and Unitary Authorities December 2024 Boundaries UK BUC", "f": "json", "num": 10}), "ons_ctyua_search.json")
get("https://www.arcgis.com/sharing/rest/search?" + urllib.parse.urlencode({"q": "Local Authority Districts December 2024 Boundaries UK BUC", "f": "json", "num": 10}), "ons_lad_search.json")
# Scotland pupil census, Wales pupils (StatsWales), Northern Ireland enrolments: search pages
get("https://www.gov.scot/api/search?" + urllib.parse.urlencode({"q": "pupil census supplementary statistics", "type": "publication"}), "scot_search.json")
get("https://statswales.gov.wales/Catalogue/Education-and-Skills/Schools-and-Teachers/Schools-Census/Pupil-Level-Annual-School-Census/Pupils", "wales_plasc.html")
get("https://www.education-ni.gov.uk/topics/statistics-and-research/statistics", "ni_stats.html")
# Ireland: ETB list and boundaries (counties), Department of Education enrolment, Pobal deprivation
get("https://www.arcgis.com/sharing/rest/search?" + urllib.parse.urlencode({"q": "Counties Ireland Tailte Eireann boundaries generalised", "f": "json", "num": 10}), "ie_counties_search.json")
get("https://data.gov.ie/api/3/action/package_search?" + urllib.parse.urlencode({"q": "post-primary schools enrolment", "rows": 10}), "ie_enrol_search.json")
get("https://data.gov.ie/api/3/action/package_search?" + urllib.parse.urlencode({"q": "Pobal HP deprivation index", "rows": 5}), "ie_pobal_search.json")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
