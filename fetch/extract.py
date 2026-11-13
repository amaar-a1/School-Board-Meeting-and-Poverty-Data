# Temporary: NSW public schools master dataset (data.nsw.gov.au, CC BY 4.0): Norfolk Island Central School enrolment and licence.
import csv, io, json, os, urllib.parse, urllib.request
OUT = "fetch/out/nfk1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
try:
    d = json.loads(get("https://data.nsw.gov.au/data/api/3/action/package_search?rows=5&q=" + urllib.parse.quote("NSW public schools master dataset")))
    for p in d["result"]["results"]:
        log.write(f"PKG {p['name']} | {p.get('title')} | licence {p.get('license_title')} | {p.get('metadata_modified','')[:10]}\n")
        for r in p.get("resources", []):
            log.write(f"   {r.get('format')} | {r.get('name')} | {r['url']}\n")
            if r.get("format", "").upper() == "CSV" and "master" in (r.get("name", "") + r["url"]).lower():
                rows = list(csv.DictReader(io.StringIO(get(r["url"]).decode("utf-8-sig", "replace"))))
                log.write(f"   cols {list(rows[0].keys())}\n")
                for x in rows:
                    if "norfolk" in json.dumps(x).lower(): log.write("   NFK " + json.dumps(x)[:1500] + "\n")
except Exception as e: log.write(f"ERR {e}\n")
log.close()
