# Temporary: Portugal's INE indicators by municipality and DGEEC pupils; Belgium's integration income (leefloon /
# revenu d'intégration) by municipality and population by age.
import html, io, json, os, re, time, traceback, urllib.parse, urllib.request, zipfile
OUT = "fetch/out/bp3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r:
        return r.read()
def step(name, f):
    t = time.time()
    try: log.write(f"== {name}\n{f()}\n({time.time()-t:.0f}s)\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1500:]}\n\n")
    log.flush()

INE = "https://www.ine.pt/ine/json_indicador"
def portugal():
    out = []
    want = {"0010284": "abono_children", "0010283": "abono_all", "0013420": "rsi_per1000_working_age", "0013417": "rsi_n",
            "0012749": "median_income_taxpayer", "0008273": "pop_age", "0012751": "taxpayers"}
    for v, name in want.items():
        try:
            meta = json.loads(get(f"{INE}/pindicaMeta.jsp?varcd={v}&lang=PT", 120))
            m = meta[0] if isinstance(meta, list) else meta
            last = m.get("UltimoPef") or m.get("UltimoPeriodo")
            out.append(f"{v} {name}: {str(m.get('IndicadorNome'))[:160]} | last {last} | dims {str(m.get('Dimensoes') or m.get('Dimensao'))[:300]}")
            json.dump(m, open(f"{OUT}/pt_meta_{v}.json", "w"), ensure_ascii=False)
            yrs = [y for y in re.findall(r"\b(20\d\d)\b", str(last))] or ["2024"]
            for y in [yrs[-1], str(int(yrs[-1]) - 1)]:
                try:
                    b = get(f"{INE}/pindica.jsp?op=2&varcd={v}&Dim1=S7A{y}&lang=PT", 300)
                    d = json.loads(b)
                    n = sum(len(vv) for x in (d if isinstance(d, list) else [d]) for vv in (x.get("Dados") or {}).values())
                    out.append(f"   {y}: {len(b)} bytes, {n} values")
                    if n > 300: open(f"{OUT}/pt_{v}_{y}.json", "wb").write(b); break
                except Exception as e: out.append(f"   {y}: ERR {str(e)[:80]}")
        except Exception as e: out.append(f"{v} ERR {str(e)[:100]}")
        time.sleep(1)
    # DGEEC pupils dataset: its resources
    try:
        d = json.loads(get("https://dados.gov.pt/api/1/datasets/?page_size=10&q=" + urllib.parse.quote("Alunos matriculados na educação pré-escolar e nos ensinos básico"), 120))
        for ds in d.get("data", [])[:3]:
            out.append(f"DGEEC {ds.get('title')} {ds.get('id')}")
            for r in ds.get("resources", [])[:30]:
                out.append(f"   {r.get('title')} | {r.get('format')} | {r.get('url')}")
            res = [r for r in ds.get("resources", []) if (r.get("format") or "").lower() in ("csv", "xlsx", "xls", "json")]
            res.sort(key=lambda r: r.get("title") or "")
            for r in res[-2:]:
                try: b = get(r["url"], 300); open(f"{OUT}/pt_dgeec_{re.sub(r'[^A-Za-z0-9.]+', '_', r.get('title') or 'x')[:60]}.{(r.get('format') or 'csv').lower()}", "wb").write(b); out.append(f"   downloaded {r.get('title')} {len(b)}")
                except Exception as e: out.append(f"   dl ERR {str(e)[:80]}")
    except Exception as e: out.append(f"DGEEC ERR {str(e)[:100]}")
    return "\n".join(out)
step("Portugal", portugal)

def belgium():
    out = []
    for u in ["https://stat.mi-is.be/fr", "https://stat.mi-is.be/nl", "https://stat.mi-is.be/fr/dashboard/ris_ris_par_commune",
              "https://www.mi-is.be/fr/etudes-publications-statistiques/statistiques", "https://www.mi-is.be/nl/studies-publicaties-statistieken/statistieken"]:
        try:
            t = get(u, 120).decode("utf-8", "ignore")
            ls = sorted({html.unescape(h) for h in re.findall(r'href="([^"]+)"', t) if re.search(r"\.(xlsx?|csv|zip)|download|export|commune|gemeente|ris|leefloon", h, re.I)})
            out.append(f"{u}: {len(t)} bytes; {ls[:40]}")
        except Exception as e: out.append(f"{u}: ERR {str(e)[:100]}")
        time.sleep(1)
    # population by age and municipality
    try:
        t = get("https://statbel.fgov.be/en/open-data?category=All&page=0", 120).decode("utf-8", "ignore")
    except Exception: t = ""
    for p in ["/en/open-data/population-place-residence-nationality-marital-status-age-and-sex-16", "/en/open-data/population-place-residence-nationality-marital-status-age-and-sex-15"]:
        try:
            t = get("https://statbel.fgov.be" + p, 120).decode("utf-8", "ignore")
            ls = sorted({html.unescape(h) for h in re.findall(r'href="([^"]+\.(?:zip|xlsx|txt))"', t, re.I)})
            out.append(f"{p}: {ls}")
            z = next((h for h in ls if h.lower().endswith(".zip")), None)
            if z:
                u = z if z.startswith("http") else "https://statbel.fgov.be" + z
                b = get(u, 600); zf = zipfile.ZipFile(io.BytesIO(b))
                out.append(f"  zip {len(b)}: {zf.namelist()}")
                # keep only municipality x age totals (sum over sex, nationality, marital status)
                name = zf.namelist()[0]; import csv
                rd = csv.reader(io.TextIOWrapper(zf.open(name), encoding="utf-8-sig", errors="replace"), delimiter="|")
                h = next(rd); out.append(f"  header {h}")
                iref = next(i for i, c in enumerate(h) if c.upper() == "CD_REFNIS"); iage = next(i for i, c in enumerate(h) if c.upper() == "CD_AGE"); ipop = next(i for i, c in enumerate(h) if c.upper() == "MS_POPULATION")
                agg = {}
                for r in rd:
                    a = agg.setdefault(r[iref], {"total": 0, "u18": 0}); n = int(r[ipop] or 0); a["total"] += n
                    if int(r[iage] or 99) < 18: a["u18"] += n
                json.dump(agg, open(f"{OUT}/be_pop_age_{p[-2:]}.json", "w")); out.append(f"  {len(agg)} municipalities")
                break
        except Exception as e: out.append(f"{p}: ERR {traceback.format_exc()[-400:]}")
    return "\n".join(out)
step("Belgium", belgium)
log.close()
