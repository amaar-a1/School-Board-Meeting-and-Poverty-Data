import os, sys, json, urllib.request, urllib.parse, re, subprocess, time
try:
    import yt_dlp  # noqa
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", "-q", "yt-dlp"], check=False)
    os.execv(sys.executable, [sys.executable] + sys.argv)
OUT = "fetch/out/disc8"; os.makedirs(OUT, exist_ok=True)
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
    log.flush()
def lv():
    base = "https://data.stat.gov.lv/api/v1/en/OSP_PUB/POP/IR/IRD/IRD041"
    meta = json.loads(get(None, base, show=0))
    log.write("IRD041 " + json.dumps([(v["code"], v["values"][:120], v["valueTexts"][:120]) for v in meta["variables"]], ensure_ascii=False)[:6000] + "\n")
    q = {"query": [{"code": v["code"], "selection": {"filter": "all", "values": ["*"]}} for v in meta["variables"] if v["code"] not in ("TIME", "SEX")] +
                  [{"code": "SEX", "selection": {"filter": "item", "values": [meta["variables"][[v["code"] for v in meta["variables"]].index("SEX")]["values"][0]]}},
                   {"code": "TIME", "selection": {"filter": "top", "values": ["1"]}}], "response": {"format": "json-stat2"}}
    get("lv_ird041.json", base, data=q, show=200)
    for n, u in [("lv_pupils_by_school_20251001.csv", "https://data.gov.lv/dati/lv/dataset/3ef3dea2-20e6-47ae-addc-2f55d11f7be2/resource/a3450196-a7be-4378-a9ac-fbca6f64e16b/download/izglitojamoskvispizglprogrpaprogr_01102025.csv"),
                 ("lv_special_by_muni_20251001.csv", "https://data.gov.lv/dati/dataset/b9bbd166-0ae6-423e-aed3-3a77f2a58f91/resource/ca236c1e-7dc0-46f5-ba98-a46e3d29f870/download/izglitojamoskvispizglprogrpapasvaldibam_01102025.csv")]:
        get(n, u, show=1200)
def ee():
    meta = json.loads(get(None, "https://andmed.stat.ee/api/v1/en/stat/SK410", show=0))
    q = {"query": [{"code": "Aasta", "selection": {"filter": "item", "values": ["2023", "2024", "2025"]}},
                   {"code": "Piirkond/Haldusüksus", "selection": {"filter": "all", "values": ["*"]}},
                   {"code": "Näitaja", "selection": {"filter": "all", "values": ["*"]}}], "response": {"format": "json-stat2"}}
    get("ee_sk410.json", "https://andmed.stat.ee/api/v1/en/stat/SK410", data=q, show=200)
    meta = json.loads(get(None, "https://andmed.stat.ee/api/v1/en/stat/RV0240", show=0))
    log.write("RV0240 " + json.dumps([(v["code"], v["values"][:30], v["valueTexts"][:30]) for v in meta["variables"]], ensure_ascii=False)[:5000] + "\n")
    sel = []
    for v in meta["variables"]:
        if v.get("time"): sel.append({"code": v["code"], "selection": {"filter": "top", "values": ["1"]}})
        elif re.search(r"sex|sugu", v["text"], re.I): sel.append({"code": v["code"], "selection": {"filter": "item", "values": [v["values"][0]]}})
        else: sel.append({"code": v["code"], "selection": {"filter": "all", "values": ["*"]}})
    get("ee_rv0240.json", "https://andmed.stat.ee/api/v1/en/stat/RV0240", data={"query": sel, "response": {"format": "json-stat2"}}, show=200)
    for t in ["HT", "HTG", "HTE"]:
        b = get(None, "https://andmed.stat.ee/api/v1/en/stat/haridus/uldharidus", show=0)
    try:
        for it in json.loads(b): log.write(f"EEH {it['id']} [{it['type']}] {it['text']}\n")
    except Exception as e: log.write(f"EEH ERR {e}\n")
def nl():
    for qq in ["leerlingen vo vestiging", "vo leerlingen per vestiging onderwijstype", "aantal leerlingen voortgezet onderwijs"]:
        b = get(None, "https://onderwijsdata.duo.nl/api/3/action/package_search?q=" + urllib.parse.quote(qq) + "&rows=15", show=0)
        for p in json.loads(b)["result"]["results"]:
            log.write(f"DUO[{qq}] {p['title']} (modified {p.get('metadata_modified')}): " + " ; ".join(f"{r.get('name')} {r.get('url')}" for r in p["resources"][:3]) + "\n")
for f in (lv, ee, nl): safe(f)
# YouTube: council and education-committee meetings, Latvia and Estonia
env = dict(os.environ, NORDIC_DATA="fetch", NORDIC_DEADLINE=str(time.time() + 3000))
r = subprocess.run([sys.executable, "fetch/nordic_youtube.py", OUT + "/yt", "LV", "EE"], env=env, capture_output=True, text=True, timeout=3600)
log.write("YT rc %s\n%s\n%s\n" % (r.returncode, r.stdout[-3000:], r.stderr[-2000:]))
