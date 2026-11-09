# Temporary: Spanish regions' open data on pupils by school or municipality: catalogue searches.
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/es_reg1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
S = {"cat": "https://analisi.transparenciacatalunya.cat/api/catalog/v1?limit=20&q=",
     "mad": "https://datos.comunidad.madrid/api/3/action/package_search?rows=15&q=",
     "eus": "https://opendata.euskadi.eus/api/3/action/package_search?rows=15&q=",
     "gob": "https://datos.gob.es/apidata/catalog/dataset/title/"}
Q = {"cat": ["alumnes matriculats", "matrícula centres educatius"], "mad": ["alumnos matriculados centros", "alumnado"], "eus": ["alumnado matriculado", "ikasleak"], "gob": ["alumnos matriculados"]}
for k, base in S.items():
    for q in Q[k]:
        try:
            d = json.loads(get(base + urllib.parse.quote(q) + (".json?_pageSize=30" if k == "gob" else "")))
            if k == "cat":
                for x in d.get("results", []):
                    r = x["resource"]; log.write(f"cat | {r['id']} | {r['name']} | {r.get('updatedAt','')[:10]} | {', '.join(c for c in r.get('columns_name', [])[:14])}\n")
            elif k == "gob":
                for x in d.get("result", {}).get("items", [])[:30]:
                    t = x.get("title"); t = t[0]["_value"] if isinstance(t, list) else t
                    log.write(f"gob | {t} | {x.get('_about','')[:120]}\n")
            else:
                for p in d["result"]["results"]:
                    log.write(f"{k} | {p['name']} | {p.get('title')} | {p.get('metadata_modified','')[:10]}\n")
                    for r in p.get("resources", [])[:3]: log.write(f"      {r.get('format')} | {r['url'][:140]}\n")
        except Exception as e: log.write(f"ERR {k} {q} {str(e)[:150]}\n")
log.close()
