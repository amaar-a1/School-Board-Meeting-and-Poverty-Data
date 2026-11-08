# Temporary: Australia, Census 2021 GCP tables G01, G02, G04 and G15 for local government areas, as CSV.
import io, os, re, traceback, urllib.request, zipfile
OUT = "fetch/out/au2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
try:
    with urllib.request.urlopen(urllib.request.Request("https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_GCP_LGA_for_AUS_short-header.zip", headers=UA), timeout=600) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    names = z.namelist(); log.write("\n".join(names[:12]) + "\n")
    for n in names:
        b = os.path.basename(n)
        if re.search(r"_(G01|G02|G04A|G04B|G15)_AUS_LGA\.csv$|_(G01|G02|G04A|G04B|G15)_AUST_LGA\.csv$", b):
            open(f"{OUT}/{b}", "wb").write(z.read(n)); log.write(f"saved {b}\n")
except Exception: log.write(traceback.format_exc()[-800:])
log.close()
