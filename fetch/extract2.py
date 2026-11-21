# Round 4c: INDEC Census 2022 tables by province (population and area; population by age).
import os, urllib.request, time
OUT = "fetch/out/ar4c"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
for n in ["c2022_tp_est_c1.xlsx", "c2022_tp_est_c2.xlsx", "c2022_tp_est_c3.xlsx", "c2022_tp_est_c4.xlsx", "c2022_tp_est_c5.xlsx", "c2022_tp_est_c6.xlsx"]:
    u = "https://www.indec.gob.ar/ftp/cuadros/poblacion/" + n
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n")
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n")
    time.sleep(2)
