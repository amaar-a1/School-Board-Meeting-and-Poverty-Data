import urllib.parse
# Round 67c: residents enrolled in public and private school (kindergarten to grade 12), by school district, from the
# Census Bureau's American Community Survey 2019-2023 (table B14002: school enrollment by level and type of school),
# for every unified, elementary and secondary school district. For districts with no schools of their own (Maine's
# unorganized territories, New Hampshire's and Vermont's tuition towns), which the NCES school counts leave out.
import os, json, urllib.request, urllib.error, time
OUT = "fetch/out/c67"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "school-board-research-project/1.0 (github.com/amaar-a1)"}
API = "https://api.census.gov/data/2023/acs/acs5"
def get(u):
    body = b""
    for i in range(3):
        try:
            body = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180).read()
            return json.loads(body)
        except urllib.error.HTTPError as e:
            err = Exception(f"HTTP {e.code}: {e.read()[:300]!r}")
            if e.code in (400, 404): break
        except Exception as e: err = Exception(f"{e}; body {body[:300]!r}")
        time.sleep(5)
    raise err
g = get(f"{API}/groups/B14002.json")["variables"]
want = {}
for v, x in g.items():
    if not v.endswith("E"): continue
    lab = x["label"].lower()
    if any(k in lab for k in ("kindergarten", "grade 1 to grade 4", "grade 5 to grade 8", "grade 9 to grade 12")) and lab.rstrip(":").endswith(("public school", "private school")):
        want[v] = "pub" if lab.rstrip(":").endswith("public school") else "priv"
log.write("sample labels: " + json.dumps([x["label"] for v, x in list(g.items())[:12]]) + "\n")
log.write(f"variables {len(want)}: {sorted(want)}\n")
vars_ = ",".join(sorted(want))
out = {}
STATES = ["01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "44", "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56", "72"]
for kind, st in [(k, s) for k in ("unified", "elementary", "secondary") for s in STATES]:
    try:
        rows = get(f"{API}?get=NAME,{vars_}&for=" + urllib.parse.quote(f"school district ({kind}):*") + f"&in=state:{st}")
    except Exception as e:
        log.write(f"ERR {kind} {st} {e}\n"); continue
    h = rows[0]
    for r in rows[1:]:
        d = dict(zip(h, r))
        code = d["state"] + d[f"school district ({kind})"]
        pub = sum(int(d[v]) for v in want if want[v] == "pub" and d[v] not in (None, "") and int(d[v]) >= 0)
        priv = sum(int(d[v]) for v in want if want[v] == "priv" and d[v] not in (None, "") and int(d[v]) >= 0)
        out[code] = {"name": d["NAME"], "kind": kind, "public": pub, "private": priv}
    log.write(f"OK {kind} {st} {len(rows) - 1}\n"); log.flush(); time.sleep(0.5)
json.dump({"source": "ACS 2019-2023 5-year, table B14002 (K-12 enrollment of residents by type of school)", "districts": out}, open(f"{OUT}/acs_b14002_sd.json", "w"))
log.close()
