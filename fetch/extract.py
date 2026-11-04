# Temporary: Iceland part 4: check LIF01140 categories one at a time.
import json, os, urllib.request
OUT = "fetch/out/is4"; os.makedirs(OUT, exist_ok=True)
U = "https://px.hagstofa.is/pxis/api/v1/is/Samfelag/lifskjor/3_fjarhagsstada/1_einstaklingar/LIF01140.px"
res = {}
for b in ("0", "1", "2"):
    q = {"query": [{"code": "Ár", "selection": {"filter": "item", "values": ["2021"]}}, {"code": "Búseta", "selection": {"filter": "item", "values": [b]}},
                   {"code": "Gildi", "selection": {"filter": "item", "values": ["0"]}}], "response": {"format": "json"}}
    r = urllib.request.Request(U, data=json.dumps(q).encode(), headers={"Content-Type": "application/json", "User-Agent": "school-board-research-script"})
    res[b] = json.loads(urllib.request.urlopen(r, timeout=120).read())
for fmt in ("csv",):
    q = {"query": [{"code": "Ár", "selection": {"filter": "item", "values": ["2020", "2021"]}}], "response": {"format": fmt}}
    r = urllib.request.Request(U, data=json.dumps(q).encode(), headers={"Content-Type": "application/json", "User-Agent": "school-board-research-script"})
    open(f"{OUT}/lif01140.csv", "wb").write(urllib.request.urlopen(r, timeout=120).read())
json.dump(res, open(f"{OUT}/check.json", "w"), ensure_ascii=False)
