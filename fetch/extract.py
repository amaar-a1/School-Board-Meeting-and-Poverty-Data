# Temporary: OSMPH/deped_schools_db (DepEd school lists): file tree, README and the header of each data file.
import json, os, urllib.request
OUT = "fetch/out/enr2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
try:
    tree = json.loads(get("https://api.github.com/repos/OSMPH/deped_schools_db/git/trees/master?recursive=1"))["tree"]
    files = [(t["path"], t.get("size")) for t in tree if t["type"] == "blob"]
    log.write(json.dumps(files, indent=0) + "\n")
    open(f"{OUT}/README.md", "wb").write(get("https://raw.githubusercontent.com/OSMPH/deped_schools_db/master/README.md"))
    for p, s in files:
        if p.endswith((".csv", ".tsv")) and s:
            b = get(f"https://raw.githubusercontent.com/OSMPH/deped_schools_db/master/{urllib.request.quote(p)}")
            log.write(f"== {p} {len(b)}\n" + b[:1500].decode("utf-8", "ignore") + "\n")
            if "enrol" in b[:3000].decode("utf-8", "ignore").lower(): open(f"{OUT}/{os.path.basename(p)}", "wb").write(b)
except Exception as e: log.write(f"ERR {str(e)[:200]}\n")
log.close()
