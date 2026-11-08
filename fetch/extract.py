# retry; log the limit headers; also look for the ministry (SIO) pupil counts on dane.gov.pl
# Temporary: Poland's primary-school pupils by gmina from the Local Data Bank (BDL), slowly (anonymous users may make
# 100 requests per 15 minutes), plus county (powiat) names to tell apart gminy with the same name.
import json, os, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/pl_pupils"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "application/json"}
BDL = "https://bdl.stat.gov.pl/api/v1"
log = open(f"{OUT}/log.txt", "w")
import urllib.error
# dane.gov.pl: datasets of pupils by school (SIO), saved as found
try:
    for q in ("liczba uczniów SIO", "uczniowie szkoły SIO", "dane SIO uczniowie"):
        with urllib.request.urlopen(urllib.request.Request("https://api.dane.gov.pl/1.4/search?q=" + urllib.parse.quote(q) + "&per_page=50", headers=UA), timeout=120) as r:
            open(f"{OUT}/danegov_{q.replace(' ', '_')}.json", "wb").write(r.read())
        log.write(f"danegov {q} ok\n"); time.sleep(1)
except Exception as e: log.write(f"danegov ERR {str(e)[:200]}\n")
# one probe of the BDL, logging the status and every header (the limit headers say when it resets)
try:
    with urllib.request.urlopen(urllib.request.Request(f"{BDL}/units?level=0&format=json", headers=UA), timeout=120) as r:
        log.write(f"probe {r.status} {dict(r.headers)}\n")
except urllib.error.HTTPError as e: log.write(f"probe {e.code} {dict(e.headers)} {e.read()[:500]}\n")
except Exception as e: log.write(f"probe ERR {e}\n")
log.flush(); time.sleep(12)
FIRST = [True]
def get(u):
    # The first request checks whether the limit has reset: 5 tries 2 minutes apart (about 10 minutes), then stop.
    tries, wait = (5, 120) if FIRST[0] else (6, 300)
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120) as r: d = json.loads(r.read())
            FIRST[0] = False; time.sleep(12); return d
        except Exception as e:
            log.write(f"retry {a} {str(e)[:80]} {u[:120]}\n"); log.flush()
            if a < tries - 1: time.sleep(wait)
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
