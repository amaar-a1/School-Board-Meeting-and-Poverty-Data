# Temporary: Nordics + Netherlands part 4: corrected data queries.
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/nordic4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, */*"}
log = []
def get(url, name=None, data=None):
    time.sleep(1.5)
    try:
        h = dict(UA); h["Content-Type"] = "application/json"
        with urllib.request.urlopen(urllib.request.Request(url, headers=h, data=data), timeout=600) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:170]}"); return d
    except Exception as e:
        body = ""
        try: body = e.read().decode()[:300]
        except Exception: pass
        log.append(f"FAIL {url[:170]}: {e} {body}"); return None
def ssb(table, name, choose):
    meta = json.loads(get(f"https://data.ssb.no/api/v0/no/table/{table}"))
    q = []
    for v in meta["variables"]:
        c, vals, txt = v["code"], v["values"], v["valueTexts"]
        if "region" in c.lower(): sel = ("all", ["*"])
        elif c == "Tid": sel = ("item", vals[-1:])
        elif c in choose: sel = ("item", [x for x, t in zip(vals, txt) if re.search(choose[c], t, re.I)] or vals[:1])
        else: sel = ("item", vals)
        q.append({"code": c, "selection": {"filter": sel[0], "values": sel[1]}})
    get(f"https://data.ssb.no/api/v0/no/table/{table}", f"{name}.json", data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode())
ssb("12944", "no_lowincome", {"Alder": r"^0-17"})
ssb("11980", "no_pupils", {"KOKeierfh0000": r"og privat", "KOKtrinn0000": r"alle trinn"})
# Sweden: municipalities only, ages 0-19, share with low economic standard, latest year
meta = json.load(open("fetch/out/nordic3/se_TAB6685_meta.json"))
regs = [k for k in meta["dimension"]["Region"]["category"]["index"] if re.fullmatch(r"\d{4}", k)]
tid = list(meta["dimension"]["Tid"]["category"]["index"])[-1]
params = {"valueCodes[Region]": ",".join(regs), "valueCodes[Alder]": "0-19", "valueCodes[ContentsCode]": "000008AC,000008AE", "valueCodes[Tid]": tid}
get("https://statistikdatabasen.scb.se/api/v2/tables/TAB6685/data?lang=sv&outputFormat=csv&" + urllib.parse.urlencode(params), "se_lowincome.csv")
# Sweden pupils: Kolada v3
d = get("https://api.kolada.se/v3/kpi?" + urllib.parse.urlencode({"title": "elever i grundskola"}), "se_kolada_kpi_search.json")
if d:
    kpis = json.loads(d).get("values", [])
    ks = [k for k in kpis if re.search(r"antal", k.get("title", ""), re.I)] or kpis
    for k in ks[:3]:
        for y in (2025, 2024):
            r = get(f"https://api.kolada.se/v3/data/kpi/{k['id']}/year/{y}", f"se_pupils_{k['id']}_{y}.json")
            if r and json.loads(r).get("values"): break
get("https://api.kolada.se/v3/municipality", "se_kolada_municipalities.json")
# Finland: comprehensive school pupils by municipality
for u in ["https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/opiskt/133w.px", "https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/opiskt/statfin_opiskt_pxt_133w.px",
          "https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/opiskt/15fe.px", "https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/opiskt/13jn.px"]:
    m = get(u)
    if m:
        open(f"{OUT}/fi_{u.split('/')[-1]}_meta.json", "wb").write(m)
        meta = json.loads(m); q = []
        for v in meta["variables"]:
            c, vals, txt = v["code"], v["values"], v["valueTexts"]
            if re.search(r"kunta|alue|maakunta", c + v["text"], re.I): sel = ("all", ["*"])
            elif re.search(r"vuosi|year", c + v["text"], re.I): sel = ("item", vals[-1:])
            else: sel = ("item", [x for x, t in zip(vals, txt) if re.search(r"yhteensä|kaikki|total|SSS", t, re.I)][:1] or vals[:1])
            q.append({"code": c, "selection": {"filter": sel[0], "values": sel[1]}})
        get(u, f"fi_pupils_{u.split('/')[-1]}.json", data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode())
# Netherlands: pupils by municipality of residence, 2025/26
f = urllib.parse.quote("Geslacht eq 'T001038' and Perioden eq '2025SJ00' and (Onderwijssoort eq 'A025279' or Onderwijssoort eq 'A025282' or Onderwijssoort eq 'T001345') and substringof('GM',Regiokenmerken)")
get(f"https://opendata.cbs.nl/ODataApi/odata/85701NED/TypedDataSet?$format=json&$filter={f}", "nl_pupils.json")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
