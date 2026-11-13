# Temporary: ABS 2021 Census QuickStats, Norfolk Island (SAL90004): people attending an educational institution.
import os, re, html, urllib.request
OUT = "fetch/out/nfk2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
try:
    t = urllib.request.urlopen(urllib.request.Request("https://www.abs.gov.au/census/find-census-data/quickstats/2021/SAL90004", headers=UA), timeout=120).read().decode("utf-8", "replace")
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
    for k in ["attending an educational institution", "Preschool", "Primary", "Secondary", "Government", "Catholic", "Other non Government", "People Male"]:
        for m in re.finditer(re.escape(k), txt): log.write(f"{k}: {txt[max(0,m.start()-60):m.start()+260]}\n")
except Exception as e: log.write(f"ERR {e}\n")
log.close()
