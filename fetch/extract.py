# Temporary: Svalbard (Longyearbyen) pupils, SSB table 11980.
import json, os, urllib.request
OUT = "fetch/out/isl_enr2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Content-Type": "application/json"}
q = {"query": [{"code": "KOKkommuneregion0000", "selection": {"filter": "item", "values": ["2111"]}},
               {"code": "KOKeierfh0000", "selection": {"filter": "item", "values": ["KP"]}},
               {"code": "KOKtrinn0000", "selection": {"filter": "item", "values": ["0"]}}], "response": {"format": "json-stat2"}}
try:
    b = urllib.request.urlopen(urllib.request.Request("https://data.ssb.no/api/v0/en/table/11980", data=json.dumps(q).encode(), headers=UA), timeout=90).read()
    open(f"{OUT}/svalbard.json", "wb").write(b); open(f"{OUT}/log.txt", "w").write(b.decode()[:3000])
except Exception as e: open(f"{OUT}/log.txt", "w").write(f"ERR {e} {getattr(e, 'read', lambda: b'')()[:500]}")
