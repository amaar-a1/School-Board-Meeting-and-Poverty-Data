# Temporary: Switzerland part 3: social assistance by canton and age; compulsory-school pupils by canton.
import json, os, re, time, urllib.request
OUT = "fetch/out/ch3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json", "Content-Type": "application/json"}
B = "https://www.pxweb.bfs.admin.ch/api/v1/de/"
log = []
def table(tid, keepall):
    u = f"{B}{tid}/{tid}.px"
    meta = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read())
    json.dump(meta, open(f"{OUT}/{tid}_meta.json", "w"), ensure_ascii=False)
    q = []
    for v in meta["variables"]:
        if re.search(keepall, v["text"], re.I): vals = v["values"]
        elif re.search(r"^jahr", v["text"], re.I): vals = v["values"][-2:]
        else: vals = [v["values"][0]]
        q.append({"code": v["code"], "selection": {"filter": "item", "values": vals}})
    body = json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode()
    try:
        d = urllib.request.urlopen(urllib.request.Request(u, headers=UA, data=body), timeout=300).read()
        open(f"{OUT}/{tid}.json", "wb").write(d); log.append(f"ok {tid} {len(d)}")
    except Exception as e:
        b = ""
        try: b = e.read().decode()[:300]
        except Exception: pass
        log.append(f"FAIL {tid} {e} {b}")
    time.sleep(1)
table("px-x-1304030000_121", r"kanton|altersklasse|absolut")
table("px-x-1502010100_101", r"kanton")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
