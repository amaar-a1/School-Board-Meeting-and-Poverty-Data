# Temporary: Statistics Finland 125j: comprehensive schools by municipality and owner type, 2025 (count of schools,
# and pupils if the table has them).
import json, os, urllib.request
OUT = "fetch/out/fi_own2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Content-Type": "application/json"}
log = open(f"{OUT}/log.txt", "w")
base = "https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/kjarj/125j.px"
m = json.loads(urllib.request.urlopen(urllib.request.Request(base, headers=UA), timeout=60).read())
for v in m["variables"]: log.write(f"{v['code']}: {list(zip(v['values'], v['valueTexts']))[:25]}\n")
types = next(v for v in m["variables"] if v["code"].startswith("oppilaittostyyp"))
want_types = [c for c, t in zip(types["values"], types["valueTexts"]) if t.startswith("Peruskoulu") or t.startswith("Perus- ja lukio")]
q = {"query": [{"code": "timeperiod_y", "selection": {"filter": "item", "values": ["2025"]}},
               {"code": "alue_23_20230101", "selection": {"filter": "all", "values": ["*"]}},
               {"code": "contentscode", "selection": {"filter": "item", "values": ["Oppyht", "kjarj-oppilaitoksia"]}},
               {"code": next(v["code"] for v in m["variables"] if v["code"].startswith("omistajatyyppi")), "selection": {"filter": "all", "values": ["*"]}},
               {"code": next(v["code"] for v in m["variables"] if v["code"].startswith("kieli")), "selection": {"filter": "item", "values": ["SSS"] if "SSS" in next(v for v in m["variables"] if v["code"].startswith("kieli"))["values"] else [next(v for v in m["variables"] if v["code"].startswith("kieli"))["values"][0]]}},
               {"code": types["code"], "selection": {"filter": "item", "values": want_types}}],
     "response": {"format": "json-stat2"}}
log.write("query " + json.dumps(q) + "\n")
try:
    b = urllib.request.urlopen(urllib.request.Request(base, data=json.dumps(q).encode(), headers=UA), timeout=120).read()
    open(f"{OUT}/fi_125j_2025.json", "wb").write(b); log.write(f"data {len(b)}\n")
except Exception as e: log.write(f"ERR {e} {getattr(e, 'read', lambda: b'')()[:400]}\n")
log.close()

# v2
