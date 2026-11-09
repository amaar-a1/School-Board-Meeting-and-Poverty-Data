# Temporary: ASTAT yearbook 2024 education chapter; Valle d'Aosta yearbook education tables; Trento (vivoscuola) school data page.
import os, urllib.request
OUT = "fetch/out/it_enr2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
U = {"astat_jb2024_k5.pdf": "https://astat.provincia.bz.it/downloads/JB2024_K5.pdf",
     "vda_2024_index.html": "https://regione.vda.it/statistica/pubblicazioni/annuari/annuario2024/default_i.aspx",
     "vda_2021_6_15.pdf": "https://www.regione.vda.it/statistica/pubblicazioni/annuari/annuario2021/SITE/6/15.PDF"}
for i in range(1, 16): U[f"vda_2024_6_{i}.pdf"] = f"https://regione.vda.it/statistica/pubblicazioni/annuari/annuario2024/SITE/6/{i}.PDF"
for n, u in U.items():
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120) as r: b = r.read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"ok {n} {len(b)}\n")
    except Exception as e: log.write(f"ERR {n} {str(e)[:100]}\n")
log.close()
