# Temporary: e-Stat API (key from the ESTAT_APP_ID secret, never printed): find School Basic Survey (学校基本調査,
# statsCode 00400001) tables with pupils by municipality and by establisher (国立・公立・私立).
import json, os, urllib.parse, urllib.request
OUT = "fetch/out/estat1"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
key = os.environ.get("ESTAT_APP_ID", "")
log.write(f"key present: {bool(key)}\n")
def api(path, **q):
    q["appId"] = key
    u = f"https://api.e-stat.go.jp/rest/3.0/app/json/{path}?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "school-board research project"}), timeout=120) as r:
        return json.loads(r.read())
seen = {}
for word in ["市町村別 児童数", "市町村別 生徒数", "市区町村 設置者", "市町村 小学校", "市町村 中学校"]:
    try:
        d = api("getStatsList", statsCode="00400001", searchWord=word, limit=60)
        res = d["GET_STATS_LIST"]["RESULT"]; log.write(f"[{word}] status {res.get('STATUS')} {res.get('ERROR_MSG','')}\n")
        tabs = d["GET_STATS_LIST"].get("DATALIST_INF", {}).get("TABLE_INF", [])
        tabs = tabs if isinstance(tabs, list) else [tabs]
        for t in tabs:
            tid = t["@id"]
            if tid in seen: continue
            title = t.get("TITLE", {}); title = title.get("$", "") if isinstance(title, dict) else title
            seen[tid] = f'{t.get("SURVEY_DATE")} | {t.get("STATISTICS_NAME","")[:40]} | {title}'
    except Exception as e: log.write(f"ERR {word} {str(e)[:150]}\n")
for k, v in sorted(seen.items(), key=lambda x: x[1], reverse=True)[:150]: log.write(f"{k} | {v}\n")
log.close()
