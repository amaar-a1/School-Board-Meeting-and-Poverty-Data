# Temporary: CBS tables for Bonaire, Sint Eustatius and Saba (population by age; pupils), and Statistics Norway's Svalbard population.
import json, os, traceback, urllib.request
OUT = "fetch/out/isl4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, data=None):
    req = urllib.request.Request(u, headers={**UA, **({"Content-Type": "application/json"} if data else {})}, data=data)
    with urllib.request.urlopen(req, timeout=300) as r: return r.read()
for t in ("83698NED", "84732NED"):
    for part in ("DataProperties", "TypedDataSet"):
        try:
            b = get(f"https://opendata.cbs.nl/ODataApi/odata/{t}/{part}?$format=json"); open(f"{OUT}/{t}_{part}.json", "wb").write(b); log.write(f"ok {t} {part} {len(b)}\n")
        except Exception as e: log.write(f"ERR {t} {part} {str(e)[:150]}\n")
    try:
        meta = json.loads(get(f"https://opendata.cbs.nl/ODataApi/odata/{t}?$format=json"))
        for x in meta["value"]:
            if x["name"] not in ("TypedDataSet", "UntypedDataSet", "DataProperties", "TableInfos"):
                open(f"{OUT}/{t}_{x['name']}.json", "wb").write(get(x["url"] + "?$format=json"))
        log.write(f"ok {t} dims\n")
    except Exception as e: log.write(f"ERR {t} dims {str(e)[:150]}\n")
try:
    q = {"query": [], "response": {"format": "json-stat2"}}
    open(f"{OUT}/ssb_07430.json", "wb").write(get("https://data.ssb.no/api/v0/no/table/07430/", json.dumps(q).encode())); log.write("ok ssb\n")
except Exception as e: log.write(f"ERR ssb {str(e)[:150]}\n")
log.close()
