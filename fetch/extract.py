# Temporary: e-Stat data catalogue: newer School Basic Survey municipal pupil files (Excel) and their URLs.
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/estat3"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
key = os.environ.get("ESTAT_APP_ID", "")
def api(path, **q):
    q["appId"] = key
    u = f"https://api.e-stat.go.jp/rest/3.0/app/json/{path}?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "school-board research project"}), timeout=120) as r:
        return json.loads(r.read())
out = []
for word in ["市町村別 児童数", "市町村別 生徒数", "市町村別集計"]:
    try:
        d = api("getDataCatalog", statsCode="00400001", searchWord=word, dataType="XLS", limit=100, surveyYears="2020-2026")
        dl = d["GET_DATA_CATALOG"].get("DATA_CATALOG_LIST_INF", {})
        log.write(f"[{word}] {d['GET_DATA_CATALOG']['RESULT'].get('ERROR_MSG')} n={dl.get('NUMBER')}\n")
        items = dl.get("DATA_CATALOG_INF", []); items = items if isinstance(items, list) else [items]
        for it in items:
            ds = it.get("DATASET", {}); res = it.get("RESOURCES", {}).get("RESOURCE", [])
            res = res if isinstance(res, list) else [res]
            for r in res:
                t = r.get("TITLE", {}); name = t.get("NAME") if isinstance(t, dict) else t
                out.append((ds.get("SURVEY_DATE"), str(name)[:110], r.get("URL"), r.get("FORMAT")))
    except Exception as e: log.write(f"ERR {word} {str(e)[:200]}\n")
seen = set()
for dt, name, url, fmt in sorted(out, key=lambda x: str(x[0]), reverse=True):
    if (name, url) in seen: continue
    seen.add((name, url))
    if any(k in name for k in ("児童数", "生徒数")): log.write(f"{dt} | {fmt} | {name} | {url}\n")
log.close()
