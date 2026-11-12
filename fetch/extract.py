# Temporary: find official enrollment by municipality (Colombia, Brazil, Mexico, Spanish regions).
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/enr_find1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=90):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
def tryit(tag, u, fn):
    try: fn(get(u))
    except Exception as e: log.write(f"ERR {tag} {u[:120]} {str(e)[:120]}\n")
# Colombia: Socrata catalogue
for q in ["matricula municipio", "estadisticas educacion municipio", "matrícula SIMAT"]:
    def f(b):
        for x in json.loads(b).get("results", [])[:12]:
            r = x["resource"]; log.write(f"CO | {r['id']} | {r['name']} | {r.get('updatedAt','')[:10]} | {', '.join(r.get('columns_name', [])[:25])}\n")
    tryit("co", "https://www.datos.gov.co/api/catalog/v1?limit=12&q=" + urllib.parse.quote(q), f)
# Brazil: INEP sinopse files
for y in (2024, 2025, 2023):
    u = f"https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopses_estatisticas_censo_escolar_{y}.zip"
    try:
        req = urllib.request.Request(u, headers=UA, method="HEAD"); r = urllib.request.urlopen(req, timeout=60)
        log.write(f"BR {y} {r.status} {r.headers.get('Content-Length')}\n")
    except Exception as e: log.write(f"BR {y} ERR {str(e)[:120]}\n")
# Mexico: datos.gob.mx CKAN
for q in ["estadistica 911 municipio", "alumnos municipio educacion basica", "matricula municipio SEP"]:
    def f(b):
        for p in json.loads(b)["result"]["results"][:10]:
            log.write(f"MX | {p['name']} | {p.get('title')} | {p.get('metadata_modified','')[:10]}\n")
            for r in p.get("resources", [])[:4]: log.write(f"      {r.get('format')} | {r.get('name','')[:60]} | {r['url'][:150]}\n")
    tryit("mx", "https://www.datos.gob.mx/api/3/action/package_search?rows=10&q=" + urllib.parse.quote(q), f)
# Spanish regions
S = {"eus": "https://opendata.euskadi.eus/api/3/action/package_search?rows=8&q=", "gva": "https://dadesobertes.gva.es/api/3/action/package_search?rows=8&q=",
     "and": "https://www.juntadeandalucia.es/datosabiertos/portal/api/3/action/package_search?rows=8&q=", "gal": "https://abertos.xunta.gal/api/3/action/package_search?rows=8&q=",
     "cyl": "https://analisis.datosabiertos.jcyl.es/api/explore/v2.1/catalog/datasets?limit=8&where=", "ara": "https://opendata.aragon.es/ckan/api/3/action/package_search?rows=8&q="}
for k, base in S.items():
    for q in ["alumnado municipio", "alumnos matriculados"]:
        def f(b, k=k):
            d = json.loads(b)
            res = d["result"]["results"] if "result" in d else d.get("results", [])
            for p in res[:8]:
                if "result" in d:
                    log.write(f"ES-{k} | {p['name']} | {p.get('title')} | {p.get('metadata_modified','')[:10]}\n")
                    for r in p.get("resources", [])[:3]: log.write(f"      {r.get('format')} | {r['url'][:150]}\n")
                else: log.write(f"ES-{k} | {p.get('dataset_id')} | {json.dumps(p.get('metas',{}).get('default',{}).get('title',''))}\n")
        tryit("es-" + k, base + urllib.parse.quote(q if k != "cyl" else f'search("{q}")'), f)
log.close()
