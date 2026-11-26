# Round 53: earlier years from sources the site already uses: Japan's municipal pupils (e-Stat SSDS 0000020205,
# E2501 and E3501), Colombia's municipal education statistics (datos.gov.co nudc-7mev, every year), Taiwan's pupils by
# county (Ministry of Education open data, every year in each file), Norway's pupils (SSB 11980, every year), Sweden's
# pupils (Kolada N15835, 2015-2024), Denmark's pupils (LABY23) and child poverty (LABY07), every year.
import os, re, json, urllib.request, urllib.parse, time, gzip, shutil
OUT = "fetch/out/c53"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, data=None, timeout=600, ctype="application/json"):
    try:
        req = urllib.request.Request(url, data=data.encode() if isinstance(data, str) else data, headers={**UA, **({"Content-Type": ctype} if data else {})})
        b = urllib.request.urlopen(req, timeout=timeout).read()
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url[:150]}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url[:150]}\n")
    finally: log.flush(); time.sleep(1.5)
# Japan
key = os.environ.get("ESTAT_APP_ID", "")
if key:
    base = "https://api.e-stat.go.jp/rest/3.0/app/json"
    for code in ("E2501", "E3501"):
        vals, pos = [], 1
        try:
            while pos:
                d = json.loads(urllib.request.urlopen(f"{base}/getStatsData?appId={key}&statsDataId=0000020205&cdCat01={code}&limit=100000&startPosition={pos}", timeout=300).read())
                sd = d["GET_STATS_DATA"]["STATISTICAL_DATA"]; v = sd.get("DATA_INF", {}).get("VALUE", [])
                vals += [{"area": x.get("@area"), "time": x.get("@time"), "v": x.get("$")} for x in (v if isinstance(v, list) else [v])]
                pos = sd.get("RESULT_INF", {}).get("NEXT_KEY"); time.sleep(1)
            json.dump(vals, open(f"{OUT}/jp_ssds_{code}.json", "w")); log.write(f"JP {code}: {len(vals)}\n")
        except Exception as e: log.write(f"JP {code} ERR {str(e)[:200]}\n")
# Colombia
get("co_men_all_years.json", "https://www.datos.gov.co/resource/nudc-7mev.json?$limit=60000")
# Taiwan
for f in ("edu_B_3_2", "edu_B_3_8", "edu_B_4_2"):
    get(f"tw_{f}.csv", f"https://stats.moe.gov.tw/files/opendata/{f}.csv")
# Norway: SSB 11980, every value of every variable
m = get("no_11980_meta.json", "https://data.ssb.no/api/v0/no/table/11980")
if m:
    meta = json.loads(m)
    log.write(f"  NO vars {[(v['code'], len(v['values']), v['values'][:3], v.get('valueTexts', [])[:3]) for v in meta['variables']]}\n")
    q = [{"code": v["code"], "selection": {"filter": "item", "values": v["values"]}} for v in meta["variables"]]
    get("no_11980_all.json", "https://data.ssb.no/api/v0/no/table/11980", data=json.dumps({"query": q, "response": {"format": "json-stat2"}}))
# Sweden: Kolada N15835 (pupils in the municipality, förskoleklass to year 9)
for y in range(2015, 2025):
    get(f"se_N15835_{y}.json", f"https://api.kolada.se/v3/data/kpi/N15835/year/{y}")
# Denmark: LABY23 (pupils) and LABY07 (children in relative poverty), every year
for t in ("LABY23", "LABY07"):
    info = get(f"dk_{t}_info.json", f"https://api.statbank.dk/v1/tableinfo/{t}?lang=en&format=JSON")
    if not info: continue
    vs = json.loads(info)["variables"]
    log.write(f"  DK {t} vars {[(v['id'], len(v['values']), [x['text'] for x in v['values'][:3]]) for v in vs]}\n")
    body = {"table": t, "format": "CSV", "lang": "en", "variables": [{"code": v["id"], "values": ["*"]} for v in vs]}
    get(f"dk_{t}_all.csv", "https://api.statbank.dk/v1/data", data=json.dumps(body))
for f in os.listdir(OUT):
    p = f"{OUT}/{f}"
    if os.path.getsize(p) > 50e6 and not f.endswith(".gz"):
        with open(p, "rb") as a, gzip.open(p + ".gz", "wb") as b: shutil.copyfileobj(a, b)
        os.remove(p)
log.close()
