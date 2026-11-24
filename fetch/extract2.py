# Round 47: history for change over time: Latvia (PPS040, IRD041), Estonia (SK410, RV0240), Slovenia (2640010S),
# Portugal (INE 0013420, 0008273), US district enrollment 2018-2023 (NCES CCD via the Urban Institute's API).
import os, json, urllib.request, urllib.parse, time
OUT = "fetch/out/c47"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, data=None, timeout=300):
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers={**UA, **({"Content-Type": "application/json"} if data else {})})
        b = urllib.request.urlopen(req, timeout=timeout).read()
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
def px(name, base, fixed):
    """PxWeb: every value of every variable, except those in fixed ({code: [values]})."""
    m = get(None, base)
    if not m: return
    meta = json.loads(m)
    q = [{"code": v["code"], "selection": {"filter": "item", "values": fixed.get(v["code"], v["values"])}} for v in meta["variables"]]
    log.write(f"  {name} vars {[(v['code'], len(v['values'])) for v in meta['variables']]}\n")
    get(name, base, data={"query": q, "response": {"format": "json-stat2"}})
# Latvia
px("lv_pps040_all.json", "https://data.stat.gov.lv/api/v1/en/OSP_PUB/VES/PP/PPS/PPS040", {})
px("lv_ird041_all.json", "https://data.stat.gov.lv/api/v1/en/OSP_PUB/POP/IR/IRD/IRD041", {"AGE": ["TOTAL"], "SEX": ["T"]})
# Estonia
px("ee_sk410_all.json", "https://andmed.stat.ee/api/v1/en/stat/SK410", {"Näitaja": ["2", "5"]})
px("ee_rv0240_all.json", "https://andmed.stat.ee/api/v1/en/stat/RV0240", {"Vanus": ["000"], "Sugu": ["1"]})
# Slovenia
px("si_2640010S_all.json", "https://pxweb.stat.si/SiStatData/api/v1/en/Data/2640010S.px", {})
# Portugal: every year of the RSI rate and population
for v in ["0013420", "0008273"]:
    get(f"pt_{v}_all.json", f"https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd={v}&Dim1=T&lang=PT", timeout=600)
# US: district enrollment, NCES CCD directory, 2018-2023 (pages followed)
for y in range(2018, 2024):
    url, out = f"https://educationdata.urban.org/api/v1/school-districts/ccd/directory/{y}/", {}
    try:
        while url:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300).read())
            for r in d["results"]:
                if r.get("enrollment") not in (None, -1, -2, -3): out[r["leaid"]] = r["enrollment"]
            url = d.get("next"); time.sleep(1)
        json.dump(out, open(f"{OUT}/us_enr_{y}.json", "w")); log.write(f"US {y} {len(out)}\n")
    except Exception as e: log.write(f"US {y} ERR {e}\n")
    log.flush()
log.close()
