import os, json, urllib.request, urllib.parse, re, csv, io
OUT = "fetch/out/disc3"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(name, url, keep=50000000, show=800):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r: b = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(b[:keep])
        log.write(f"== {name} OK {len(b)} {url}\n{b[:show].decode('utf-8','replace')}\n\n"); return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n\n"); return None
def ckan(tag, base, q, n=8):
    b = get(None, f"{base}/api/3/action/package_search?q={urllib.parse.quote(q)}&rows={n}", show=0)
    try:
        for p in json.loads(b)["result"]["results"]:
            log.write(f"{tag} {p['title']}: " + " ; ".join(f"{r.get('name')} {r.get('url')}" for r in p["resources"][:6]) + "\n")
    except Exception as e: log.write(f"{tag} ERR {e}\n")
# Catalonia: sums by year, municipality, naturalesa, studies
soql = ("$select=curs,codi_municipi_5,nom_municipi,nom_naturalesa,nom_estudis,sum(matr_cules_total) as n"
        "&$where=" + urllib.parse.quote("curs in('2024/2025','2025/2026')") +
        "&$group=curs,codi_municipi_5,nom_municipi,nom_naturalesa,nom_estudis&$limit=50000")
get("cat_agg.json", "https://analisi.transparenciacatalunya.cat/resource/xvme-26kg.json?" + soql, show=600)
# Flanders: sum by site municipality NIS, organising body type, main structure
b = get(None, "https://opendata.dataplatform-onderwijs.vlaanderen.be/dataloep/inschrijvingen-leerplicht-instellingen-dataset-2024-2025-1feb.csv", show=0)
if b:
    agg = {}
    for r in csv.DictReader(io.StringIO(b.decode("utf-8-sig"))):
        k = (r["vestiging_fusiegemeente_nis"], r["soort_inrichtende_macht"], r["hoofdstructuur_inschrijving"])
        agg[k] = agg.get(k, 0) + int(r["aantal_inschrijvingen"] or 0)
    json.dump([[*k, v] for k, v in sorted(agg.items())], open(f"{OUT}/vl_by_body.json", "w"), ensure_ascii=False)
    log.write(f"VL agg {len(agg)}\n")
# Wallonia-Brussels FWB: search ODWB
for q in ["fase", "implantation", "population scolaire", "réseau"]:
    b = get(None, "https://www.odwb.be/api/explore/v2.1/catalog/datasets?where=" + urllib.parse.quote(f'search("{q}")') + "&limit=40&select=dataset_id,metas", show=0)
    try:
        for x in json.loads(b)["results"]: log.write(f"ODWB[{q}] {x['dataset_id']}: {x['metas']['default'].get('title')}\n")
    except Exception as e: log.write(f"odwb {q} ERR {e}\n")
# Netherlands DUO CKAN
ckan("DUO", "https://onderwijsdata.duo.nl", "leerlingen vestiging")
ckan("DUO", "https://onderwijsdata.duo.nl", "leerlingen po per vestiging")
ckan("DUO", "https://onderwijsdata.duo.nl", "leerlingen vo per vestiging")
# Alberta school directory, BC headcount
get("ab_auth_school.xlsx", "https://education.alberta.ca/media/1626669/authority_and_school.xlsx", show=0)
get("bc_headcount.xlsx", "https://catalogue.data.gov.bc.ca/dataset/7114187e-305c-4a79-acbb-3294ba0f53c8/resource/c1a55945-8554-4058-9019-514b16178f89/download/student_headcount_by_grade_2017_18_to_2025_26.xlsx", show=0)
ckan("QC", "https://www.donneesquebec.ca/recherche", "établissements d'enseignement privé")
ckan("QC", "https://www.donneesquebec.ca/recherche", "effectif élèves établissement")
# Switzerland: BFS assets
b = get(None, "https://dam-api.bfs.admin.ch/hub/api/dam/assets?language=de&prodima=900212&limit=60", show=0)
try:
    for a in json.loads(b)["data"]: log.write(f"BFSA {a['ids']['damId']} {a['description']['titles']['main']} | {a['shop'].get('orderNr')}\n")
except Exception as e: log.write(f"bfsa ERR {e}\n")
for q in ["Lernende obligatorische Schule Kanton Schulträger", "öffentliche private Schulen Kanton Lernende"]:
    b = get(None, "https://dam-api.bfs.admin.ch/hub/api/dam/assets?language=de&limit=30&searchString=" + urllib.parse.quote(q), show=0)
    try:
        for a in json.loads(b)["data"]: log.write(f"BFSQ {a['ids']['damId']} {a['description']['titles']['main']} | {a['shop'].get('orderNr')}\n")
    except Exception as e: log.write(f"bfsq ERR {e}\n")
