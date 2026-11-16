import os, json, urllib.request, urllib.parse, re
OUT = "fetch/out/disc7"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(name, url, keep=80000000, show=600, data=None):
    try:
        h = dict(UA)
        if data is not None: h["Content-Type"] = "application/json"; data = json.dumps(data).encode()
        with urllib.request.urlopen(urllib.request.Request(url, headers=h, data=data), timeout=600) as r: b = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(b[:keep])
        log.write(f"== {name} OK {len(b)} {url}\n{b[:show].decode('utf-8','replace')}\n\n"); return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n\n"); return None
def safe(f):
    try: f()
    except Exception as e: log.write(f"SECTION ERR {f.__name__}: {e}\n")
DUO = "https://onderwijsdata.duo.nl"
def nl():
    for pid in ["786f12ea-6224-42fd-ab72-de4d7d879535", "033ab279-8e6f-44a2-8455-6ad42147762f", "c8e6ffdd-cc2b-44ee-880f-0ff03f72e868",
                "173cbf21-1567-464a-bccd-518cd7a46bd0", "19c81dcb-a7c5-4410-8122-145f0996d082", "e3ab98c0-881a-413a-ba8a-676dd1313593"]:
        p = json.loads(get(None, f"{DUO}/api/3/action/package_show?id={pid}", show=0))["result"]
        for r in p["resources"]:
            url = re.sub(r"^https://beheer-ggm-ckan-prd\.apps\.prd\.duo\.rijksapps\.nl", DUO, r["url"])
            log.write(f"DUO {p['title']} | {r.get('name')} | {url}\n")
            if re.search(r"vestiging|voins|cumi|brin6", (r.get("name") or "") + url, re.I) and url.endswith(".csv"):
                get("nl_" + re.sub(r"[^a-z0-9]+", "_", (r.get("name") or "x").lower())[:60] + ".csv", url, show=500)
def fwb():
    for ds in ["spe-type-v3", "ord-niveau-degre-annee-v3", "spe-secondaire-par-forme-v3", "ord-d2d3-section-et-forme-v3",
               "fwb-age_classes-dise-pour-les-implantations-scolaires", "fwb-age-fichier-signaletique-des-etablissements-d-enseignement-de-la-federation-"]:
        m = json.loads(get(None, f"https://www.odwb.be/api/explore/v2.1/catalog/datasets/{ds}", show=0))
        log.write(f"ODWB {ds}: {m['metas']['default'].get('title')} | {[f['name'] for f in m.get('fields', [])]}\n")
        get(f"fwb_{ds[:30]}_sample.json", f"https://www.odwb.be/api/explore/v2.1/catalog/datasets/{ds}/records?limit=3", show=2500)
def lv():
    base = "https://data.stat.gov.lv/api/v1/en/OSP_PUB/VES/PP/PPS/PPS040"
    meta = json.loads(get(None, base, show=0))
    q = {"query": [{"code": v["code"], "selection": {"filter": "all", "values": ["*"]}} for v in meta["variables"] if v["code"] != "TIME"] +
                  [{"code": "TIME", "selection": {"filter": "top", "values": ["3"]}}], "response": {"format": "json-stat2"}}
    get("lv_pps040.json", base, data=q, show=300)
    base = "https://data.stat.gov.lv/api/v1/en/OSP_PUB/POP/IR/IRD/IRD041"
    meta = json.loads(get(None, base, show=0)); log.write("IRD041 vars " + json.dumps([(v["code"], v["values"][:30]) for v in meta["variables"]]) + "\n")
    q = {"query": [{"code": "TIME", "selection": {"filter": "top", "values": ["1"]}}, {"code": "SEX", "selection": {"filter": "item", "values": ["T"]}}], "response": {"format": "json-stat2"}}
    get("lv_ird041.json", base, data=q, show=300)
    for qq in ["izglītojamo skaits", "vispārējās izglītības iestādes", "skolēnu skaits"]:
        b = get(None, "https://data.gov.lv/dati/api/3/action/package_search?q=" + urllib.parse.quote(qq) + "&rows=8", show=0)
        for p in json.loads(b)["result"]["results"]:
            log.write(f"LVDATA[{qq}] {p['title']}: " + " ; ".join(f"{r.get('name')} {r.get('url')}" for r in p["resources"][:4]) + "\n")
def ee():
    q = {"query": [{"code": "Aasta", "selection": {"filter": "item", "values": ["2024", "2025"]}}], "response": {"format": "json-stat2"}}
    get("ee_sk410.json", "https://andmed.stat.ee/api/v1/en/stat/SK410", data=q, show=300)
    for path in ["/rahvastik/rahvastikunaitajad-ja-koosseis/rahvaarv-ja-rahvastiku-koosseis", "/haridus/uldharidus", "/haridus"]:
        b = get(None, "https://andmed.stat.ee/api/v1/en/stat" + path, show=0)
        try:
            for it in json.loads(b): log.write(f"EE {path}/{it['id']} [{it['type']}] {it['text']}\n")
        except Exception as e: log.write(f"EE {path} ERR {e}\n")
    for qq in ["õpilaste arv", "üldhariduskoolid"]:
        get(None, "https://avaandmed.eesti.ee/api/datasets?search=" + urllib.parse.quote(qq), show=1500)
for f in (nl, fwb, lv, ee): safe(f)
