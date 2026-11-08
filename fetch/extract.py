# Temporary: PSA OpenSTAT table 2a, every value (poverty by region, province and highly urbanized city, 2018-2023).
import json, os, urllib.request
OUT = "fetch/out/ph6"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Content-Type": "application/json"}
u = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/1F/FY/0041F3DF02A.px"
meta = json.load(open("fetch/out/ph5/t2a_meta.json"))
q = {"query": [{"code": v["code"], "selection": {"filter": "item", "values": v["values"]}} for v in meta["variables"]], "response": {"format": "json-stat2"}}
with urllib.request.urlopen(urllib.request.Request(u, headers=UA, data=json.dumps(q).encode()), timeout=300) as r: open(f"{OUT}/t2a_data.json", "wb").write(r.read())
