# Temporary: third set of Canadian enrolment files (Ontario 2024-25, Alberta 2024-25, Saskatchewan).
import json, os, subprocess, time, urllib.request
OUT = "fetch/out/enrol3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
log = []
def get(url, name=None):
    time.sleep(3)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
            data = r.read()
        if name:
            open(f"{OUT}/{name}", "wb").write(data)
        log.append(f"ok {len(data)} {url} -> {name}")
        return data
    except Exception as e:
        log.append(f"FAIL {url}: {e}"); return None
get("https://data.ontario.ca/dataset/d85f68c5-fcb0-4b4d-aec5-3047db47dcd5/resource/f75540ed-59eb-49ab-ac43-976d563b3a65/download/new_sif_data_2024_25_final_en_sep_2026.xlsx", "on_sif_2024_25.xlsx")
d = get("https://open.alberta.ca/api/3/action/package_show?id=ccbcf0fb-615e-44a0-b7ec-681e2ea4e1e7")
if d:
    res = json.loads(d)["result"]["resources"]
    open(f"{OUT}/ab_resources.json", "w").write(json.dumps([(r.get("name"), r.get("format"), r.get("url")) for r in res], indent=1))
    pick = [r for r in res if "2024" in ((r.get("name") or "") + (r.get("url") or "")) and "2025" in ((r.get("name") or "") + (r.get("url") or ""))]
    for i, r in enumerate(pick[:2]):
        get(r["url"], f"ab_2024_25_{i}.xlsx")
# Saskatchewan's server doesn't send its full certificate chain; curl with the system CA store.
r = subprocess.run(["curl", "-sSfL", "-A", UA["User-Agent"], "-o", f"{OUT}/sk_active_schools.bin",
                    "https://publications.saskatchewan.ca/api/v1/products/83293/formats/95844/download"], capture_output=True, text=True)
log.append(f"sk curl {r.returncode} {r.stderr[:200]}")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
