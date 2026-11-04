# Temporary: world fetch part 3: Germany (Wegweiser Kommune child poverty by district; Eurostat NUTS3).
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/w3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, text/csv, */*"}
log = []
def get(url, name=None):
    time.sleep(1.2)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:220]}"); return d
    except Exception as e:
        body = ""
        try: body = e.read().decode()[:300]
        except Exception: pass
        log.append(f"FAIL {url[:220]}: {e} {body}"); return None
ES = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
get(ES + "demo_r_d3dens?geo=DE&sinceTimePeriod=2021", "es_dens_probe.json")
nuts = json.load(open("fetch/out/w1/de_nuts3.geojson"))
ids = sorted(f["properties"]["NUTS_ID"] for f in nuts["features"] if f["properties"]["CNTR_CODE"] == "DE")
q = "&".join(f"geo={i}" for i in ids)
get(ES + f"demo_r_d3dens?{q}&sinceTimePeriod=2021", "es_de_dens.json")
get(ES + f"demo_r_pjanaggr3?{q}&sex=T&age=Y_LT15&age=TOTAL&sinceTimePeriod=2021", "es_de_pop.json")
get(ES + "ilc_li02?geo=DE&age=Y_LT18&sinceTimePeriod=2020", "es_de_arop.json")
# Wegweiser: find each district's page name, then export child poverty in chunks.
WW = "https://www.wegweiser-kommune.de/data-api/rest"
found = {}
for f in nuts["features"]:
    p = f["properties"]
    if p["CNTR_CODE"] != "DE": continue
    name = p["NAME_LATN"]
    term = re.sub(r",.*$|^(Landkreis|Kreis|Regionalverband|Städteregion|Stadtkreis)\s+|-?Kreis$", "", name).strip()
    kfs = "Kreisfreie Stadt" in name or "Stadtkreis" in name
    d = get(f"{WW}/region/list?" + urllib.parse.urlencode({"search": term}) + ("&types=KREISFREIE_STADT" if kfs else "&types=LANDKREIS"))
    try: found[p["NUTS_ID"]] = {"nuts": name, "term": term, "hits": json.loads(d) if d else []}
    except Exception: found[p["NUTS_ID"]] = {"nuts": name, "term": term, "hits": []}
json.dump(found, open(f"{OUT}/de_ww_search.json", "w"), ensure_ascii=False)
def best(v):
    h = v["hits"]
    if not h: return None
    norm = lambda s: re.sub(r"[^a-zäöüß]", "", s.lower())
    for x in h:
        if norm(x["name"]) == norm(v["term"]): return x["friendlyUrl"]
    return h[0]["friendlyUrl"]
urls = {k: best(v) for k, v in found.items()}
json.dump(urls, open(f"{OUT}/de_ww_urls.json", "w"))
vals = [u for u in urls.values() if u]
for i in range(0, len(vals), 25):
    get(f"{WW}/export/kinderarmut+" + "+".join(vals[i:i + 25]) + "+2021-2023+tabelle.csv", f"de_ww_chunk{i // 25:02d}.csv")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
