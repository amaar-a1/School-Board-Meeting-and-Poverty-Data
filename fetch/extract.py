# Temporary: a DGEEC file the user found (pupils, Portugal), and a look inside it.
import io, os, traceback, urllib.request, zipfile
OUT = "fetch/out/pt_dgeec"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
try:
    u = "https://www.dgeec.medu.pt/api/ficheiros/68df8c23ceacc0faf4a39755"
    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}), timeout=300) as r:
        b = r.read(); ct = r.headers.get("Content-Type"); cd = r.headers.get("Content-Disposition")
    ext = "xlsx" if b[:2] == b"PK" else "xls" if b[:4] == b"\xd0\xcf\x11\xe0" else "pdf" if b[:4] == b"%PDF" else "bin"
    open(f"{OUT}/dgeec_file.{ext}", "wb").write(b)
    log.write(f"{len(b)} bytes; {ct}; {cd}; saved as .{ext}\n")
    if ext == "xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(b), read_only=True)
        for ws in wb.worksheets:
            log.write(f"== sheet {ws.title}\n")
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                log.write(f"{[str(c)[:30] for c in row[:14]]}\n")
                if i > 14: break
except Exception: log.write(traceback.format_exc()[-800:])
log.close()
