# Temporary: download the files found for the next data gaps, and look further where the first pass failed.
# Writes to fetch/out/g2/ (files over 90 MB are summarised instead of kept).
import json, os, re, urllib.request, urllib.parse, time, traceback, zipfile, io, csv
OUT = "fetch/out/g2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")


def get(url, n=None, data=None, hdr=None, method=None, timeout=300):
    req = urllib.request.Request(url, data=data, headers={**UA, **(hdr or {})}, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read() if n is None else r.read(n)


def step(name, f):
    t = time.time()
    try:
        res = f()
        log.write(f"== {name} ({time.time()-t:.0f}s)\n{res}\n\n")
    except Exception:
        log.write(f"== {name}\nERR {traceback.format_exc()[-1200:]}\n\n")
    log.flush(); time.sleep(2)


def save(name, url, **kw):
    s, ct, b = get(url, **kw)
    open(f"{OUT}/{name}", "wb").write(b)
    return f"{s} {ct} {len(b)} bytes -> {name}"


# --- CivicSearch: keep the app script to find how it loads a place's meetings
def civic():
    s, ct, b = get("https://schools.civicsearch.org/main.js")
    open(f"{OUT}/civic_main.js", "wb").write(b)
    t = b.decode("utf-8", "replace")
    hits = sorted(set(re.findall(r'["\'`]([^"\'`]{0,60}(?:api|get_|search|meeting)[^"\'`]{0,60})["\'`]', t)))
    return f"{len(b)} bytes\n" + "\n".join(h for h in hits if "/" in h or "get_" in h)[:20000]
step("civicsearch main.js", civic)

# --- Germany: Regionalstatistik GENESIS REST (POST with credentials in headers)
def genesis():
    out = []
    for base in ["https://www.regionalstatistik.de/genesisws/rest/2020", "https://www-genesis.destatis.de/genesisWS/rest/2020"]:
        h = {"username": "GAST", "password": "GAST", "Content-Type": "application/x-www-form-urlencoded"}
        try:
            s, ct, b = get(base + "/helloworld/logincheck", data=b"language=de", hdr=h, method="POST", n=2000); out.append(f"{base} logincheck {s} {b[:300]!r}")
        except Exception as e:
            out.append(f"{base} logincheck ERR {e}")
        for name in ["21111-01-03-4", "21111-02-06-4", "21111-01-04-4", "21111-02-01-4"]:
            body = urllib.parse.urlencode({"name": name, "area": "all", "compress": "false", "format": "ffcsv", "language": "de"}).encode()
            try:
                s, ct, b = get(base + "/data/tablefile", data=body, hdr=h, method="POST")
                fn = f"de_{name}_{'rs' if 'regional' in base else 'ds'}.csv"
                open(f"{OUT}/{fn}", "wb").write(b); out.append(f"{name} {s} {ct} {len(b)} {b[:300]!r}")
            except Exception as e:
                out.append(f"{name} ERR {e}")
            time.sleep(2)
    return "\n".join(out)
step("genesis POST", genesis)

# --- Iceland: pupils by school (SKO02102), metadata and all data
def iceland():
    u = "https://px.hagstofa.is/pxis/api/v1/is/Samfelag/skolamal/2_grunnskolastig/0_gsNemendur/SKO02102.px"
    s, ct, meta = get(u); open(f"{OUT}/is_SKO02102_meta.json", "wb").write(meta)
    m = json.loads(meta)
    q = {"query": [{"code": v["code"], "selection": {"filter": "item", "values": v["values"] if v["code"].lower().startswith(("sk", "school", "ár", "ar", "year")) or len(v["values"]) < 3 else [v["values"][0]]}} for v in m["variables"]],
         "response": {"format": "csv"}}
    # keep every school and the latest year; for other variables take their first value (usually the total)
    for qq, v in zip(q["query"], m["variables"]):
        txt = (v.get("text") or "").lower()
        if "ár" in txt or "year" in txt: qq["selection"]["values"] = [v["values"][-1]]
        elif "skól" in txt: qq["selection"]["values"] = v["values"]
        else: qq["selection"]["values"] = [v["values"][0]]
    s, ct, b = get(u, data=json.dumps(q).encode(), hdr={"Content-Type": "application/json"}, method="POST")
    open(f"{OUT}/is_SKO02102.csv", "wb").write(b)
    return json.dumps([(v["code"], v["text"], len(v["values"]), v["valueTexts"][:3], v["valueTexts"][-2:]) for v in m["variables"]], ensure_ascii=False) + f"\n{len(b)} bytes"
step("iceland SKO02102", iceland)
step("iceland schools register", lambda: save("is_grunnskolar.html", "https://island.is/grunnskolar"))

# --- Ireland: school-level enrolment (primary and post-primary)
step("ireland primary 2024/25", lambda: save("ie_primary_2024_25.xlsx", "https://assets.gov.ie/static/documents/09fe3ad4/Data_on_Individual_Schools_Mainstream_2024_25.xlsx"))
step("ireland primary latest", lambda: save("ie_primary_latest.xlsx", "https://assets.gov.ie/static/documents/8e1b86ab/Data_on_Individual_Schools_Mainstream..xlsx"))
def ie_pp():
    s, ct, b = get("https://www.gov.ie/en/department-of-education/collections/post-primary-schools-enrolment-figures/")
    t = b.decode("utf-8", "replace")
    xs = sorted(set(re.findall(r'href=["\']([^"\']+\.xlsx?)["\']', t)))
    out = "\n".join(xs)
    pick = [x for x in xs if re.search(r"202[45]", x)] or xs[-1:]
    for i, x in enumerate(pick[:3]):
        out += "\n" + save(f"ie_postprimary_{i}.xlsx", urllib.parse.urljoin("https://www.gov.ie/", x))
    return out
step("ireland post-primary", ie_pp)

# --- Ireland ETBs: board minutes pages (for meeting counts)
ETB = ["https://www.cdetb.ie", "https://www.ddletb.ie", "https://www.cmetb.ie", "https://www.cetb.ie", "https://www.corketb.ie", "https://www.donegaletb.ie",
       "https://www.gretb.ie", "https://www.kwetb.ie", "https://www.kerryetb.ie", "https://www.kcetb.ie", "https://www.lcetb.ie", "https://www.lmetb.ie",
       "https://www.loetb.ie", "https://www.msletb.ie", "https://www.tipperaryetb.ie", "https://www.wwetb.ie"]
def etbs():
    out = []
    for u in ETB:
        try:
            s, ct, b = get(u, timeout=60); t = b.decode("utf-8", "replace")
            hs = sorted(set(urllib.parse.urljoin(u, h) for h in re.findall(r'href=["\']([^"\']+)["\']', t) if re.search(r"board|minute|meeting|governance|about", h, re.I)))
            out.append(f"{u} {s} {len(b)}\n  " + "\n  ".join(hs[:40]))
        except Exception as e:
            out.append(f"{u} ERR {e}")
        time.sleep(2)
    return "\n".join(out)
step("ireland ETB sites", etbs)

# --- Mexico: CONEVAL municipal poverty 2020, INEGI census 2020 by locality (school attendance), borders
step("coneval concentrado", lambda: save("mx_coneval_2020.zip", "https://www.coneval.org.mx/Medicion/Documents/Pobreza_municipal/2020/Concentrado_indicadores_de_pobreza_2020.zip"))
def coneval_pages():
    out = []
    for u in ["https://www.coneval.org.mx/Medicion/Paginas/Pobreza-municipio-2010-2020.aspx", "https://www.coneval.org.mx/Medicion/Paginas/Pobreza_municipal.aspx",
              "https://www.coneval.org.mx/Medicion/Paginas/pobreza-municipal-grupos-poblacion.aspx"]:
        try:
            s, ct, b = get(u); t = b.decode("utf-8", "replace")
            out.append(f"{u} {s}\n  " + "\n  ".join(sorted(set(re.findall(r'href=["\']([^"\']+\.(?:zip|xlsx?|csv))["\']', t, re.I)))))
        except Exception as e:
            out.append(f"{u} ERR {e}")
    return "\n".join(out)
step("coneval pages", coneval_pages)
def iter_mx():
    s, ct, b = get("https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/iter/iter_00_cpv2020_csv.zip", timeout=900)
    out = f"{s} {ct} {len(b)}"
    z = zipfile.ZipFile(io.BytesIO(b)); out += "\n" + "\n".join(z.namelist())
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    rows = csv.reader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig", errors="replace"))
    hdr = next(rows); out += "\n" + ",".join(hdr)
    with open(f"{OUT}/mx_iter_municipal.csv", "w", newline="") as fo:
        w = csv.writer(fo); w.writerow(hdr)
        for r in rows:
            if len(r) > 5 and r[hdr.index("LOC")] == "0000" and r[hdr.index("MUN")] != "000": w.writerow(r)   # municipal totals
    return out
step("inegi iter 2020", iter_mx)
step("geoboundaries MEX ADM2", lambda: save("mx_adm2.geojson", "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/MEX/ADM2/geoBoundaries-MEX-ADM2_simplified.geojson"))

# --- Brazil: school census summary, census 2022 income tables, Bolsa Família by municipality, borders
def inep():
    s, ct, b = get("https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2025.zip", timeout=900)
    z = zipfile.ZipFile(io.BytesIO(b)); names = z.namelist()
    keep = [n for n in names if n.lower().endswith((".xlsx", ".xls"))]
    for n in keep:
        open(f"{OUT}/br_sinopse_2025.xlsx", "wb").write(z.read(n)); break
    return f"{len(b)} bytes\n" + "\n".join(f"{i.filename} {i.file_size}" for i in z.infolist())
step("inep sinopse 2025", inep)
def sidra():
    s, ct, b = get("https://servicodados.ibge.gov.br/api/v3/agregados", timeout=600)
    d = json.loads(b); out = []
    for p in d:
        for a in p.get("agregados", []):
            nm = a.get("nome", "")
            if re.search(r"rendimento", nm, re.I) and re.search(r"censo|2022", p.get("nome", "") + nm, re.I):
                out.append(f"{a['id']} | {p.get('nome')} | {nm}")
    return "\n".join(out[:300])
step("sidra income tables", sidra)
def bf():
    out = []
    for ym in ["202509", "202508", "202506"]:
        u = f"https://portaldatransparencia.gov.br/download-de-dados/novo-bolsa-familia/{ym}"
        try:
            s, ct, b = get(u, n=2000, method="HEAD") if False else get(u, n=2000)
            out.append(f"{u} {s} {ct} {b[:200]!r}")
            break
        except Exception as e:
            out.append(f"{u} ERR {e}")
    return "\n".join(out)
step("bolsa familia probe", bf)
step("geoboundaries BRA ADM2", lambda: save("br_adm2.geojson", "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/BRA/ADM2/geoBoundaries-BRA-ADM2_simplified.geojson"))

# keep only what fits in git
for f in os.listdir(OUT):
    p = os.path.join(OUT, f)
    if os.path.getsize(p) > 90_000_000:
        log.write(f"removed {f} ({os.path.getsize(p)} bytes): too big for git\n"); os.remove(p)
log.close()
