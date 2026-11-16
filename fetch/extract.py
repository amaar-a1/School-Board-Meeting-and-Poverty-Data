import os, json, urllib.request, urllib.parse, re, time
OUT = "fetch/out/disc1"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(name, url, keep=400000, show=1500):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
            b = r.read()
        open(f"{OUT}/{name}", "wb").write(b[:keep])
        log.write(f"== {name} OK {len(b)} {url}\n{b[:show].decode('utf-8','replace')}\n\n")
        return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n\n"); return None
def links(name, url, pat):
    b = get(name, url, show=200)
    if b:
        ls = sorted(set(re.findall(r'href="([^"]*)"', b.decode("utf-8", "replace"))))
        log.write(f"-- links {name}: " + "\n".join(l for l in ls if re.search(pat, l, re.I)) + "\n\n")
# Catalonia
get("cat_search.json", "https://api.us.socrata.com/api/catalog/v1?domains=analisi.transparenciacatalunya.cat&q=alumnes%20matriculats&limit=15", show=200)
try:
    d = json.load(open(f"{OUT}/cat_search.json"))
    for x in d["results"]: log.write(f"CAT {x['resource']['id']} | {x['resource']['name']} | {x['resource'].get('columns_field_name')}\n")
except Exception as e: log.write(f"cat parse {e}\n")
get("cat_sample.json", "https://analisi.transparenciacatalunya.cat/resource/xvme-26kg.json?$limit=3")
# World Bank private enrolment shares
get("wb_prm.json", "https://api.worldbank.org/v2/country/all/indicator/SE.PRM.PRIV.ZS?format=json&per_page=20000&date=2010:2025", keep=5000000, show=600)
get("wb_sec.json", "https://api.worldbank.org/v2/country/all/indicator/SE.SEC.PRIV.ZS?format=json&per_page=20000&date=2010:2025", keep=5000000, show=300)
# Netherlands DUO
links("duo_po.html", "https://duo.nl/open_onderwijsdata/primair-onderwijs/aantal-leerlingen/", r"\.csv|leerling")
links("duo_vo.html", "https://duo.nl/open_onderwijsdata/voortgezet-onderwijs/aantal-leerlingen/", r"\.csv|leerling")
# Belgium
get("odwb.json", "https://www.odwb.be/api/explore/v2.1/catalog/datasets?where=search(%22%C3%A9l%C3%A8ves%22)&limit=50&select=dataset_id", show=4000)
links("vl_stat.html", "https://onderwijs.vlaanderen.be/nl/onderwijsstatistieken/statistisch-jaarboek-van-het-vlaams-onderwijs", r"xls|csv|jaarboek|leerling")
get("vl_open.json", "https://opendata.vlaanderen.be/api/3/action/package_search?q=leerlingen%20onderwijsnet&rows=20", show=3000)
# Switzerland
get("bfs_list.json", "https://www.pxweb.bfs.admin.ch/api/v1/de/", show=3000)
get("bfs_search.json", "https://dam-api.bfs.admin.ch/hub/api/dam/assets?language=de&q=Lernende%20Kanton%20Schultr%C3%A4ger&limit=20", show=4000)
# NZ
get("nz_ckan.json", "https://catalogue.data.govt.nz/api/3/action/package_search?q=school%20directory&rows=5", show=3000)
links("nz_dir.html", "https://www.educationcounts.govt.nz/directories/list-of-nz-schools", r"\.csv|directory")
# Ireland
get("ie_ckan.json", "https://data.gov.ie/api/3/action/package_search?q=enrolment%20schools&rows=15", show=3000)
# Croatia
get("hr_ckan.json", "https://data.gov.hr/ckan/api/3/action/package_search?q=%C5%A1kole&rows=15", show=3000)
# Canada
get("bc_ckan.json", "https://catalogue.data.gov.bc.ca/api/3/action/package_search?q=student%20headcount%20independent&rows=5", show=3000)
get("ab_ckan.json", "https://open.alberta.ca/api/3/action/package_search?q=student%20population%20school%20authority&rows=5", show=3000)
get("qc_ckan.json", "https://www.donneesquebec.ca/recherche/api/3/action/package_search?q=effectif%20scolaire%20priv%C3%A9&rows=5", show=3000)
# Estonia
get("ee_volis.html", "https://www.volis.ee/", show=2000)
get("ee_stat.json", "https://andmed.stat.ee/api/v1/en/stat/sotsiaalelu", show=3000)
# Korea CLIK
get("kr_clik.html", "https://clik.nanet.go.kr/", show=1500)
# Lithuania / Latvia / Czech
get("lt_osp.json", "https://get.data.gov.lt/datasets/gov/vssa/?format=json", show=1500)
get("cz_exek.html", "https://www.mapaexekuci.cz/", show=1500)
get("lv_csp.json", "https://data.stat.gov.lv/api/v1/en/OSP_PUB/", show=2000)
