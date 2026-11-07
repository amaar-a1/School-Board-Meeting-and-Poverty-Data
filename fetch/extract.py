# Temporary: two PDFs the user pointed to, as text: INSEE's poverty in the overseas departments (RPM 2024, F21)
# and INEC's NBI methodology book (Ecuador).
import os, subprocess, time, traceback, urllib.request
OUT = "fetch/out/pdfs1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
subprocess.run(["sudo", "apt-get", "install", "-y", "-qq", "poppler-utils"], capture_output=True)
for name, u in (("insee_rpm2024_f21", "https://www.insee.fr/fr/statistiques/fichier/7941411/RPM2024-F21.pdf"),
                ("inec_nbi_libro", "https://www.ecuadorencifras.gob.ec/documentos/web-inec/Bibliotecas/Libros/NBI_VersionLibroMetodologico.pdf")):
    try:
        b = None
        for a in range(3):
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r: b = r.read(); break
            except Exception as e:
                log.write(f"{name} try {a}: {e}\n"); time.sleep(15)
        open(f"/tmp/{name}.pdf", "wb").write(b)
        r = subprocess.run(["pdftotext", "-layout", f"/tmp/{name}.pdf", f"{OUT}/{name}.txt"], capture_output=True, text=True)
        t = open(f"{OUT}/{name}.txt", encoding="utf-8", errors="replace").read()
        log.write(f"{name}: {len(b)} bytes pdf, {len(t)} chars text, rc {r.returncode} {r.stderr[:200]}\n")
    except Exception:
        log.write(f"{name}: ERR {traceback.format_exc()[-600:]}\n")
log.close()
