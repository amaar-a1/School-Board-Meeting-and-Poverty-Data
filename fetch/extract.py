# Temporary: e-Stat: latest School Basic Survey municipal files: elementary (児童数) and lower secondary (中学校 生徒数)
# pupils by municipality, total and private; download and describe.
import json, os, re, subprocess, sys, urllib.parse, urllib.request
OUT = "fetch/out/estat5"; os.makedirs(OUT, exist_ok=True)
try:
    import xlrd, openpyxl
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "xlrd", "openpyxl"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
log = open(f"{OUT}/log.txt", "w")
key = os.environ.get("ESTAT_APP_ID", "")
def api(path, **q):
    q["appId"] = key
    u = f"https://api.e-stat.go.jp/rest/3.0/app/json/{path}?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "school-board research project"}), timeout=120) as r:
        return json.loads(r.read())
items = []
for word in ["市町村別学年別児童数", "市町村別学年別生徒数"]:
    d = api("getDataCatalog", statsCode="00400001", searchWord=word, dataType="XLS", limit=200, surveyYears="201801-202612")
    its = d["GET_DATA_CATALOG"].get("DATA_CATALOG_LIST_INF", {}).get("DATA_CATALOG_INF", []); its = its if isinstance(its, list) else [its]
    for it in its:
        ds = it.get("DATASET", {}); dt = ds.get("TITLE", {}); dtitle = json.dumps(dt, ensure_ascii=False)[:200]
        res = it.get("RESOURCES", {}).get("RESOURCE", []); res = res if isinstance(res, list) else [res]
        for r in res:
            t = r.get("TITLE", {}); name = t.get("NAME") if isinstance(t, dict) else str(t)
            sid = re.search(r"statInfId=(\d+)", r.get("URL", "")); 
            items.append({"name": name, "url": r.get("URL"), "sid": sid.group(1) if sid else "", "dataset": dtitle, "survey": ds.get("SURVEY_DATE"), "released": r.get("RELEASE_DATE")})
for it in sorted(items, key=lambda x: x["sid"], reverse=True)[:30]: log.write(f"{it['sid']} | {it['released']} | {it['name']} | {it['dataset'][:160]}\n")
def pick(kind, sector):
    c = [x for x in items if f"市町村別学年別{kind}" in x["name"] and x["name"].endswith(sector) and ("中学校" in x["dataset"] if kind == "生徒数" else True)]
    return max(c, key=lambda x: x["sid"]) if c else None
got = {}
for kind, label in (("児童数", "el"), ("生徒数", "ls")):
    for sector, s in (("計", "total"), ("私立", "private")):
        p = pick(kind, sector)
        if not p: log.write(f"none for {kind} {sector}\n"); continue
        b = urllib.request.urlopen(urllib.request.Request(p["url"], headers={"User-Agent": "school-board research project"}), timeout=120).read()
        fn = f"{OUT}/{label}_{s}_{p['sid']}.xls" + ("x" if b[:2] == b"PK" else "")
        open(fn, "wb").write(b); got[f"{label}_{s}"] = fn
        log.write(f"GOT {label} {s}: {p['sid']} {p['name']} {p['released']} {len(b)} bytes {p['dataset'][:120]}\n")
        try:
            if fn.endswith("x"):
                ws = openpyxl.load_workbook(fn, read_only=True, data_only=True).active; rows = [list(r) for r in ws.iter_rows(max_row=14, values_only=True)]
            else:
                sh = xlrd.open_workbook(fn).sheet_by_index(0); rows = [sh.row_values(i) for i in range(min(14, sh.nrows))]
            for r in rows: log.write("   " + str([str(c)[:16] for c in r[:12]]) + "\n")
        except Exception as e: log.write(f"   read ERR {e}\n")
json.dump(got, open(f"{OUT}/files.json", "w"))
log.close()
