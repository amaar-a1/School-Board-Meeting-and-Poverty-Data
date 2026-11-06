# Temporary: INEP school census 2025 (its server sends no intermediate certificate) and census age codes.
import json, os, re, subprocess, urllib.request, zipfile
OUT = "fetch/out/g6w"; os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"
log = open(f"{OUT}/log.txt", "w")
host = "download.inep.gov.br"
r = subprocess.run(f"openssl s_client -connect {host}:443 -servername {host} -showcerts </dev/null", shell=True, capture_output=True, text=True, timeout=60)
log.write("s_client:\n" + r.stdout[-6000:] + "\n" + r.stderr[-1500:] + "\n")
pems = re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", r.stdout, re.S)
aia = None
if pems:
    open("/tmp/leaf.pem", "w").write(pems[0])
    t = subprocess.run("openssl x509 -in /tmp/leaf.pem -noout -text", shell=True, capture_output=True, text=True).stdout
    log.write("leaf:\n" + t[-2500:] + "\n")
    m = re.search(r"CA Issuers - URI:(\S+)", t); aia = m and m.group(1)
log.write(f"AIA {aia}\n"); log.flush()
if aia:
    subprocess.run(["curl", "-sSL", "-m", "60", "-o", "/tmp/int.crt", aia])
    pem = subprocess.run("openssl x509 -inform DER -in /tmp/int.crt 2>/dev/null || openssl x509 -in /tmp/int.crt", shell=True, capture_output=True, text=True).stdout
    log.write("intermediate subject: " + subprocess.run("openssl x509 -noout -subject -issuer", input=pem, shell=True, capture_output=True, text=True).stdout + "\n")
    open("/tmp/bundle.pem", "w").write(open("/etc/ssl/certs/ca-certificates.crt").read() + "\n" + pem)
    for url in ["https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2025.zip",
                "https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2024.zip"]:
        z = f"{OUT}/sinopse.zip"
        c = subprocess.run(["curl", "-sSL", "--cacert", "/tmp/bundle.pem", "--retry", "4", "--retry-all-errors", "--retry-delay", "20", "-m", "2400", "-A", UA,
                            "-o", z, "-w", "%{http_code} %{size_download}", url], capture_output=True, text=True)
        log.write(f"{url} -> {c.stdout} {c.stderr[-500:]}\n"); log.flush()
        if os.path.exists(z) and zipfile.is_zipfile(z):
            zf = zipfile.ZipFile(z); log.write("\n".join(f"{i.filename} {i.file_size}" for i in zf.infolist()) + "\n")
            xl = max((i for i in zf.infolist() if i.filename.lower().endswith((".xlsx", ".xls"))), key=lambda i: i.file_size)
            open(f"{OUT}/br_sinopse_{url[-8:-4]}" + os.path.splitext(xl.filename)[1], "wb").write(zf.read(xl)); os.remove(z); break
        if os.path.exists(z): os.remove(z)
# census age groups: the classification codes, from Brazil-level values
for name, path in [("age_codes_9514", "t/9514/n1/all/v/allxp/p/all/c2/6794/c287/all/c286/113635"), ("age_codes_9514b", "t/9514/n1/all/v/allxp/p/all/c287/all")]:
    try:
        with urllib.request.urlopen(urllib.request.Request("https://apisidra.ibge.gov.br/values/" + path, headers={"User-Agent": UA}), timeout=300) as f:
            b = f.read(); open(f"{OUT}/{name}.json", "wb").write(b); log.write(f"{name} {len(b)}\n")
    except Exception as e:
        log.write(f"{name} ERR {e}\n")
log.close()
