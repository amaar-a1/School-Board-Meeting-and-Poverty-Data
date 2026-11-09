# Temporary: Italian regions with their own school systems: search the open-data portals of Bolzano (South Tyrol),
# Trento and Valle d'Aosta for pupils by school or comune.
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/it_enr1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
Q = {"bz": ("https://data.civis.bz.it/api/3/action/package_search?rows=40&q=", ["schüler", "alunni scuola", "studenti scuole"]),
     "tn": ("https://dati.trentino.it/api/3/action/package_search?rows=40&q=", ["studenti iscritti scuole", "alunni", "istituzioni scolastiche"]),
     "vda": ("https://dati.regione.vda.it/api/3/action/package_search?rows=40&q=", ["alunni", "scuole studenti", "iscritti"])}
for k, (base, qs) in Q.items():
    for q in qs:
        try:
            d = json.loads(get(base + urllib.parse.quote(q)))["result"]
            log.write(f"== {k} '{q}': {d['count']}\n")
            for p in d["results"]:
                res = [(r.get("format"), r.get("name") or "", r["url"]) for r in p.get("resources", [])]
                log.write(f"  {p['name']} | {p.get('title')} | {p.get('metadata_modified','')[:10]}\n")
                for r in res[:6]: log.write(f"      {r[0]} | {str(r[1])[:60]} | {r[2][:160]}\n")
        except Exception as e: log.write(f"ERR {k} {q} {str(e)[:150]}\n")
log.close()
