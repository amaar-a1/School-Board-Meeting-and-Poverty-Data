import os, json, urllib.request, urllib.parse, re, csv, io, time
OUT = "fetch/out/disc2"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(name, url, keep=400000, show=1500, data=None):
    try:
        req = urllib.request.Request(url, headers=dict(UA, **({"Content-Type": "application/json"} if data else {})), data=data)
        with urllib.request.urlopen(req, timeout=300) as r: b = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(b[:keep])
        log.write(f"== {name} OK {len(b)} {url}\n{b[:show].decode('utf-8','replace')}\n\n"); return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n\n"); return None
# 1 Catalonia: pupils by municipality, naturalesa, level (2025/2026 and 2024/2025)
q = "$select=curs,codi_municip_6,nom_municipi,nom_naturalesa,count(*)&$group=curs,codi_municip_6,nom_municipi,nom_naturalesa&$limit=50000"
get("cat_cols.json", "https://analisi.transparenciacatalunya.cat/api/views/xvme-26kg.json", show=200)
try:
    cols = [c["fieldName"] for c in json.load(open(f"{OUT}/cat_cols.json"))["columns"]]; log.write(f"CAT COLUMNS {cols}\n")
except Exception as e: log.write(f"cat cols {e}\n")
get("cat_row.json", "https://analisi.transparenciacatalunya.cat/resource/xvme-26kg.json?$limit=1&$where=" + urllib.parse.quote("curs='2025/2026' AND nom_naturalesa='Públic'"), show=3000)
# 2 Flanders: enrolments by school site with network
b = get(None, "https://opendata.dataplatform-onderwijs.vlaanderen.be/dataloep/inschrijvingen-leerplicht-instellingen-dataset-2024-2025-1feb.csv", show=1500)
if b:
    t = b.decode("utf-8-sig", "replace"); open(f"{OUT}/vl_head.txt", "w").write("\n".join(t.splitlines()[:5]))
    sep = ";" if t[:2000].count(";") > t[:2000].count(",") else ","
    rows = list(csv.DictReader(io.StringIO(t), delimiter=sep)); log.write(f"VL rows {len(rows)} cols {list(rows[0].keys())}\n")
    for k in rows[0]:
        vals = {}
        for r in rows: vals[r[k]] = vals.get(r[k], 0) + 1
        if len(vals) < 40: log.write(f"  VL {k}: {vals}\n")
# 3 Wallonia WalStat datasets on odwb
for ds in ["2432000", "243300", "2435000", "2437010", "243700", "2434000", "2436000", "2321000", "216000", "201131", "8338000", "8115100", "831100", "833602", "8312000"]:
    b = get(None, f"https://www.odwb.be/api/explore/v2.1/catalog/datasets/{ds}", show=0)
    if b:
        d = json.loads(b); m = d.get("metas", {}).get("default", {})
        log.write(f"ODWB {ds}: {m.get('title')} | fields {[f['name'] for f in d.get('fields', [])]}\n")
get("odwb_search.json", "https://www.odwb.be/api/explore/v2.1/catalog/datasets?where=" + urllib.parse.quote('search("réseau") OR search("population scolaire") OR search("implantation")') + "&limit=60&select=dataset_id,metas.default.title", show=6000)
# 4 DUO overview
b = get("duo_over.html", "https://duo.nl/open_onderwijsdata/overzicht-open-data.jsp", show=0)
if b: log.write("DUO links: " + " ".join(l for l in set(re.findall(r'href="([^"]+)"', b.decode("utf-8", "replace"))) if re.search(r"leerling|\.csv|primair|voortgezet", l, re.I)) + "\n\n")
# 5 Croatia primary school lists
for n, u in [("hr_os1.csv", "https://data.gov.hr/ckan/dataset/2841fb78-c828-4ab2-8cdc-f22abeed3a8c/resource/3c72e1c1-4c41-48f0-8663-c7ce4a997e88/download/data.csv"),
             ("hr_os2.csv", "https://data.gov.hr/ckan/dataset/8f3aa566-ac50-47db-adc0-ccab7d6b0e57/resource/2d906a25-e863-4ff4-a6d7-0e940e8b11df/download/osovne-kole.csv")]:
    get(n, u, keep=3000000, show=1200)
get("hr_meta.json", "https://data.gov.hr/ckan/api/3/action/package_show?id=2841fb78-c828-4ab2-8cdc-f22abeed3a8c", show=1500)
# 6 Alberta school enrolment 2025/26 + school list
get("ab_school_enr.xlsx", "https://open.alberta.ca/dataset/ccbcf0fb-615e-44a0-b7ec-681e2ea4e1e7/resource/fccf0597-1693-4f73-9def-902963fd20d1/download/ecc-school-enrolment-data-2025-2026.xlsx", keep=20000000, show=0)
get("ab_list.json", "https://open.alberta.ca/api/3/action/package_search?q=school%20list%20authority%20directory&rows=8", show=0)
try:
    for p in json.load(open(f"{OUT}/ab_list.json"))["result"]["results"]:
        log.write(f"AB {p['title']}: " + " ; ".join(f"{r.get('name')} {r.get('url')}" for r in p["resources"][:4]) + "\n")
except Exception as e: log.write(f"ab list {e}\n")
# 7 BC / Quebec catalogue
for n, u in [("bc1.json", "https://catalogue.data.gov.bc.ca/api/3/action/package_search?q=student%20headcount&rows=8"),
             ("qc1.json", "https://www.donneesquebec.ca/recherche/api/3/action/package_search?q=effectif%20scolaire&rows=8")]:
    b = get(n, u, show=0)
    try:
        for p in json.loads(b)["result"]["results"]:
            log.write(f"{n} {p['title']}: " + " ; ".join(f"{r.get('name')} {r.get('url')}" for r in p["resources"][:5]) + "\n")
    except Exception as e: log.write(f"{n} {e}\n")
# 8 Switzerland: table metadata
for t in ["px-x-1502010100_101", "px-x-1502010100_102", "px-x-1502010100_103", "px-x-1502010100_104", "px-x-1502020100_101", "px-x-1502020100_102", "px-x-1502010000_101"]:
    b = get(None, f"https://www.pxweb.bfs.admin.ch/api/v1/de/{t}/{t}.px", show=0)
    if b:
        d = json.loads(b); log.write(f"BFS {t}: {d.get('title')} | " + " | ".join(f"{v['code']}: {v['valueTexts'][:8]}" for v in d["variables"]) + "\n")
# 9 New countries probes
get("ee_soc.json", "https://andmed.stat.ee/api/v1/en/stat/sotsiaalne-terjutus-laekeni-indikaatorid", show=3000)
get("ee_sots.json", "https://andmed.stat.ee/api/v1/en/stat/sotsiaalne-kaitse", show=3000)
get("lv_ves.json", "https://data.stat.gov.lv/api/v1/en/OSP_PUB/VES", show=3000)
get("lv_fin.json", "https://data.stat.gov.lv/api/v1/en/OSP_PUB/FIN", show=3000)
get("lt_osp.html", "https://osp.stat.gov.lt/", show=500)
get("kr_clik_api.html", "https://clik.nanet.go.kr/potal/guide/openApi.do", show=3000)
get("cz_exek2.html", "https://mapaexekuci.cz/index.php/mapa-2/", show=500)
