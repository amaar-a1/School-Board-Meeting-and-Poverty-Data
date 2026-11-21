# Round 12: Uruguay poverty by department - the 2024 report, the yearbook's TUS table (3.9.3) and the ECH microdata page.
import os, re, urllib.request, time
OUT = "fetch/out/uy12"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(n, u):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); return b
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n")
    finally: time.sleep(2)
get("uy_pobreza_2024.html", "https://www5.ine.gub.uy/documents/Demograf%C3%ADayEESS/HTML/ECH/Pobreza/2024/Estimacion%20de%20la%20pobreza%20por%20el%20metodo%20de%20ingreso%20anual%202024.html")
get("uy_3.9.3.xlsx", "https://www5.ine.gub.uy/documents/ANUARIOS/Anuario%202025/3%20-%20ASPECTOS%20SOCIALES/3.9%20Desarrollo%20Social/3.9.3ok.xlsx")
get("uy_3.9.1.xlsx", "https://www5.ine.gub.uy/documents/ANUARIOS/Anuario%202025/3%20-%20ASPECTOS%20SOCIALES/3.9%20Desarrollo%20Social/3.9.1ok.xlsx")
for n, u in [("uy_ech_2025.html", "https://www.gub.uy/instituto-nacional-estadistica/datos-y-estadisticas/encuestas/encuesta-continua-hogares-2025"),
             ("uy_ech_micro.html", "https://www.gub.uy/instituto-nacional-estadistica/datos-y-estadisticas/encuestas/microdatos-ech"),
             ("uy_ech_list.html", "https://www.gub.uy/instituto-nacional-estadistica/datos-y-estadisticas/encuestas/encuesta-continua-hogares")]:
    b = get(n, u)
    if b:
        for l in sorted(set(re.findall(rb'href="([^"]+)"', b))):
            if re.search(rb"ech|microdat|ECH|\.zip|\.sav|\.csv", l): log.write("   link " + l.decode("utf-8", "replace") + "\n")
