# Temporary: public/private pupils: England (GIAS full extract: independent schools' pupils by LA), Colombia (datos.gov.co
# enrollment by sector and municipality), Germany (Regionalstatistik: pupils by school ownership, districts).
import csv, io, json, os, time, urllib.parse, urllib.request
OUT = "fetch/out/pub3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
# England
for d in ("20261113", "20261112", "20261111", "20261110", "20261109"):
    try:
        b = get(f"https://ea-edubase-api-prod.azurewebsites.net/edubase/downloads/public/edubasealldata{d}.csv")
        rows = list(csv.DictReader(io.StringIO(b.decode("cp1252"))))
        log.write(f"EN {d}: {len(rows)} rows; cols {[c for c in rows[0] if 'Type' in c or 'Pupils' in c or 'LA' in c or 'Status' in c][:12]}\n")
        agg = {}
        for r in rows:
            if r.get("EstablishmentStatus (name)") != "Open": continue
            g = r.get("EstablishmentTypeGroup (name)"); la = r.get("LA (name)")
            try: n = float(r.get("NumberOfPupils") or 0)
            except ValueError: n = 0
            agg.setdefault(la, {}).setdefault(g, 0); agg[la][g] += n
        json.dump({"date": d, "by_la": agg}, open(f"{OUT}/england_pupils_by_la_group.json", "w"))
        log.write("EN groups " + json.dumps(sorted({g for v in agg.values() for g in v})) + "\n"); break
    except Exception as e: log.write(f"EN {d} ERR {str(e)[:120]}\n")
# Colombia
for q in ["matricula sector oficial no oficial municipio", "matricula por sector municipio", "matrícula oficial no oficial"]:
    try:
        d = json.loads(get("https://www.datos.gov.co/api/catalog/v1?limit=10&q=" + urllib.parse.quote(q), 60))
        for x in d.get("results", []):
            r = x["resource"]; log.write(f"CO | {r['id']} | {r['name']} | {r.get('updatedAt','')[:10]} | {', '.join(r.get('columns_name', [])[:20])}\n")
    except Exception as e: log.write(f"ERR CO {e}\n")
# Germany
for term in ["Schüler Trägerschaft", "Schulen Trägerschaft Kreise"]:
    try:
        u = "https://www.regionalstatistik.de/genesisws/rest/2020/find/find?" + urllib.parse.urlencode({"username": "GAST", "password": "GAST", "term": term, "category": "tables", "language": "de"})
        d = json.loads(get(u, 60))
        for t in (d.get("Tables") or [])[:20]: log.write(f"DE | {t.get('Code')} | {t.get('Content')}\n")
    except Exception as e: log.write(f"ERR DE {e}\n")
    time.sleep(2)
log.close()
