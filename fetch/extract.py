# Temporary: foundations for Poland, Italy and Japan (borders, population, poverty stand-ins, pupils), and
# discovery of source URLs where they aren't fixed.
import io, json, os, re, subprocess, time, traceback, urllib.parse, urllib.request, zipfile
OUT = "fetch/out/pij1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300, hdr=None):
    with urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}), timeout=t) as r:
        return r.read()
def step(name, f):
    t = time.time()
    try: log.write(f"== {name}\n{f()}\n({time.time()-t:.0f}s)\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1500:]}\n\n")
    log.flush()
subprocess.run("npm install -g mapshaper@0.6 >/dev/null 2>&1", shell=True)

# ---------- Borders: Eurostat GISCO LAU (Poland's gminy, Italy's comuni), with population and density
def lau():
    out = []
    for yr in ("2024", "2023", "2021"):
        u = f"https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_{yr}_4326.geojson"
        try:
            b = get(u, 900); open("/tmp/lau.geojson", "wb").write(b); out.append(f"{yr}: {len(b)} bytes"); break
        except Exception as e: out.append(f"{yr}: ERR {str(e)[:120]}")
    else: return "\n".join(out)
    d = json.load(open("/tmp/lau.geojson")); out.append(f"features {len(d['features'])}; props {list(d['features'][0]['properties'])}")
    for cc in ("PL", "IT"):
        fs = [f for f in d["features"] if f["properties"].get("CNTR_CODE") == cc]
        json.dump({"type": "FeatureCollection", "features": fs}, open(f"/tmp/lau_{cc}.geojson", "w"))
        r = subprocess.run(f"mapshaper /tmp/lau_{cc}.geojson -simplify 3% keep-shapes -o precision=0.0001 format=geojson {OUT}/lau_{cc}.geojson", shell=True, capture_output=True, text=True)
        out.append(f"{cc}: {len(fs)} features; {r.stderr[-200:]}; size {os.path.getsize(f'{OUT}/lau_{cc}.geojson') if os.path.exists(f'{OUT}/lau_{cc}.geojson') else 0}")
        out.append(f"  sample {fs[0]['properties'] if fs else ''}")
    return "\n".join(out)
step("GISCO LAU", lau)

# ---------- Poland: Statistics Poland's Local Data Bank (BDL) API - find the variables
BDL = "https://bdl.stat.gov.pl/api/v1"
def bdl_search():
    res = {}
    for q in ["pomocy społecznej", "pomoc społeczna", "korzystający", "zasiłek rodzinny", "uczniowie szkół podstawowych", "uczniowie", "ludność ogółem", "w wieku przedprodukcyjnym", "dochody budżetów gmin na mieszkańca"]:
        try:
            d = json.loads(get(f"{BDL}/variables/search?name={urllib.parse.quote(q)}&level=6&page-size=100&lang=pl&format=json", 120))
            res[q] = [{k: v.get(k) for k in ("id", "subjectId", "n1", "n2", "n3", "n4", "n5", "level", "measureUnitName")} for v in d.get("results", [])]
        except Exception as e: res[q] = f"ERR {e}"
        time.sleep(1.5)
    json.dump(res, open(f"{OUT}/pl_bdl_search.json", "w"), ensure_ascii=False, indent=0)
    subj = []
    for q in ["pomoc społeczna", "oświata", "wychowanie"]:
        try:
            d = json.loads(get(f"{BDL}/subjects/search?name={urllib.parse.quote(q)}&page-size=100&lang=pl&format=json", 120))
            subj += [{k: v.get(k) for k in ("id", "name", "parentId", "levels", "hasVariables")} for v in d.get("results", [])]
        except Exception as e: subj.append(f"ERR {e}")
        time.sleep(1.5)
    json.dump(subj, open(f"{OUT}/pl_bdl_subjects.json", "w"), ensure_ascii=False, indent=0)
    return {k: (len(v) if isinstance(v, list) else v) for k, v in res.items()}
step("Poland: BDL variable search", bdl_search)

