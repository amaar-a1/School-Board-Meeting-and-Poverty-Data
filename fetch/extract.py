# Temporary: third pass. CivicSearch monthly meeting counts for every place; Brazil census tables; INEP; Regionalatlas.
import json, os, re, urllib.request, urllib.parse, time, traceback, subprocess
OUT = "fetch/out/g4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(url, n=None, timeout=300):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read() if n is None else r.read(n)
def step(name, f):
    t = time.time()
    try: res = f(); log.write(f"== {name} ({time.time()-t:.0f}s)\n{res}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-800:]}\n\n")
    log.flush()

def sidra():
    for attempt in range(3):
        try:
            d = json.loads(get("https://servicodados.ibge.gov.br/api/v3/agregados", timeout=600)[2]); break
        except Exception as e:
            err = e; time.sleep(30)
    else:
        raise err
    out = []
    for p in d:
        for a in p.get("agregados", []):
            nm = a.get("nome", "")
            if re.search(r"rendimento|frequent|escola|pobreza|matr", nm, re.I) and re.search(r"2022", p.get("nome", "") + nm):
                out.append(f"{a['id']} | {p.get('nome')} | {nm}")
    json.dump(d, open(f"{OUT}/sidra_agregados.json", "w"))
    return "\n".join(out[:400])
step("sidra tables", sidra)
def sidra_meta():
    out = []
    for t in re.findall(r"^(\d+) \|", open(f"{OUT}/log.txt").read(), re.M)[:60]:
        try:
            m = json.loads(get(f"https://servicodados.ibge.gov.br/api/v3/agregados/{t}/metadados", timeout=120)[2])
            lv = m.get("nivelTerritorial", {}).get("Administrativo", [])
            if "N6" in lv:
                out.append(f"{t} {m.get('nome')} | vars: " + "; ".join(f"{v['id']}:{v['nome']}" for v in m.get("variaveis", [])[:8]) +
                           " | cls: " + "; ".join(f"{c['id']}:{c['nome']}[" + ", ".join(f"{x['id']}:{x['nome']}" for x in c.get("categorias", [])[:14]) + "]" for c in m.get("classificacoes", [])))
        except Exception as e:
            out.append(f"{t} ERR {e}")
        time.sleep(1)
    return "\n".join(out)
step("sidra metadata (municipal tables)", sidra_meta)

def inep():
    r = subprocess.run(["curl", "-v", "-sSL", "--retry", "5", "--retry-all-errors", "--retry-delay", "30", "-m", "2400", "-A", UA["User-Agent"],
                        "-o", f"{OUT}/br_sinopse_2025.zip", "-w", "%{http_code} %{size_download}",
                        "https://download.inep.gov.br/dados_abertos/sinopses_estatisticas/sinopse_estatistica_censo_escolar_2025.zip"], capture_output=True, text=True)
    out = r.stdout + "\n" + r.stderr[-1500:]
    import zipfile
    if os.path.exists(f"{OUT}/br_sinopse_2025.zip") and zipfile.is_zipfile(f"{OUT}/br_sinopse_2025.zip"):
        z = zipfile.ZipFile(f"{OUT}/br_sinopse_2025.zip"); out += "\n" + "\n".join(f"{i.filename} {i.file_size}" for i in z.infolist())
        xl = max((i for i in z.infolist() if i.filename.lower().endswith((".xlsx", ".xls"))), key=lambda i: i.file_size)
        open(f"{OUT}/br_sinopse_2025.xlsx", "wb").write(z.read(xl))
    if os.path.exists(f"{OUT}/br_sinopse_2025.zip"): os.remove(f"{OUT}/br_sinopse_2025.zip")
    return out
step("inep sinopse 2025", inep)

def ra():
    s, ct, b = get("https://regionalatlas.statistikportal.de/"); t = b.decode("utf-8", "replace")
    out = []
    for j in sorted(set(re.findall(r'src=["\']([^"\']+\.js)["\']', t))):
        u = urllib.parse.urljoin("https://regionalatlas.statistikportal.de/", j)
        try:
            _, _, jb = get(u); jt = jb.decode("utf-8", "replace")
            urls = sorted(set(re.findall(r'https?://[^"\'\s]+(?:MapServer|FeatureServer|rest/services|\.json)[^"\'\s]*', jt)))
            ai = sorted(set(re.findall(r'\bAI\d{4,6}\b|\bai\d{4,6}\b', jt)))[:50]
            out.append(f"{u} {len(jb)} urls {urls[:30]} ids {ai}")
            if "config" in u.lower() or urls: open(f"{OUT}/ra_{os.path.basename(u)}", "wb").write(jb)
        except Exception as e:
            out.append(f"{u} ERR {e}")
    return "\n".join(out)
step("regionalatlas app", ra)

def civic():
    pl = json.loads(get("https://schools.civicsearch.org/api/get_place_list")[2])
    res = {}; t0 = time.time()
    for i, p in enumerate(pl):
        q = {"keywords": "board", "lonlat": f"{p['longitude']},{p['latitude']}", "search_radius": "0", "start_date": "2000-01-01", "end_date": "2026-12-31"}
        for attempt in range(3):
            try:
                d = json.loads(get("https://schools.civicsearch.org/api/search?" + urllib.parse.urlencode(q), timeout=120)[2])
                res[p["query_id"]] = {"num_meetings": p["num_meetings"], "last_meeting_title": p["last_meeting_title"],
                                      "locations": d.get("location_counts"), "months": d.get("matched_meeting_counts")}
                break
            except Exception as e:
                res[p["query_id"]] = {"error": str(e)}; time.sleep(10)
        time.sleep(1)
        if time.time() - t0 > 4.5 * 3600: break
    json.dump(res, open(f"{OUT}/civic_months.json", "w"))
    ok = [v for v in res.values() if "months" in v]
    full = sum(1 for v in ok if sum((v["months"] or {}).values()) == v["num_meetings"])
    return f"{len(res)} of {len(pl)} places; {len(ok)} answered; {full} with monthly counts adding up to the place's total"
step("civicsearch months", civic)
log.close()
