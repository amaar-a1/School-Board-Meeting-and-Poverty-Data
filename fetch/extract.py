# Temporary: enrolment for Saskatchewan (archived copy), PEI, NWT, Yukon and Newfoundland and Labrador.
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/enrol4"; os.makedirs(OUT, exist_ok=True)
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
# Saskatchewan: the Internet Archive's copies of the Active List of Saskatchewan Schools/Programs and the category listing
for u in ["publications.saskatchewan.ca/api/v1/products/83293/formats/95844/download", "publications.saskatchewan.ca/api/v1/products/83293",
          "publications.saskatchewan.ca/api/v1/categories/2303/products"]:
    d = get("https://archive.org/wayback/available?url=" + urllib.parse.quote(u))
    snap = json.loads(d).get("archived_snapshots", {}).get("closest", {}) if d else {}
    log.append(f"wayback {u}: {snap}")
    if snap.get("url"):
        raw = re.sub(r"/web/(\d+)/", r"/web/\1id_/", snap["url"])   # id_ = the original file, unmodified
        get(raw, "sk_" + re.sub(r"\W+", "_", u.split("/api/v1/")[1])[:40])
d = get("https://web.archive.org/cdx/search/cdx?url=publications.saskatchewan.ca/api/v1/products/*&output=json&limit=200&filter=statuscode:200")
if d:
    open(f"{OUT}/sk_cdx.json", "wb").write(d)
# PEI: official K-12 enrolment report pages, then their PDFs
for node in ("71985", "78851"):
    h = get(f"https://www.princeedwardisland.ca/en/node/{node}", f"pe_node_{node}.html")
    if h:
        for i, link in enumerate(sorted(set(re.findall(rb'href="([^"]+\.pdf)"', h)))[:3]):
            get(urllib.parse.urljoin("https://www.princeedwardisland.ca/", link.decode()), f"pe_{node}_{i}.pdf")
# NWT: JK-12 performance measures report 2024-25 (enrolment by education body)
get("https://www.ece.gov.nt.ca/sites/ece/files/resources/jk-12_annual_pm_report_2024-25_final.pdf", "nt_pm_2024_25.pdf")
# Yukon: open data search for school enrolment
d = get("https://open.yukon.ca/data/api/3/action/package_search?q=school%20enrolment&rows=10")
if d:
    res = json.loads(d)["result"]["results"]
    open(f"{OUT}/yt_search.json", "w").write(json.dumps([(p["title"], p["name"], [(r.get("format"), r.get("url")) for r in p["resources"]][:5]) for p in res], indent=1))
    for p in res:
        if re.search(r"enrol", p["title"], re.I):
            for i, r in enumerate([r for r in p["resources"] if (r.get("format") or "").upper() in ("CSV", "XLSX")][:2]):
                get(r["url"], f"yt_{p['name'][:30]}_{i}.{(r.get('format') or 'csv').lower()}")
            break
# Newfoundland and Labrador: Community Accounts enrolment table
get("https://nl.communityaccounts.ca/table.asp?_=vb7En4WVgbOxz7ZjS6rIxpuixqOVko7Lqomyv4yplszCmJ6-x84_", "nl_enrolment.html")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
