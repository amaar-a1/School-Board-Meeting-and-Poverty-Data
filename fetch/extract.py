# Temporary: look for INEC's 2022 census NBI poverty by canton (tabulados) next to the NBI methodology book.
import os, re, time, traceback, urllib.request
OUT = "fetch/out/ec_nbi22"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
pages = ["https://www.ecuadorencifras.gob.ec/pobreza-por-necesidades-basicas-insatisfechas/",
         "https://www.ecuadorencifras.gob.ec/biblioteca/", "https://www.ecuadorencifras.gob.ec/libros/",
         "https://www.ecuadorencifras.gob.ec/pobreza-necesidades-basicas-insatisfechas-nbi-censo-2022/",
         "https://www.ecuadorencifras.gob.ec/estadisticas/"]
found = set()
for u in pages:
    try:
        t = get(u).decode("utf-8", "replace")
        links = set(re.findall(r"""href=["']([^"']+)["']""", t))
        hits = sorted(l for l in links if re.search(r"nbi|pobreza|censo|2022|cpv", l, re.I))
        found |= {l for l in hits if re.search(r"\.(xlsx?|zip|csv)$", l, re.I)}
        log.write(f"== {u}: {len(t)} chars; {len(hits)} matching links\n" + "\n".join(hits[:80]) + "\n\n")
    except Exception as e:
        log.write(f"== {u}: {e}\n\n")
base = "https://www.ecuadorencifras.gob.ec/documentos/web-inec/"
for g in ("POBREZA/NBI/NBI-FUENTE-CPV/Tabulados_pobreza_por_NBI_2022.xlsx", "POBREZA/NBI/NBI-FUENTE-CPV/Tabulados_NBI_CPV_2022.xlsx",
          "POBREZA/NBI/NBI-FUENTE-CPV/Tabulados_pobreza_por_NBI_CPV2022.xlsx", "Bibliotecas/Libros/Tabulados_NBI_CPV2022.xlsx",
          "POBREZA/NBI/NBI-FUENTE-CPV/2022/Tabulados_pobreza_por_NBI.xlsx"):
    found.add(base + g)
for u in sorted(found):
    try:
        b = get(u, 300); n = re.sub(r"[^\w.]+", "_", u.split("/web-inec/")[-1])[-120:]
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"OK {u}: {len(b)} bytes\n")
    except Exception as e:
        log.write(f"no {u}: {e}\n")
log.close()
