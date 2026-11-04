# Temporary: world fetch part 6: fallback poverty figures.
import json, os, time, urllib.parse, urllib.request
OUT = "fetch/out/w6"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, text/html, */*"}
log = []
def get(url, name=None, data=None):
    time.sleep(1.5)
    try:
        h = dict(UA)
        if data: h["Content-Type"] = "application/json"
        with urllib.request.urlopen(urllib.request.Request(url, headers=h, data=data), timeout=600) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:220]}"); return d
    except Exception as e:
        body = ""
        try: body = e.read().decode()[:300]
        except Exception: pass
        log.append(f"FAIL {url[:220]}: {e} {body}"); return None
ES = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
get(ES + "ilc_li41?geo=IE04&geo=IE05&geo=IE06&geo=IE&sinceTimePeriod=2019", "ie_ilc_li41.json")
# Norway: SSB 12944 metadata, then all ages; registered unemployment by municipality
get("https://data.ssb.no/api/v0/no/table/12944", "no_12944_meta.json")
m = json.load(open("fetch/no_li_meta.json"))
regs = list(m["dimension"]["Region"]["category"]["index"])
for alder in ("0-17", "00-999", "0-999", "999"):
    pass
meta = get("https://data.ssb.no/api/v0/no/table/12944")
if meta:
    mm = json.loads(meta)
    var = {v["code"]: v for v in mm["variables"]}
    open(f"{OUT}/no_12944_vars.json", "w").write(json.dumps({k: {"values": v["values"][:40], "texts": v["valueTexts"][:40]} for k, v in var.items() if k != "Region"}, ensure_ascii=False))
    ages = var["Alder"]["values"]
    q = {"query": [{"code": "Region", "selection": {"filter": "item", "values": regs}},
                   {"code": "Alder", "selection": {"filter": "item", "values": ages}},
                   {"code": "ContentsCode", "selection": {"filter": "item", "values": var["ContentsCode"]["values"]}},
                   {"code": "Tid", "selection": {"filter": "item", "values": var["Tid"]["values"][-1:]}}], "response": {"format": "json-stat2"}}
    get("https://data.ssb.no/api/v0/no/table/12944", "no_12944_allages.json", data=json.dumps(q).encode())
um = get("https://data.ssb.no/api/v0/no/table/13563")
if um: open(f"{OUT}/no_13563_meta.json", "wb").write(um)
um = get("https://data.ssb.no/api/v0/no/table/10540")
if um: open(f"{OUT}/no_10540_meta.json", "wb").write(um)
# Finland: Sotkanet indicator list
get("https://sotkanet.fi/rest/1.1/indicators", "fi_indicators.json")
# Saint-Martin, Saint-Barthélemy (INSEE), Norfolk Island (ABS)
for g in ("COM-977", "COM-978"):
    get(f"https://www.insee.fr/fr/statistiques/2011101?geo={g}", f"insee_{g}.html")
get("https://www.abs.gov.au/census/find-census-data/quickstats/2021/901031003", "abs_norfolk_sa2.html")
get("https://www.abs.gov.au/census/find-census-data/quickstats/2021/9", "abs_other_territories.html")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
