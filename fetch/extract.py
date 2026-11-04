# Temporary: world fetch part 7: Finland fallbacks, Norfolk Island census.
import os, time, urllib.request
OUT = "fetch/out/w7"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
log = []
def get(url, name):
    time.sleep(1.5)
    try:
        d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600).read()
        open(f"{OUT}/{name}", "wb").write(d); log.append(f"ok {len(d)} {url}")
    except Exception as e:
        log.append(f"FAIL {url}: {e}")
for ind in (3099, 181):
    get(f"https://sotkanet.fi/rest/1.1/json?indicator={ind}&years=2022&years=2023&years=2024&genders=total", f"fi_{ind}.json")
for c in ("901011001", "901021002", "901031003", "901041004", "SAL90004", "SAL90003", "SAL90002", "SAL90001"):
    get(f"https://www.abs.gov.au/census/find-census-data/quickstats/2021/{c}", f"abs_{c}.html")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
