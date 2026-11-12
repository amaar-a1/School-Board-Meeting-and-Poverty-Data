# Temporary: Svalbard pupils (SSB 11980 region list), plus Falklands/Norfolk/Niue/Tokelau/Pitcairn school pages.
import json, os, urllib.request
OUT = "fetch/out/isl_enr1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, data=None, t=90):
    h = dict(UA); 
    if data: h["Content-Type"] = "application/json"
    with urllib.request.urlopen(urllib.request.Request(u, data=data, headers=h), timeout=t) as r: return r.read()
try:
    m = json.loads(get("https://data.ssb.no/api/v0/en/table/11980"))
    for v in m["variables"]:
        vals = list(zip(v["values"], v["valueTexts"]))
        log.write(f"SSB var {v['code']} {v['text']} n={len(vals)} {[x for x in vals if 'valbard' in x[1] or 'Longyear' in x[1]] or vals[:6]}\n")
    reg = next(v for v in m["variables"] if v["code"] == "Region")
    sv = [c for c, t in zip(reg["values"], reg["valueTexts"]) if "valbard" in t or "Longyear" in t]
    q = {"query": [{"code": "Region", "selection": {"filter": "item", "values": sv}}] + [{"code": v["code"], "selection": {"filter": "item", "values": [v["values"][-1]]}} for v in m["variables"] if v["code"] == "Tid"], "response": {"format": "json-stat2"}}
    log.write("SSB data " + get("https://data.ssb.no/api/v0/en/table/11980", json.dumps(q).encode()).decode()[:2500] + "\n")
except Exception as e: log.write(f"ERR SSB {e}\n")
for tag, u in [("FLK", "https://en.wikipedia.org/w/index.php?title=Falkland_Islands_Community_School&action=raw"),
               ("FLK2", "https://en.wikipedia.org/w/index.php?title=Infant_and_Junior_School&action=raw"),
               ("NFK", "https://en.wikipedia.org/w/index.php?title=Norfolk_Island_Central_School&action=raw"),
               ("NIU", "https://en.wikipedia.org/w/index.php?title=Niue_High_School&action=raw"),
               ("NIU2", "https://en.wikipedia.org/w/index.php?title=Education_in_Niue&action=raw"),
               ("TKL", "https://en.wikipedia.org/w/index.php?title=Education_in_Tokelau&action=raw"),
               ("PCN", "https://en.wikipedia.org/w/index.php?title=Pulawana_School&action=raw")]:
    try:
        t = get(u).decode()
        import re
        hits = [m.group(0) for m in re.finditer(r"[^\n]{0,160}(students|pupils|enrolment|enrollment|roll)[^\n]{0,160}", t, re.I)][:8]
        log.write(f"{tag} {len(t)}\n  " + "\n  ".join(hits) + "\n")
    except Exception as e: log.write(f"{tag} ERR {e}\n")
log.close()
