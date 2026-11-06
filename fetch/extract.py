# Temporary: second pass for the data gaps. Writes to fetch/out/g3/.
import json, os, re, urllib.request, urllib.parse, time, traceback, zipfile, io, csv, subprocess
OUT = "fetch/out/g3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(url, n=None, data=None, hdr=None, method=None, timeout=300):
    req = urllib.request.Request(url, data=data, headers={**UA, **(hdr or {})}, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read() if n is None else r.read(n)
def step(name, f):
    t = time.time()
    try: res = f(); log.write(f"== {name} ({time.time()-t:.0f}s)\n{res}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-800:]}\n\n")
    log.flush(); time.sleep(2)
def curl(name, url, extra=()):
    r = subprocess.run(["curl", "-sSL", "--retry", "5", "--retry-all-errors", "--retry-delay", "20", "-m", "1800", "-A", UA["User-Agent"], *extra, "-o", f"{OUT}/{name}", "-w", "%{http_code} %{size_download}", url], capture_output=True, text=True)
    return r.stdout + " " + r.stderr[-300:]

# CivicSearch search API: what one place's results look like
def civic():
    pl = json.loads(get("https://schools.civicsearch.org/api/get_place_list")[2])
    out = []
    for p in pl[:2]:
        for q in [{"keywords": "meeting", "lonlat": f"{p['longitude']},{p['latitude']}", "search_radius": "0"},
                  {"keywords": "board", "lonlat": f"{p['longitude']},{p['latitude']}", "search_radius": "0", "start_date": "2020-01-01", "end_date": "2026-12-31"}]:
            u = "https://schools.civicsearch.org/api/search?" + urllib.parse.urlencode(q)
            try:
                s, ct, b = get(u); open(f"{OUT}/civic_search_{len(out)}.json", "wb").write(b)
                d = json.loads(b)
                out.append(f"{u} {s} {len(b)} type {type(d).__name__} keys {list(d)[:20] if isinstance(d, dict) else len(d)}\n{b[:2500]!r}")
            except Exception as e:
                out.append(f"{u} ERR {e}")
            time.sleep(2)
    return "\n".join(out)
step("civicsearch search", civic)

# INEP school census summary 2025 (retry with curl)
def inep():
    s = curl("br_sinopse_2025.zip", "https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2025.zip")
    z = zipfile.ZipFile(f"{OUT}/br_sinopse_2025.zip"); info = "\n".join(f"{i.filename} {i.file_size}" for i in z.infolist())
    xl = [i for i in z.infolist() if i.filename.lower().endswith((".xlsx", ".xls"))]
    big = max(xl, key=lambda i: i.file_size); open(f"{OUT}/br_sinopse_2025.xlsx", "wb").write(z.read(big)); os.remove(f"{OUT}/br_sinopse_2025.zip")
    return s + "\n" + info
step("inep sinopse 2025", inep)

# Brazil population and households by municipality (IBGE file server)
step("ibge ftp estimativa 2025", lambda: curl("br_pop_2025.xls", "https://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2025/estimativa_dou_2025.xls"))
step("ibge ftp listing censo 2022", lambda: get("https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/", 200000)[2].decode("utf-8", "replace")[:6000])
step("sidra api", lambda: get("https://apisidra.ibge.gov.br/values/t/4709/n6/3550308/v/93", 5000, timeout=120)[2][:500])

# Bolsa Família, September 2025: families per municipality
def bf():
    s = curl("bf.zip", "https://portaldatransparencia.gov.br/download-de-dados/novo-bolsa-familia/202509")
    z = zipfile.ZipFile(f"{OUT}/bf.zip"); n = z.namelist()[0]
    rd = csv.reader(io.TextIOWrapper(z.open(n), encoding="latin-1"), delimiter=";")
    hdr = next(rd); cnt = {}; val = {}
    im = [i for i, h in enumerate(hdr) if "SIAFI" in h.upper()][0]; iv = [i for i, h in enumerate(hdr) if "VALOR" in h.upper()][0]
    iu = [i for i, h in enumerate(hdr) if h.strip().upper() == "UF"][0]; inm = [i for i, h in enumerate(hdr) if "NOME MUNIC" in h.upper()][0]
    names = {}
    for r in rd:
        k = r[im]; cnt[k] = cnt.get(k, 0) + 1; val[k] = val.get(k, 0) + float(r[iv].replace(".", "").replace(",", ".") or 0); names[k] = (r[iu], r[inm])
    with open(f"{OUT}/br_bolsa_familia_202509.csv", "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(["siafi", "uf", "municipio", "familias", "valor"])
        for k in sorted(cnt): w.writerow([k, *names[k], cnt[k], round(val[k], 2)])
    os.remove(f"{OUT}/bf.zip")
    return f"{s} {hdr} {len(cnt)} municipalities, {sum(cnt.values())} families"
step("bolsa familia", bf)
# SIAFI to IBGE municipality codes (Tesouro Nacional table)
step("siafi-ibge", lambda: curl("br_siafi_ibge.csv", "https://www.tesourotransparente.gov.br/ckan/dataset/abb968cb-3710-4f85-89cf-875c91b9c7f6/resource/eebb3bc6-9eea-4496-8bcf-304f33155282/download/TABMUN.csv"))

# Mexico: INEGI census 2020, municipal totals
def iter_mx():
    s = curl("iter.zip", "https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_00_cpv2020_csv.zip")
    z = zipfile.ZipFile(f"{OUT}/iter.zip")
    name = [n for n in z.namelist() if "conjunto_de_datos" in n and n.lower().endswith(".csv")][0]
    rows = csv.reader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig", errors="replace"))
    hdr = next(rows); n = 0
    with open(f"{OUT}/mx_iter_municipal.csv", "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(hdr)
        for r in rows:
            if len(r) > 5 and r[hdr.index("LOC")] == "0000" and r[hdr.index("MUN")] != "000": w.writerow(r); n += 1
    os.remove(f"{OUT}/iter.zip")
    return f"{s} {n} municipalities\n" + ",".join(hdr)
step("inegi iter 2020", iter_mx)

# Germany: Regionalatlas (statistical offices' map service) layers, to find pupils by Kreis
def ra():
    out = []
    for u in ["https://www.gis-idmz.nrw.de/arcgis/rest/services/stba/regionalatlas/MapServer?f=json",
              "https://regionalatlas.statistikportal.de/"]:
        try:
            s, ct, b = get(u, 3_000_000); t = b.decode("utf-8", "replace")
            if u.endswith("json"):
                d = json.loads(t); out.append(f"{u} {s} layers {len(d.get('layers', []))}: " + "; ".join(f"{l['id']}:{l['name']}" for l in d.get("layers", [])[:400]))
            else:
                out.append(f"{u} {s} {len(b)}\n" + "\n".join(sorted(set(re.findall(r'(?:src|href)=["\']([^"\']+)["\']', t)))[:60]))
        except Exception as e:
            out.append(f"{u} ERR {e}")
    return "\n".join(out)
step("regionalatlas", ra)
log.close()
