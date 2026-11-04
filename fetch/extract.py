# Temporary: Nordics + Netherlands part 3: the data (child low income, pupils).
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/nordic3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, */*"}
log = []
def get(url, name=None, data=None, ctype="application/json"):
    time.sleep(1.5)
    try:
        h = dict(UA); h["Content-Type"] = ctype
        with urllib.request.urlopen(urllib.request.Request(url, headers=h, data=data), timeout=600) as r:
            d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:170]}"); return d
    except Exception as e:
        body = ""
        try: body = e.read().decode()[:300]
        except Exception: pass
        log.append(f"FAIL {url[:170]}: {e} {body}"); return None
def pick(values, texts, pattern):
    for v, t in zip(values, texts):
        if re.search(pattern, t, re.I): return v
    return None
# ---- Norway: SSB PxWeb v0 (GET metadata, POST query)
def ssb(table, name, prefs):
    m = get(f"https://data.ssb.no/api/v0/no/table/{table}")
    if not m: return
    meta = json.loads(m); open(f"{OUT}/{name}_meta.json", "w").write(json.dumps(meta, ensure_ascii=False))
    q = []
    for v in meta["variables"]:
        code, vals, txts = v["code"], v["values"], v["valueTexts"]
        if code == "Region":
            q.append({"code": code, "selection": {"filter": "all", "values": ["*"]}})
        elif code == "Tid":
            q.append({"code": code, "selection": {"filter": "item", "values": vals[-1:]}})
        else:
            pat = prefs.get(code)
            sel = pick(vals, txts, pat) if pat else None
            q.append({"code": code, "selection": {"filter": "item", "values": [sel] if sel else ([vals[0]] if code != "ContentsCode" else vals)}})
    get(f"https://data.ssb.no/api/v0/no/table/{table}", f"{name}.json", data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode())
ssb("12944", "no_lowincome", {"Alder": r"0-17|under 18", "ContentsCode": r"prosent|andel"})
ssb("11980", "no_pupils", {"EierforhGrsk": r"i alt|alle", "Klassetrinn": r"i alt|1\.-10|alle"})
# ---- Sweden: SCB PxWebApi v2 (TAB6685 low economic standard by region and age); Kolada for pupils
m = get("https://statistikdatabasen.scb.se/api/v2/tables/TAB6685/metadata?lang=sv", "se_TAB6685_meta.json")
if m:
    meta = json.loads(m); dims = meta.get("dimension", {}); ids = meta.get("id", [])
    params = {}
    for d in ids:
        cats = dims[d]["category"]; keys = list(cats["index"].keys()) if isinstance(cats["index"], dict) else cats["index"]
        labels = cats.get("label", {})
        if d.lower() == "region": params[f"valueCodes[{d}]"] = "*"
        elif d.lower() in ("tid", "time"): params[f"valueCodes[{d}]"] = keys[-1]
        else:
            k = pick(keys, [labels.get(k, k) for k in keys], r"0-17|0–17|0-19") if d.lower().startswith("ald") else None
            params[f"valueCodes[{d}]"] = k or ",".join(keys)
    get("https://statistikdatabasen.scb.se/api/v2/tables/TAB6685/data?lang=sv&outputFormat=csv&" + urllib.parse.urlencode(params), "se_lowincome.csv")
d = get("https://api.kolada.se/v2/kpi?" + urllib.parse.urlencode({"title": "elever i grundskola"}))
if d:
    kpis = json.loads(d).get("values", [])
    open(f"{OUT}/se_kolada_kpis.json", "w").write(json.dumps([(k["id"], k["title"]) for k in kpis], ensure_ascii=False, indent=1))
    ks = [k for k in kpis if re.search(r"^elever i grundskola", k["title"], re.I) and re.search(r"antal", k["title"], re.I)] or kpis[:1]
    for k in ks[:2]:
        for y in (2025, 2024):
            r = get(f"https://api.kolada.se/v2/data/kpi/{k['id']}/year/{y}", f"se_pupils_{k['id']}_{y}.json")
            if r and json.loads(r).get("values"): break
d = get("https://api.kolada.se/v2/municipality")
if d: open(f"{OUT}/se_kolada_municipalities.json", "wb").write(d)
# ---- Denmark: Statbank (LABY07 relative poverty 0-17; LABY23 pupils)
for t in ("LABY07", "LABY23"):
    i = get(f"https://api.statbank.dk/v1/tableinfo/{t}?lang=en&format=JSON", f"dk_{t}_info.json")
    if not i: continue
    info = json.loads(i); vars_ = []
    for v in info["variables"]:
        ids_ = [x["id"] for x in v["values"]]; txt = [x["text"] for x in v["values"]]
        if v["id"] in ("KOMGRP", "OMRÅDE", "KOMMUNEDK"): sel = ["*"]
        elif v["id"] == "Tid": sel = ids_[-1:]
        elif v["id"] == "ALDER": sel = [pick(ids_, txt, r"0-17") or ids_[0]]
        else: sel = [ids_[0]]
        vars_.append({"code": v["id"], "values": sel})
    get("https://api.statbank.dk/v1/data", f"dk_{t}.csv", data=json.dumps({"table": t, "format": "CSV", "lang": "en", "variables": vars_}).encode())
# ---- Finland: Sotkanet pupils indicator search + data
d = get("https://sotkanet.fi/rest/1.1/indicators")
if d:
    ind = [(i["id"], i.get("title", {}).get("fi"), i.get("title", {}).get("en")) for i in json.loads(d) if re.search(r"peruskoulu|perusopetu", json.dumps(i.get("title", {}), ensure_ascii=False), re.I) and re.search(r"oppila", json.dumps(i.get("title", {}), ensure_ascii=False), re.I)]
    open(f"{OUT}/fi_pupil_indicators.json", "w").write(json.dumps(ind, ensure_ascii=False, indent=1))
get("https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/opiskt/statfin_opiskt_pxt_133w.px", "fi_133w_meta.json")
get("https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/opiskt/", "fi_opiskt_list.json")
# ---- Netherlands: CBS OData (86132NED child poverty; 85701NED pupils by residence)
for t, dims in (("86132NED", ["PersoonsEnHuishoudenskenmerken", "Perioden"]), ("85701NED", ["Geslacht", "Onderwijssoort", "Regiokenmerken", "Perioden"])):
    for dim in dims:
        get(f"https://opendata.cbs.nl/ODataApi/odata/{t}/{dim}?$format=json", f"nl_{t}_{dim}.json")
p = json.loads(open(f"{OUT}/nl_86132NED_PersoonsEnHuishoudenskenmerken.json").read())["value"] if os.path.exists(f"{OUT}/nl_86132NED_PersoonsEnHuishoudenskenmerken.json") else []
tot = next((x["Key"].strip() for x in p if re.search(r"totaal", x["Title"], re.I)), p[0]["Key"].strip() if p else "")
f = urllib.parse.quote(f"PersoonsEnHuishoudenskenmerken eq '{tot}' and (Perioden eq '2023JJ00' or Perioden eq '2024JJ00')")
get(f"https://opendata.cbs.nl/ODataApi/odata/86132NED/TypedDataSet?$format=json&$filter={f}", "nl_childpoverty.json")
get("https://opendata.cbs.nl/ODataApi/odata/85701NED/TypedDataSet?$format=json&$top=1", "nl_85701_sample.json")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
