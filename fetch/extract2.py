# Round 46: US SAIPE school district poverty for earlier years (2019-2023), for change over time.
import os, urllib.request, time
OUT = "fetch/out/c46"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
for y in range(2019, 2024):
    yy = str(y)[2:]
    for ext in ("csv", "txt"):
        u = f"https://www2.census.gov/programs-surveys/saipe/datasets/{y}/{y}-school-districts/ussd{yy}.{ext}"
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180).read()
            open(f"{OUT}/ussd{yy}.{ext}", "wb").write(b); log.write(f"OK {u} {len(b)}\n   {b[:240]!r}\n"); break
        except Exception as e: log.write(f"ERR {u} {e}\n")
        finally: log.flush(); time.sleep(2)
