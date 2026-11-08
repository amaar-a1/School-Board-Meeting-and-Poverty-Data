# Temporary: PSA OpenSTAT table 2a in several formats (the JSON-stat answer came back with one value).
import json, os, urllib.request
OUT = "fetch/out/ph7"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Content-Type": "application/json"}
u = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1F/FY/0041F3DF02A.px"
meta = json.load(open("fetch/out/ph5/t2a_meta.json"))
log = open(f"{OUT}/log.txt", "w")
for fmt in ("csv", "json", "json-stat"):
    for sel in ("item", "all"):
        q = {"query": [{"code": v["code"], "selection": ({"filter": "item", "values": v["values"]} if sel == "item" else {"filter": "all", "values": ["*"]})} for v in meta["variables"]], "response": {"format": fmt}}
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA, data=json.dumps(q).encode()), timeout=300) as r: b = r.read()
            open(f"{OUT}/t2a_{sel}.{fmt.replace('-', '')}", "wb").write(b); log.write(f"ok {fmt} {sel} {len(b)}\n")
        except Exception as e: log.write(f"ERR {fmt} {sel} {str(e)[:150]}\n")
log.close()
