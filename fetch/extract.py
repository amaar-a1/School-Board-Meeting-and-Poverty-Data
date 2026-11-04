# Temporary: Iceland part 3: child low income by residence, children by municipality, unemployment page.
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/is3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, text/html, */*"}
log = []
def get(url, name=None, data=None):
    time.sleep(1.2)
    try:
        h = dict(UA)
        if data: h["Content-Type"] = "application/json"
        d = urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%"), headers=h, data=data), timeout=300).read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:200]}"); return d
    except Exception as e:
        body = ""
        try: body = e.read().decode()[:300]
        except Exception: pass
        log.append(f"FAIL {url[:200]}: {e} {body}"); return None
HG = "https://px.hagstofa.is/pxis/api/v1/is/"
def table(path, name, pick):
    m = get(HG + path)
    if not m: return
    meta = json.loads(m); open(f"{OUT}/{name}_meta.json", "w").write(json.dumps(meta, ensure_ascii=False))
    q = []
    for v in meta["variables"]:
        vals = pick(v)
        if vals is not None: q.append({"code": v["code"], "selection": {"filter": "item", "values": vals}})
    get(HG + path, f"{name}.json", data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode())
last = lambda v: v["values"][-3:] if v.get("time") or re.search(r"ár|year", v["text"], re.I) else None
table("Samfelag/lifskjor/3_fjarhagsstada/1_einstaklingar/LIF01140.px", "is_child_lowincome", lambda v: v["values"][-4:] if v.get("time") or re.search(r"^ár", v["text"], re.I) else v["values"])
def popsel(v):
    if v.get("time") or re.search(r"^ár", v["text"], re.I): return v["values"][-1:]
    if re.search(r"aldur", v["text"], re.I):
        return [x for x, t in zip(v["values"], v["valueTexts"]) if re.fullmatch(r"([6-9]|1[0-5]) ár[sa]?", t.strip()) or t.strip() in ("Alls", "Samtals")]
    if re.search(r"kyn", v["text"], re.I): return [x for x, t in zip(v["values"], v["valueTexts"]) if t.strip() in ("Alls", "Samtals")] or v["values"][:1]
    return v["values"]
table("Ibuar/mannfjoldi/2_byggdir/sveitarfelog/MAN02005.px", "is_pop", popsel)
get("https://island.is/s/vinnumalastofnun/maelabord-og-toelulegar-upplysingar", "vmst_stats.html")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
