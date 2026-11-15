# Temporary: e-Stat: every year of the School Basic Survey's municipal pupil tables, and the dimensions of the latest.
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/estat2"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
key = os.environ.get("ESTAT_APP_ID", "")
def api(path, **q):
    q["appId"] = key
    u = f"https://api.e-stat.go.jp/rest/3.0/app/json/{path}?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "school-board research project"}), timeout=120) as r:
        return json.loads(r.read())
found = {}
for word in ["市町村別集計 学年別児童数", "市町村別集計 学年別生徒数"]:
    start = 1
    while start:
        d = api("getStatsList", statsCode="00400001", searchWord=word, limit=100, startPosition=start)
        dl = d["GET_STATS_LIST"].get("DATALIST_INF", {})
        tabs = dl.get("TABLE_INF", []); tabs = tabs if isinstance(tabs, list) else [tabs]
        for t in tabs:
            title = t.get("TITLE", {}); title = title.get("$", "") if isinstance(title, dict) else title
            found[t["@id"]] = (t.get("SURVEY_DATE"), title)
        nxt = dl.get("RESULT_INF", {}).get("NEXT_KEY"); start = int(nxt) if nxt else 0
for k, (dt, title) in sorted(found.items(), key=lambda x: str(x[1][0]), reverse=True)[:40]: log.write(f"{k} | {dt} | {title}\n")
el = [k for k, (dt, t) in sorted(found.items(), key=lambda x: str(x[1][0]), reverse=True) if "小学校" in t and "学年別児童数" in t]
if el:
    m = api("getMetaInfo", statsDataId=el[0])
    for c in m["GET_META_INFO"]["METADATA_INF"]["CLASS_INF"]["CLASS_OBJ"]:
        cls = c["CLASS"] if isinstance(c["CLASS"], list) else [c["CLASS"]]
        log.write(f"META {el[0]} {c['@id']} {c['@name']}: {len(cls)} | {[x['@name'] for x in cls[:12]]}\n")
log.close()
