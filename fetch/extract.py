# Temporary: Nordics part 5: Finland pupils (totals), Sweden pupils and child low income.
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/nordic5"; os.makedirs(OUT, exist_ok=True)
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
# Finland: 133w, every municipality, totals elsewhere, latest year
q = [{"code": "alue_23_20250101", "selection": {"filter": "all", "values": ["*"]}}] + \
    [{"code": c, "selection": {"filter": "item", "values": ["SSS"]}} for c in ("kieli_15_20180102", "vluokka_2_20180101", "sukupuoli_9_20180101", "oppilaittostyyp_6_20180101")] + \
    [{"code": "timeperiod_y", "selection": {"filter": "item", "values": ["2025"]}}, {"code": "contentscode", "selection": {"filter": "item", "values": ["oppil_lkm1"]}}]
get("https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/opiskt/133w.px", "fi_pupils.json", data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode())
# Sweden pupils: Kolada N15835 (compulsory school F-9, home municipality)
for y in (2025, 2024):
    r = get(f"https://api.kolada.se/v3/data/kpi/N15835/year/{y}", f"se_pupils_N15835_{y}.json")
    if r and json.loads(r).get("values"): break
# Sweden child low income: SCB v2 POST selection (municipalities, ages 0-19, latest year)
meta = json.load(open("fetch/out/nordic3/se_TAB6685_meta.json"))
regs = [k for k in meta["dimension"]["Region"]["category"]["index"] if re.fullmatch(r"\d{4}", k)]
tid = list(meta["dimension"]["Tid"]["category"]["index"])[-1]
body = {"selection": [{"variableCode": "Region", "valueCodes": regs}, {"variableCode": "Alder", "valueCodes": ["0-19"]},
                      {"variableCode": "ContentsCode", "valueCodes": ["000008AC", "000008AE"]}, {"variableCode": "Tid", "valueCodes": [tid]}]}
get("https://statistikdatabasen.scb.se/api/v2/tables/TAB6685/data?lang=sv&outputFormat=csv", "se_lowincome.csv", data=json.dumps(body).encode())
# Kolada fallback: KPIs on children in economically vulnerable households / low economic standard
for t in ("ekonomiskt utsatta", "låg ekonomisk standard", "barnfattigdom"):
    get("https://api.kolada.se/v3/kpi?" + urllib.parse.urlencode({"title": t}), f"se_kolada_{t.split()[0]}.json")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
