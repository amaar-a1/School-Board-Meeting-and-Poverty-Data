# Temporary: Nordics + Netherlands part 2.
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/nordic2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, */*"}
log = []
def get(url, name=None, data=None, ctype=None):
    time.sleep(1.5)
    try:
        h = dict(UA)
        if ctype: h["Content-Type"] = ctype
        with urllib.request.urlopen(urllib.request.Request(url, headers=h, data=data), timeout=600) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:160]}"); return d
    except Exception as e:
        log.append(f"FAIL {url[:160]}: {e}"); return None
def save(name, obj): json.dump(obj, open(f"{OUT}/{name}", "w"), indent=1, ensure_ascii=False)
# Norway: SSB v0 search, single words
for q in ["lavinntekt", "vedvarende lavinntekt", "grunnskolen elever", "elevar"]:
    d = get("https://data.ssb.no/api/v0/no/table/?" + urllib.parse.urlencode({"query": q}))
    if d: save(f"no_{q.replace(' ', '_')}.json", [(t.get("id"), t.get("text") or t.get("title"), t.get("updated")) for t in json.loads(d)][:60] if isinstance(json.loads(d), list) else json.loads(d))
# Sweden: SCB v2 search
for q in ["ekonomisk standard", "låg ekonomisk standard", "elever grundskola", "grundskolan elever kommun"]:
    d = get("https://statistikdatabasen.scb.se/api/v2/tables?" + urllib.parse.urlencode({"query": q, "lang": "sv", "pageSize": 60}))
    if d: save(f"se_{q.replace(' ', '_')}.json", [(t.get("id"), t.get("label"), t.get("firstPeriod"), t.get("lastPeriod")) for t in json.loads(d).get("tables", [])])
# Denmark: table details, Danish table list for pupils
for t in ["IFOR12P", "IFOR11P", "IFOR12A", "LABY07", "IFOR51"]:
    get(f"https://api.statbank.dk/v1/tableinfo/{t}?lang=en&format=JSON", f"dk_info_{t}.json")
d = get("https://api.statbank.dk/v1/tables?lang=da&format=JSON")
if d: save("dk_tables_da.json", [(t["id"], t["text"]) for t in json.loads(d) if re.search(r"elev|folkeskol|grundskol|fattig", t["text"], re.I)])
# Finland: Sotkanet indicator 228 (child at-risk-of-poverty rate) and regions; StatFin pupils table 133w metadata
get("https://sotkanet.fi/rest/1.1/regions", "fi_regions.json")
get("https://sotkanet.fi/rest/1.1/json?indicator=228&years=2022&years=2023&years=2024&genders=total", "fi_228.json")
get("https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/opiskt/statfin_opiskt_pxt_133w.px", "fi_133w_meta.json")
# Netherlands: CBS child poverty by region (86132NED) and pupils by residence (85701NED): metadata + data for municipalities
for t in ["86132NED", "85701NED"]:
    get(f"https://opendata.cbs.nl/ODataApi/odata/{t}/DataProperties?$format=json", f"nl_{t}_props.json")
    get(f"https://opendata.cbs.nl/ODataApi/odata/{t}/RegioS?$format=json", f"nl_{t}_regions.json")
    get(f"https://opendata.cbs.nl/ODataApi/odata/{t}/Perioden?$format=json", f"nl_{t}_periods.json")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
