# Temporary: Philippines. PSA OpenSTAT table list (poverty), HDX search for municipal poverty and boundaries, border repo tree.
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/ph2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
for name, u in {"openstat_db.json": "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB",
                "openstat_1E.json": "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1E",
                "openstat_1E_FY.json": "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1E/FY",
                "hdx_pov.json": "https://data.humdata.org/api/3/action/package_search?q=philippines%20poverty%20municipal&rows=30",
                "hdx_cod.json": "https://data.humdata.org/api/3/action/package_show?id=cod-ab-phl",
                "gh_tree.json": "https://api.github.com/repos/faeldon/philippines-json-maps/git/trees/master"}.items():
    try:
        b = get(u); open(f"{OUT}/{name}", "wb").write(b); log.write(f"ok {name} {len(b)}\n")
    except Exception as e: log.write(f"ERR {name} {str(e)[:150]}\n")
log.close()
