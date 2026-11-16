import os, json, urllib.request
OUT = "fetch/out/disc9"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
B = "https://www.pxweb.bfs.admin.ch/api/v1/de/"
lst = json.loads(urllib.request.urlopen(urllib.request.Request(B, headers=UA), timeout=120).read())
for t in [x["dbid"] for x in lst if x["dbid"].startswith("px-x-1502")]:
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(f"{B}{t}/{t}.px", headers=UA), timeout=120).read())
        codes = [v["code"] for v in d["variables"]]
        log.write(f"{t}: {d.get('title')} | " + " | ".join(f"{v['code']}[{len(v['values'])}]" for v in d["variables"]) + "\n")
        if any("anton" in c for c in codes) and any(("harakter" in c) or ("räger" in c) or ("Träger" in c) for c in codes):
            log.write("   MATCH " + json.dumps([(v["code"], v["valueTexts"][:30]) for v in d["variables"]], ensure_ascii=False)[:3000] + "\n")
    except Exception as e: log.write(f"{t}: ERR {e}\n")
