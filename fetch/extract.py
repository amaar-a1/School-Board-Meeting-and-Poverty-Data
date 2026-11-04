# Temporary: islands (World Bank, Eurostat), Germany and New Zealand exploration.
import json, os, time, urllib.parse, urllib.request
OUT = "fetch/out/w1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, */*"}
log = []
def get(url, name=None, data=None, ctype="application/json"):
    time.sleep(1.5)
    try:
        h = dict(UA)
        if data: h["Content-Type"] = ctype
        with urllib.request.urlopen(urllib.request.Request(url, headers=h, data=data), timeout=600) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:200]}"); return d
    except Exception as e:
        body = ""
        try: body = e.read().decode()[:300]
        except Exception: pass
        log.append(f"FAIL {url[:200]}: {e} {body}"); return None
ISO = "ABW AIA ATG BHR BHS BLM BMU BRB COK COM CPV CUW CYM CYP DMA FJI FLK FRO FSM GGY GRD GRL IMN ISL JAM JEY KIR KNA LCA MAF MDV MHL MLT MSR MUS NCL NFK NIU NRU PLW PYF SGP SHN SLB STP SXM SYC TCA TON TTO TUV VCT VGB VUT WLF WSM CHI".split()
for ind in ("SE.PRM.ENRL", "SE.SEC.ENRL", "SI.POV.NAHC", "SL.UEM.TOTL.ZS", "SP.POP.TOTL", "SP.POP.0014.TO.ZS"):
    get(f"https://api.worldbank.org/v2/country/{';'.join(ISO)}/indicator/{ind}?format=json&per_page=20000&date=2005:2025", f"wb_{ind}.json")
get("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_li02?age=Y_LT18&indic_il=LI_R_MD60&sex=T&unit=PC&geo=MT&geo=CY&geo=IS&geo=DE&sinceTimePeriod=2019", "es_ilc_li02.json")
# Germany
get("https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_10M_2021_4326_LEVL_3.geojson", "de_nuts3.geojson")
RS = "https://www.regionalstatistik.de/genesisws/rest/2020"
get(f"{RS}/helloworld/logincheck?username=GAST&password=GAST", "de_rs_login.json")
for t in ("Bedarfsgemeinschaften", "Kinder SGB II", "Schüler allgemeinbildende Schulen", "Leistungsberechtigte"):
    get(f"{RS}/find/find?" + urllib.parse.urlencode({"username": "GAST", "password": "GAST", "term": t, "category": "tables", "pagelength": 100}), f"de_rs_find_{t.split()[0]}.json")
get("https://www-genesis.destatis.de/genesisWS/rest/2020/helloworld/logincheck?username=GAST&password=GAST", "de_destatis_login.json")
get("https://www.inkar.de/", "de_inkar.html")
get("https://www.wegweiser-kommune.de/daten/kinderarmut", "de_wwk.html")
# New Zealand
get("https://catalogue.data.govt.nz/api/3/action/package_search?" + urllib.parse.urlencode({"q": "schools directory", "rows": 10}), "nz_ckan_schools.json")
get("https://catalogue.data.govt.nz/api/3/action/package_search?" + urllib.parse.urlencode({"q": "child poverty region", "rows": 10}), "nz_ckan_poverty.json")
get("https://www.stats.govt.nz/information-releases/child-poverty-statistics-year-ended-june-2025/", "nz_cp2025.html")
get("https://www.stats.govt.nz/information-releases/child-poverty-statistics-year-ended-june-2024/", "nz_cp2024.html")
get("https://www.educationcounts.govt.nz/directories/list-of-nz-schools", "nz_ec_list.html")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
