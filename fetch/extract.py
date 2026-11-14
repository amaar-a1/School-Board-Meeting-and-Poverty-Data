# Temporary: public-school pupils by municipality: Norway (SSB 11980, kommunal), Denmark (LABY23 by school type),
# Sweden (Kolada KPIs on independent schools).
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/nordic_pub1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, data=None, t=180):
    h = dict(UA)
    if data is not None: h["Content-Type"] = "application/json"
    with urllib.request.urlopen(urllib.request.Request(u, data=data, headers=h), timeout=t) as r: return r.read()
try:
    q = {"query": [{"code": "KOKkommuneregion0000", "selection": {"filter": "all", "values": ["*"]}},
                   {"code": "KOKeierfh0000", "selection": {"filter": "item", "values": ["K", "KP"]}},
                   {"code": "KOKtrinn0000", "selection": {"filter": "item", "values": ["0"]}},
                   {"code": "Tid", "selection": {"filter": "item", "values": ["2025"]}}], "response": {"format": "json-stat2"}}
    b = get("https://data.ssb.no/api/v0/no/table/11980", json.dumps(q).encode()); open(f"{OUT}/no_pupils_K_KP.json", "wb").write(b); log.write(f"NO {len(b)}\n")
except Exception as e: log.write(f"ERR NO {e} {getattr(e,'read',lambda:b'')()[:300]}\n")
try:
    info = json.loads(get("https://api.statbank.dk/v1/tableinfo/LABY23?lang=en&format=JSON"))
    for v in info["variables"]: log.write(f"DK var {v['id']} {v['text']}: {[(x['id'], x['text']) for x in v['values'][:15]]} n={len(v['values'])}\n")
    g = next(v for v in info["variables"] if v["id"] == "GRUNDSKOL")
    body = {"table": "LABY23", "format": "CSV", "lang": "en", "variables": [
        {"code": "FSTATUS", "values": [info["variables"][0]["values"][0]["id"]]}, {"code": "UDDANNELSE", "values": ["TOT"] if any(x["id"] == "TOT" for x in info["variables"][1]["values"]) else [info["variables"][1]["values"][0]["id"]]},
        {"code": "GRUNDSKOL", "values": [x["id"] for x in g["values"]]}, {"code": "KOMGRP", "values": ["*"]}, {"code": "Tid", "values": ["2025"]}]}
    b = get("https://api.statbank.dk/v1/data", json.dumps(body).encode()); open(f"{OUT}/dk_LABY23_by_type.csv", "wb").write(b); log.write(f"DK data {len(b)} head {b[:400]!r}\n")
except Exception as e: log.write(f"ERR DK {e} {getattr(e,'read',lambda:b'')()[:300]}\n")
try:
    for q in ["fristående grundskola", "kommunal grundskola"]:
        d = json.loads(get("https://api.kolada.se/v2/kpi?title=" + urllib.parse.quote(q)))
        for k in d["values"][:25]: log.write(f"SE kpi {k['id']} | {k['title']} | {k.get('municipality_type')} | {k.get('has_ou_data')}\n")
except Exception as e: log.write(f"ERR SE {e}\n")
log.close()
