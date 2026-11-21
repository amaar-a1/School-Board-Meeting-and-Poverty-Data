# Round 11: Uruguay's income-poverty report for 2025 (HTML, with tables by department).
import os, urllib.request, time
OUT = "fetch/out/uy11"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
for n, u in [("uy_pobreza_2025.html", "https://www5.ine.gub.uy/documents/Demograf%C3%ADayEESS/HTML/ECH/Pobreza/2025/Informe%20pobreza%20Anual-2025.html"),
             ("uy_pobreza_2026s1.html", "https://www5.ine.gub.uy/documents/Demograf%C3%ADayEESS/HTML/ECH/Pobreza/2026/Informe%20Pobreza_Monetaria_%20primer%20semestre%202026.html")]:
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)}\n")
    except Exception as e: log.write(f"== {n} ERR {e}\n")
    time.sleep(2)
