# Temporary: world fetch part 2.
import json, os, time, urllib.parse, urllib.request
OUT = "fetch/out/w2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, text/csv, */*"}
log = []
def get(url, name=None, data=None):
    time.sleep(1.5)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA, data=data), timeout=600) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:220]}"); return d
    except Exception as e:
        body = ""
        try: body = e.read().decode()[:600]
        except Exception: pass
        log.append(f"FAIL {url[:220]}: {e} {body}"); return None
for ind in ("SE.PRM.ENRL", "SE.SEC.ENRL", "SI.POV.NAHC", "SL.UEM.TOTL.ZS", "SP.POP.TOTL", "SP.POP.0014.TO.ZS"):
    get(f"https://api.worldbank.org/v2/country/all/indicator/{ind}?format=json&per_page=20000&date=2010:2025", f"wb_{ind}.json")
get("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_li02?geo=MT&geo=CY&geo=IS&geo=DE&age=Y_LT18&sinceTimePeriod=2020", "es_ilc_li02.json")
NZ = "https://www.stats.govt.nz/assets/Uploads/Child-poverty-statistics/Child-poverty-statistics-Year-ended-June-2025/Download-data/"
get(NZ + "child-poverty-statistics-year-ended-june-2025.xlsx", "nz_cp2025.xlsx")
get(NZ + "child-poverty-statistics-year-ended-june-2025-summary-table.xlsx", "nz_cp2025_summary.xlsx")
WW = "https://www.wegweiser-kommune.de"
get(WW + "/data-api/rest/export/kinderarmut+berlin+2016-2023+tabelle.csv", "de_ww_berlin.csv")
get(WW + "/data-api/rest/export/kinderarmut+berlin+hamburg+2023+tabelle.csv", "de_ww_two.csv")
get(WW + "/data-api/rest/region/filter", "de_ww_region_filter.json")
for q in ("?search=kreis", "?query=kreis", "?term=Landkreis", "?type=LANDKREIS", ""):
    get(WW + "/data-api/rest/region/list" + q, f"de_ww_region_list{len(q)}.json")
get(WW + "/data-api/rest/suggest/regionType", "de_ww_regiontype.json")
get(WW + "/data-api/rest/indicator/list?search=Kinderarmut", "de_ww_ind.json")
get(WW + "/data-api/js/statistics/main.aec9d13b.chunk.js", "de_ww_main.js")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
