# Round 50: population (and some poverty) over time from sources already used, or official ones not yet used:
# Eurostat GISCO LAU population for every year 2016-2023; Eurostat NUTS 3 population (Germany's districts, Switzerland's
# cantons); IBGE municipal estimates (Brazil); ONS mid-year estimates by local authority (UK, via Nomis); e-Stat
# municipal population and welfare recipients (Japan); DSS payment demographics, every June (Australia) and ABS's
# dataflow list; links to CONAPO (Mexico) and DANE (Colombia) municipal projections; INDEC province projections (Argentina).
import os, re, json, urllib.request, urllib.parse, time, html, gc
OUT = "fetch/out/c50"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def raw(url, timeout=600):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
def get(name, url, timeout=600):
    try:
        b = raw(url, timeout)
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url}\n")
    finally: log.flush(); time.sleep(1.5)
def links(b, base, pat):
    t = b.decode("utf-8", "ignore")
    return sorted(set(urllib.parse.urljoin(base, html.unescape(x)) for x in re.findall(r'href="([^"]+)"', t) if re.search(pat, x, re.I)))

# 1. GISCO LAU: each LAU's population, every year (properties POP_YYYY or POP_YEAR)
for y in range(2016, 2024):
    b = get(None, f"https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_{y}_4326.geojson", timeout=1200)
    if not b: continue
    try:
        feats = json.loads(b)["features"]; del b; gc.collect()
        props = feats[0]["properties"]; log.write(f"  LAU {y} props {list(props)}\n")
        out = {}
        for f in feats:
            p = f["properties"]
            pop = next((v for k, v in p.items() if k.upper().startswith("POP") and "DENS" not in k.upper() and v not in (None, "")), None)
            if pop is not None: out.setdefault(p.get("CNTR_CODE"), {})[p.get("GISCO_ID") or p.get("LAU_ID")] = pop
        json.dump(out, open(f"{OUT}/lau_pop_{y}.json", "w")); log.write(f"  LAU {y}: {sum(len(v) for v in out.values())} with population\n")
        del feats, out; gc.collect()
    except Exception as e: log.write(f"  LAU {y} ERR {e}\n")
    log.flush()
