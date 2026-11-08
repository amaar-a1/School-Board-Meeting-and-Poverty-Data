# Temporary: Poland's primary-school pupils by gmina from the Local Data Bank (BDL), slowly (anonymous users may make
# 100 requests per 15 minutes), plus county (powiat) names to tell apart gminy with the same name.
import json, os, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/pl_pupils"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "application/json"}
BDL = "https://bdl.stat.gov.pl/api/v1"
log = open(f"{OUT}/log.txt", "w")
def get(u):
    for a in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120) as r: d = json.loads(r.read())
            time.sleep(12); return d
        except Exception as e:
            log.write(f"retry {a} {str(e)[:80]} {u[:120]}\n"); log.flush(); time.sleep(300)
    raise RuntimeError("gave up: " + u)
try:
    pv = []
    for page in range(3):
        d = get(f"{BDL}/variables/search?name={urllib.parse.quote('uczniowie')}&level=6&page-size=100&page={page}&format=json&lang=pl")
        pv += [{k: v.get(k) for k in ("id", "subjectId", "n1", "n2", "n3", "n4", "n5", "measureUnitName")} for v in d.get("results", [])]
        if not d.get("links", {}).get("next"): break
    json.dump(pv, open(f"{OUT}/pl_pupil_vars.json", "w"), ensure_ascii=False, indent=0)
    cand = [v for v in pv if "podstaw" in " ".join(str(v.get(k) or "") for k in ("n1", "n2", "n3")).lower() and "ogółem" in " ".join(str(v.get(k) or "") for k in ("n2", "n3", "n4")).lower()]
    log.write("candidates: " + json.dumps(cand[:10], ensure_ascii=False) + "\n")
    data = {}
    for v in cand[:3]:
        vid, vals, got = str(v["id"]), {}, 0
        for yr in ("2024", "2023"):
            page = 0
            while True:
                d = get(f"{BDL}/data/by-variable/{vid}?unit-level=6&year={yr}&page-size=100&page={page}&format=json&lang=pl")
                for r in d.get("results", []):
                    for x in r.get("values", []):
                        if x.get("val") is not None: vals[r["id"]] = x["val"]; got += 1
                if not d.get("links", {}).get("next"): break
                page += 1
            log.write(f"{vid} {yr}: {got}\n"); log.flush()
            if got: data[vid] = {"var": v, "year": yr, "values": vals}; break
        json.dump(data, open(f"{OUT}/pl_pupils.json", "w"), ensure_ascii=False)
        if got > 2000: break
    # counties
    units, page = [], 0
    while True:
        d = get(f"{BDL}/units?level=5&page-size=100&page={page}&format=json&lang=pl")
        units += [{"id": u["id"], "name": u["name"]} for u in d.get("results", [])]
        if not d.get("links", {}).get("next"): break
        page += 1
    json.dump(units, open(f"{OUT}/pl_counties.json", "w"), ensure_ascii=False)
    log.write(f"counties {len(units)}\n")
except Exception:
    log.write(traceback.format_exc()[-1500:])
log.close()
