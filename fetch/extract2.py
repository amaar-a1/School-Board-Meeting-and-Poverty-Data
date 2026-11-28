import urllib.parse
# Round 67: residents enrolled in public and private school (kindergarten to grade 12), by school district, from the
# Census Bureau's American Community Survey 2019-2023 (table B14002: school enrollment by level and type of school),
# for every unified, elementary and secondary school district. For districts with no schools of their own (Maine's
# unorganized territories, New Hampshire's and Vermont's tuition towns), which the NCES school counts leave out.
import os, json, urllib.request, time
OUT = "fetch/out/c67"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "school-board-research-project/1.0 (github.com/amaar-a1)"}
API = "https://api.census.gov/data/2023/acs/acs5"
def get(u):
    for i in range(3):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180).read())
        except Exception as e: err = e; time.sleep(5)
    raise err
g = get(f"{API}/groups/B14002.json")["variables"]
want = {}
for v, x in g.items():
    if not v.endswith("E"): continue
    lab = x["label"]
    if ("Kindergarten" in lab or "Grade 1 to grade 4" in lab or "Grade 5 to grade 8" in lab or "Grade 9 to grade 12" in lab) and ("Public school" in lab or "Private school" in lab):
        want[v] = "pub" if "Public school" in lab else "priv"
log.write(f"variables {len(want)}: {sorted(want)}\n")
vars_ = ",".join(sorted(want))
out = {}
for kind in ("unified", "elementary", "secondary"):
    try:
        rows = get(f"{API}?get=NAME,{vars_}&for=" + urllib.parse.quote(f"school district ({kind}):*") + "&in=state:*")
    except Exception as e:
        log.write(f"ERR {kind} {e}\n"); continue
    h = rows[0]
    for r in rows[1:]:
        d = dict(zip(h, r))
        code = d["state"] + d[f"school district ({kind})"]
        pub = sum(int(d[v]) for v in want if want[v] == "pub" and d[v] not in (None, "") and int(d[v]) >= 0)
        priv = sum(int(d[v]) for v in want if want[v] == "priv" and d[v] not in (None, "") and int(d[v]) >= 0)
        out[code] = {"name": d["NAME"], "kind": kind, "public": pub, "private": priv}
    log.write(f"OK {kind} {len(rows) - 1}\n"); log.flush(); time.sleep(2)
json.dump({"source": "ACS 2019-2023 5-year, table B14002 (K-12 enrollment of residents by type of school)", "districts": out}, open(f"{OUT}/acs_b14002_sd.json", "w"))
log.close()
