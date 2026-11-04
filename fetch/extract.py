# Temporary: second set of Canadian enrolment files (Ontario, Nova Scotia, Saskatchewan, NWT).
import json, os, time, urllib.request
OUT = "fetch/out/enrol2"; os.makedirs(OUT, exist_ok=True)
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
for base in ("https://data.ontario.ca", "https://data2.ontario.ca"):
    d = get(f"{base}/api/3/action/package_show?id=school-information-and-student-demographics")
    if d:
        res = json.loads(d)["result"]["resources"]
        open(f"{OUT}/on_sif_resources.json", "w").write(json.dumps([(r.get("name"), r.get("format"), r.get("url")) for r in res], indent=1))
        en = [r for r in res if (r.get("format") or "").upper() == "XLSX" and "_fr" not in (r.get("url") or "").lower()]
        for i, r in enumerate(en[:2]):
            get(r["url"], f"on_sif_{i}.xlsx")
        break
get("https://data.novascotia.ca/api/views/cjnf-ywvt/rows.csv?accessType=DOWNLOAD", "ns_enrolment.csv")
get("https://publications.saskatchewan.ca/api/v1/products/83293/formats/95844/download", "sk_active_schools.bin")
get("https://www.ece.gov.nt.ca/sites/ece/files/school_funding_framework_2025-26.pdf", "nt_funding_2025_26.pdf")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
