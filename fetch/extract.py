# Temporary: Brazil INEP sinopse (educação básica). Links from the gov.br page; download with the server's missing
# intermediate certificate added from its AIA URL (verification stays on). Aggregate enrollment by municipality.
import io, json, os, re, ssl, socket, subprocess, sys, traceback, urllib.request, zipfile
OUT = "fetch/out/br_inep2"; os.makedirs(OUT, exist_ok=True); W = "/tmp/br"; os.makedirs(W, exist_ok=True)
log = open(f"{OUT}/log.txt", "a")
try:
    import certifi, openpyxl
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "certifi", "openpyxl"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(u, t=300, ctx=None):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t, context=ctx) as r: return r.read()
links = []
try:
    t = get("https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/sinopses-estatisticas/educacao-basica").decode("utf-8", "replace")
    links = sorted(set(re.findall(r'https?://[^"\']+\.zip', t))); log.write("links " + json.dumps(links) + "\n")
except Exception as e: log.write(f"ERR page {e}\n")
ctx = ssl.create_default_context(cafile=certifi.where())
try:
    conn = socket.create_connection(("download.inep.gov.br", 443), timeout=60)
    s = ssl.create_default_context(); s.check_hostname = False; s.verify_mode = ssl.CERT_NONE   # only to READ the leaf's AIA field
    with s.wrap_socket(conn, server_hostname="download.inep.gov.br") as tls: der = tls.getpeercert(binary_form=True)
    open(f"{W}/leaf.der", "wb").write(der)
    txt = subprocess.run(["openssl", "x509", "-inform", "DER", "-in", f"{W}/leaf.der", "-noout", "-text"], capture_output=True, text=True).stdout
    aia = re.findall(r"CA Issuers - URI:(\S+)", txt); log.write(f"issuer {re.findall(r'Issuer: (.*)', txt)} aia {aia}\n")
    bundle = open(certifi.where()).read()
    for u in aia:
        b = get(u, 60); open(f"{W}/int", "wb").write(b)
        pem = subprocess.run(["openssl", "x509", "-inform", "PEM" if b.startswith(b"-----") else "DER", "-in", f"{W}/int"], capture_output=True, text=True).stdout
        bundle += "\n" + pem
    open(f"{W}/bundle.pem", "w").write(bundle); ctx = ssl.create_default_context(cafile=f"{W}/bundle.pem")
except Exception as e: log.write("ERR chain " + traceback.format_exc()[-400:] + "\n")
cands = [l for l in links if "educacao_basica" in l.lower() or "censo_escolar" in l.lower()] or [f"https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopses_estatisticas_censo_escolar_{y}.zip" for y in (2025, 2024)]
for u in sorted(cands, reverse=True)[:3]:
    try:
        b = get(u, 900, ctx); log.write(f"{u}: {len(b)} bytes\n")
        z = zipfile.ZipFile(io.BytesIO(b)); log.write(json.dumps(z.namelist()) + "\n")
        x = next(n for n in z.namelist() if n.lower().endswith((".xlsx", ".xls")))
        open(f"{W}/sinopse.xlsx", "wb").write(z.read(x))
        wb = openpyxl.load_workbook(f"{W}/sinopse.xlsx", read_only=True, data_only=True)
        for sn in wb.sheetnames[:12]:
            ws = wb[sn]; head = [c for row in ws.iter_rows(min_row=1, max_row=10, values_only=True) for c in row if c]
            log.write(f"sheet {sn}: {' | '.join(str(c)[:40] for c in head[:30])}\n")
        json.dump({"url": u, "file": x}, open(f"{OUT}/meta.json", "w")); break
    except Exception as e: log.write(f"ERR {u} {str(e)[:200]}\n")
log.close()