# 2. Eurostat NUTS 3 population, every year (Germany, Switzerland)
for c in ("DE", "CH"):
    get(f"es_pop_nuts3_{c}.json", f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_r_pjanaggr3?sex=T&age=TOTAL&unit=NR&geoLevel=nuts3&lang=EN&format=JSON" + "".join(f"&geo={c}" for _ in [0])[:0] + f"&geo_prefix={c}")
get("es_pop_nuts3_all.json", "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_r_pjanaggr3?sex=T&age=TOTAL&unit=NR&geoLevel=nuts3&lang=EN")
# 3. Brazil: IBGE population estimates by municipality, every year (SIDRA table 6579)
get("br_sidra_6579.json", "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/all", timeout=1200)
# 4. UK: ONS mid-year population estimates, local authorities (Nomis NM_2002_1), 2011 on
for t in ("TYPE424", "TYPE423", "TYPE432", "TYPE431"):
    get(f"uk_nomis_{t}.csv", f"https://www.nomisweb.co.uk/api/v01/dataset/NM_2002_1.data.csv?geography={t}&date=latestMINUS14-latest&gender=0&c_age=200&measures=20100&select=date_name,geography_code,geography_name,obs_value")
# 5. Japan: e-Stat municipal data (SSDS 0000020201): total population (A1101) and welfare recipients (生活保護被保護実人員)
key = os.environ.get("ESTAT_APP_ID", "")
if key:
    base = "https://api.e-stat.go.jp/rest/3.0/app/json"
    try:
        meta = json.loads(raw(f"{base}/getMetaInfo?appId={key}&statsDataId=0000020201"))
        cls = meta["GET_META_INFO"]["METADATA_INF"]["CLASS_INF"]["CLASS_OBJ"]
        cat = next(c for c in cls if c["@id"] == "cat01")["CLASS"]
        want = [c for c in cat if c["@code"] == "A1101" or "被保護実人員" in c.get("@name", "") or "生活保護" in c.get("@name", "")]
        json.dump([{k: c.get(k) for k in ("@code", "@name")} for c in want], open(f"{OUT}/jp_ssds_codes.json", "w"), ensure_ascii=False)
        log.write(f"JP codes {[(c['@code'], c['@name']) for c in want]}\n")
        for c in want[:4]:
            vals, pos = [], 1
            while pos:
                d = json.loads(raw(f"{base}/getStatsData?appId={key}&statsDataId=0000020201&cdCat01={c['@code']}&limit=100000&startPosition={pos}"))
                sd = d["GET_STATS_DATA"]["STATISTICAL_DATA"]
                v = sd.get("DATA_INF", {}).get("VALUE", [])
                vals += [{"area": x.get("@area"), "time": x.get("@time"), "v": x.get("$")} for x in (v if isinstance(v, list) else [v])]
                pos = sd.get("RESULT_INF", {}).get("NEXT_KEY"); time.sleep(1)
            json.dump(vals, open(f"{OUT}/jp_ssds_{c['@code']}.json", "w")); log.write(f"JP {c['@code']}: {len(vals)}\n")
    except Exception as e: log.write(f"JP ERR {str(e)[:200]}\n")
    log.flush()
# 6. Australia: DSS payment demographics, the June file of each year; ABS dataflows (for LGA population)
try:
    pk = json.loads(raw("https://data.gov.au/data/api/3/action/package_show?id=dss-payment-demographic-data"))["result"]["resources"]
    json.dump([{k: r.get(k) for k in ("name", "url", "created")} for r in pk], open(f"{OUT}/au_dss_resources.json", "w"), indent=0)
    for r in pk:
        n = (r.get("name") or "") + " " + (r.get("url") or "")
        m = re.search(r"june[-_ ]?(20\d\d)", n, re.I)
        if m and 2016 <= int(m.group(1)) <= 2025 and re.search(r"\.xlsx?$", r.get("url", ""), re.I):
            get(f"au_dss_june_{m.group(1)}.xlsx", r["url"])
except Exception as e: log.write(f"AU DSS ERR {e}\n")
get("au_abs_dataflows.xml", "https://data.api.abs.gov.au/rest/dataflow/ABS?detail=allstubs")
for fl in ("ABS_ANNUAL_ERP_LGA2024", "ABS_ANNUAL_ERP_LGA2023", "ABS_ANNUAL_ERP_ASGS2021"):
    get(f"au_{fl}.csv", f"https://data.api.abs.gov.au/rest/data/ABS,{fl}/all?format=csvfilewithlabels")
# 7. Mexico (CONAPO) and Colombia (DANE): municipal projections, from their pages' links
for name, page, pat in (("mx", "https://www.gob.mx/conapo/documentos/reconstruccion-y-proyecciones-de-la-poblacion-de-los-municipios-de-mexico-2015-2030", r"munic|\.csv|\.xlsx|\.zip"),
                        ("mx2", "https://www.gob.mx/conapo/documentos/bases-de-datos-de-la-conciliacion-demografica-1950-a-2019-y-proyecciones-de-la-poblacion-de-mexico-2020-a-2070", r"munic"),
                        ("co", "https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion", r"Mun|munic")):
    b = get(f"{name}_page.html", page)
    if not b: continue
    ls = links(b, page, pat); log.write(f"  {name} links {ls[:40]}\n")
    for l in [l for l in ls if re.search(r"\.(xlsx?|csv|zip)$", l, re.I)][:6]:
        get(f"{name}_" + os.path.basename(urllib.parse.urlparse(l).path)[-90:], l, timeout=1200)
# 8. Argentina: INDEC population projections by province, 2010-2040
get("ar_proy_prov.xls", "https://www.indec.gob.ar/ftp/cuadros/poblacion/c1_proyecciones_prov_2010_2040.xls")
log.flush()
# Files too big for GitHub (100 MB): gzipped.
import gzip, shutil
for f in os.listdir(OUT):
    p = f"{OUT}/{f}"
    if os.path.getsize(p) > 50e6 and not f.endswith(".gz"):
        with open(p, "rb") as a, gzip.open(p + ".gz", "wb") as b: shutil.copyfileobj(a, b)
        os.remove(p)
log.close()
