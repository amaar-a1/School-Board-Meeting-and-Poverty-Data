# Temporary: fourth pass. Irish ETB minutes and UK ModernGov committees; Brazil census tables (apisidra) and INEP; Brazil YouTube shards 3-5.
import json, os, re, subprocess, sys, time, traceback, urllib.request
T0 = time.time()
OUT = "fetch/out/g5w"; os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"
log = open(f"{OUT}/log.txt", "w")
def step(name, f):
    t = time.time()
    try: res = f(); log.write(f"== {name} ({time.time()-t:.0f}s)\n{res}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-800:]}\n\n")
    log.flush()
def get(url, timeout=120):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
        return r.read()

def sidra():
    out = []
    ids = [4712, 4714, 9514, 9606, 9605, 9923] + list(range(10050, 10125)) + list(range(10280, 10300))
    for t in ids:
        try:
            b = get(f"https://apisidra.ibge.gov.br/desctabapi.aspx?c={t}", 60).decode("utf-8", "replace")
            ttl = re.search(r'id="lblNomeTabela"[^>]*>(.*?)<', b, re.S)
            lv = "N6" if re.search(r"N6\b|Munic", b) else ""
            out.append(f"{t} | {lv} | {re.sub(r'\s+', ' ', ttl.group(1)).strip() if ttl else b[:120]!r}")
            open(f"{OUT}/sidra_{t}.html", "w").write(b) if re.search(r"rendimento|frequen|escola|domic", b, re.I) else None
        except Exception as e:
            out.append(f"{t} ERR {e}")
        time.sleep(0.5)
    return "\n".join(out)
step("apisidra table descriptions", sidra)
def sidra_vals():
    out = []
    for name, path in [("households_4712", "t/4712/n6/all/v/all/p/all"), ("age_9514", "t/9514/n6/all/v/allxp/p/all/c2/6794/c287/93070,93084,93085,93086,93087,93088,93089,93090,93091,93092,93093,93094,93095,93096,93097,93098,93099,6653")]:
        try:
            b = get("https://apisidra.ibge.gov.br/values/" + path, 900); open(f"{OUT}/sidra_{name}.json", "wb").write(b)
            out.append(f"{name} {len(b)} bytes {b[:300]!r}")
        except Exception as e:
            out.append(f"{name} ERR {e}")
    return "\n".join(out)
step("apisidra values", sidra_vals)

def inep():
    # The runner's trust store lacks the issuing CA's intermediate certificate; fetch it from the address the
    # server's own certificate names (Authority Information Access) and verify against it.
    host = "download.inep.gov.br"
    s = subprocess.run(f"echo | openssl s_client -connect {host}:443 -servername {host} 2>/dev/null | openssl x509 -noout -text", shell=True, capture_output=True, text=True).stdout
    aia = re.search(r"CA Issuers - URI:(\S+)", s)
    out = f"AIA {aia.group(1) if aia else None}\n"
    if not aia: return out + s[-1500:]
    subprocess.run(["curl", "-sSL", "-m", "60", "-o", "/tmp/int.crt", aia.group(1)])
    pem = subprocess.run("openssl x509 -inform DER -in /tmp/int.crt 2>/dev/null || openssl x509 -in /tmp/int.crt", shell=True, capture_output=True, text=True).stdout
    open("/tmp/bundle.pem", "w").write(open("/etc/ssl/certs/ca-certificates.crt").read() + "\n" + pem)
    r = subprocess.run(["curl", "-sSL", "--cacert", "/tmp/bundle.pem", "--retry", "5", "--retry-all-errors", "--retry-delay", "30", "-m", "2400", "-A", UA,
                        "-o", f"{OUT}/br_sinopse_2025.zip", "-w", "%{http_code} %{size_download}",
                        "https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2025.zip"], capture_output=True, text=True)
    out += r.stdout + "\n" + r.stderr[-800:]
    import zipfile
    z = f"{OUT}/br_sinopse_2025.zip"
    if os.path.exists(z) and zipfile.is_zipfile(z):
        zf = zipfile.ZipFile(z); out += "\n" + "\n".join(f"{i.filename} {i.file_size}" for i in zf.infolist())
        xl = max((i for i in zf.infolist() if i.filename.lower().endswith((".xlsx", ".xls"))), key=lambda i: i.file_size)
        open(f"{OUT}/br_sinopse_2025" + os.path.splitext(xl.filename)[1], "wb").write(zf.read(xl))
    if os.path.exists(z): os.remove(z)
    return out
step("inep sinopse 2025", inep)

log.close()