# ---------- Italy: income tax by comune (MEF), comuni list (ISTAT), schools and pupils (Ministry of Education)
def italy():
    out = []
    for yr in ("2023", "2022", "2021"):
        u = f"https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_{yr}.zip"
        try:
            b = get(u, 300); z = zipfile.ZipFile(io.BytesIO(b)); names = z.namelist()
            for n in names:
                if n.lower().endswith(".csv"): open(f"{OUT}/it_irpef_{yr}.csv", "wb").write(z.read(n))
            out.append(f"MEF {yr}: {len(b)} bytes {names}"); break
        except Exception as e: out.append(f"MEF {yr}: ERR {str(e)[:120]}")
    for u, fn in [("https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv", "it_comuni.csv")]:
        try: b = get(u); open(f"{OUT}/{fn}", "wb").write(b); out.append(f"{fn}: {len(b)}")
        except Exception as e: out.append(f"{fn}: ERR {str(e)[:120]}")
    # Ministry of Education open data: find the latest school directory and pupils-by-school files
    try:
        page = get("https://dati.istruzione.it/opendata/opendata/catalogo/elements1/?area=Scuole", 120).decode("utf-8", "ignore")
        links = sorted(set(re.findall(r'(?:href|data-url)="([^"]+\.csv)"', page)))
        out.append(f"MIUR catalogue links: {links[:60]}")
    except Exception as e: out.append(f"MIUR catalogue: ERR {str(e)[:150]}")
    for yr in ("202425", "202324"):
        for kind in ("SCUANAGRAFESTAT", "ALUCORSOETASTA", "ALUCORSOINDCLASTA"):
            for day in ("20240901", "20230901", "20250901"):
                u = f"https://dati.istruzione.it/opendata/opendata/catalogo/elements1/{kind}{yr}{day}.csv"
                try:
                    b = get(u, 300); open(f"{OUT}/it_{kind}_{yr}.csv", "wb").write(b); out.append(f"{kind}{yr}{day}: {len(b)}"); break
                except Exception as e: pass
    return "\n".join(out)
step("Italy", italy)

# ---------- Japan: borders (geoBoundaries ADM2), and e-Stat's municipal statistics (SSDS) file listing
def japan():
    out = []
    try:
        m = json.loads(get("https://www.geoboundaries.org/api/current/gbOpen/JPN/ADM2/", 120))
        out.append(f"gb meta: {m.get('boundaryYearRepresented')} {m.get('admUnitCount')} {m.get('boundarySource')}")
        b = get(m["simplifiedGeometryGeoJSON"], 600); open("/tmp/jp.geojson", "wb").write(b)
        r = subprocess.run(f"mapshaper /tmp/jp.geojson -simplify 15% keep-shapes -o precision=0.0001 format=geojson {OUT}/gb_JPN_ADM2.geojson", shell=True, capture_output=True, text=True)
        g = json.load(open(f"{OUT}/gb_JPN_ADM2.geojson")); out.append(f"JPN ADM2 {len(g['features'])} {g['features'][0]['properties']} size {os.path.getsize(f'{OUT}/gb_JPN_ADM2.geojson')}")
        m1 = json.loads(get("https://www.geoboundaries.org/api/current/gbOpen/JPN/ADM1/", 120))
        b = get(m1["simplifiedGeometryGeoJSON"], 600); open("/tmp/jp1.geojson", "wb").write(b)
        subprocess.run(f"mapshaper /tmp/jp1.geojson -simplify 10% keep-shapes -o precision=0.001 format=geojson {OUT}/gb_JPN_ADM1.geojson", shell=True)
    except Exception as e: out.append(f"geoBoundaries ERR {str(e)[:200]}")
    for u, fn in [("https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200502&tstat=000001226576", "jp_ssds_list1.html"),
                  ("https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200502", "jp_ssds_list0.html"),
                  ("https://www.e-stat.go.jp/stat-search?page=1&query=%E7%B5%B1%E8%A8%88%E3%81%A7%E3%81%BF%E3%82%8B%E5%B8%82%E5%8C%BA%E7%94%BA%E6%9D%91%E3%81%AE%E3%81%99%E3%81%8C%E3%81%9F", "jp_ssds_search.html")]:
        try:
            b = get(u, 120); open(f"{OUT}/{fn}", "wb").write(b)
            t = b.decode("utf-8", "ignore")
            out.append(f"{fn}: {len(b)} statInfId {len(set(re.findall(r'statInfId=(\d+)', t)))} tstat {sorted(set(re.findall(r'tstat=(\d+)', t)))[:20]}")
        except Exception as e: out.append(f"{fn}: ERR {str(e)[:150]}")
    return "\n".join(out)
step("Japan", japan)
log.close()
