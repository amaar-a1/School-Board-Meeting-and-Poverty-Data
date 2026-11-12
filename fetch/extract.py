# Temporary: Brazil INEP school census summary (sinopse) with the server's missing intermediate certificate added from
# its own AIA "CA Issuers" URL (verification stays on), summed by municipality.
import io, json, os, re, ssl, subprocess, sys, urllib.request, zipfile
OUT = "fetch/out/br_inep1"; os.makedirs(OUT, exist_ok=True); W = "/tmp/br"; os.makedirs(W, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
try:
    import certifi
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "certifi", "openpyxl"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
try:
    import openpyxl
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "openpyxl"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
host = "download.inep.gov.br"
leaf = ssl.get_server_certificate((host, 443))
open(f"{W}/leaf.pem", "w").write(leaf)
txt = subprocess.run(["openssl", "x509", "-in", f"{W}/leaf.pem", "-noout", "-text"], capture_output=True, text=True).stdout
aia = re.findall(r"CA Issuers - URI:(\S+)", txt); log.write(f"issuer {re.findall(r'Issuer: (.*)', txt)} aia {aia}\n")
bundle = open(certifi.where()).read()
for u in aia:
    der = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
    open(f"{W}/int.der", "wb").write(der)
    pem = subprocess.run(["openssl", "x509", "-inform", "DER" if not der.startswith(b"-----") else "PEM", "-in", f"{W}/int.der"], capture_output=True, text=True).stdout
    bundle += "\n" + pem
open(f"{W}/bundle.pem", "w").write(bundle)
ctx = ssl.create_default_context(cafile=f"{W}/bundle.pem")
for y in (2025, 2024, 2023):
    u = f"https://{host}/dados_abertos/sinopses_estatisticas/sinopses_estatisticas_censo_escolar_{y}.zip"
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=900, context=ctx)
        b = r.read(); log.write(f"{y}: {len(b)} bytes\n")
        z = zipfile.ZipFile(io.BytesIO(b)); names = z.namelist(); log.write(json.dumps(names) + "\n")
        x = next(n for n in names if n.lower().endswith((".xlsx", ".xls")) and "basica" in n.lower().replace("á", "a"))
        wb = openpyxl.load_workbook(io.BytesIO(z.read(x)), read_only=True, data_only=True)
        log.write(f"sheets {wb.sheetnames}\n")
        ws = wb[wb.sheetnames[1]] if len(wb.sheetnames) > 1 else wb.active
        rows = [[c for c in row] for row in ws.iter_rows(min_row=1, max_row=12, values_only=True)]
        for rr in rows: log.write("  " + json.dumps([str(c)[:30] if c is not None else None for c in rr[:14]], ensure_ascii=False) + "\n")
        open(f"{W}/sinopse.xlsx", "wb").write(z.read(x))
        # keep the sheet of enrollment by municipality ("Matrícula" totals): find it by its title cell
        out = {}
        for sn in wb.sheetnames:
            ws = wb[sn]; head = " ".join(str(c) for row in ws.iter_rows(min_row=1, max_row=6, values_only=True) for c in row if c)
            log.write(f"sheet {sn}: {head[:160]}\n")
        json.dump({"year": y, "file": x}, open(f"{OUT}/meta.json", "w")); break
    except Exception as e: log.write(f"{y} ERR {str(e)[:200]}\n")
log.close()
