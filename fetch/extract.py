# Temporary: foundations and source discovery for Belgium and Portugal.
import html, io, json, os, re, subprocess, time, traceback, urllib.parse, urllib.request, zipfile
OUT = "fetch/out/bp1"; os.makedirs(OUT, exist_ok=True)
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
subprocess.run("npm install -g mapshaper@0.6 >/dev/null 2>&1", shell=True)

def lau():
    b = get("https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_2024_4326.geojson", 900)
    d = json.loads(b); out = []
    for cc in ("BE", "PT"):
        fs = [f for f in d["features"] if f["properties"].get("CNTR_CODE") == cc]
        json.dump({"type": "FeatureCollection", "features": fs}, open(f"/tmp/lau_{cc}.geojson", "w"))
        r = subprocess.run(f"mapshaper /tmp/lau_{cc}.geojson -simplify 8% keep-shapes -o precision=0.0001 format=geojson {OUT}/lau_{cc}.geojson", shell=True, capture_output=True, text=True)
        out.append(f"{cc}: {len(fs)} features; sample {fs[0]['properties'] if fs else ''}; {r.stderr[-150:]}")
    return "\n".join(out)
step("GISCO LAU 2024", lau)

def statbel():
    out, links = [], set()
    for u in ["https://statbel.fgov.be/en/open-data?category=All&page=0", "https://statbel.fgov.be/en/open-data?category=All&page=1",
              "https://statbel.fgov.be/en/open-data?category=All&page=2", "https://statbel.fgov.be/en/open-data?category=All&page=3",
              "https://statbel.fgov.be/en/open-data?category=All&page=4", "https://statbel.fgov.be/en/open-data?category=All&page=5",
              "https://statbel.fgov.be/en/open-data/fiscal-statistics-income", "https://statbel.fgov.be/nl/open-data/fiscale-statistiek-van-de-inkomens",
              "https://statbel.fgov.be/en/open-data/code-lists-refnis", "https://statbel.fgov.be/en/open-data/population-place-residence"]:
        try:
            t = get(u, 120).decode("utf-8", "ignore")
            for h, txt in re.findall(r'href="([^"]+)"[^>]*>([^<]{0,140})<', t):
                if re.search(r"\.(zip|xlsx?|csv|txt)(\?|$)", h, re.I) or "/open-data/" in h: links.add((html.unescape(h), re.sub(r"\s+", " ", txt).strip()))
        except Exception as e: out.append(f"ERR {u} {str(e)[:80]}")
        time.sleep(1)
    keep = sorted(l for l in links if re.search(r"income|inkomen|revenu|fisc|refnis|munic|gemeente|population|bevolking|tax", l[0] + l[1], re.I))
    json.dump(keep, open(f"{OUT}/statbel_links.json", "w"), ensure_ascii=False, indent=0)
    out.append(f"{len(links)} links, {len(keep)} relevant: " + json.dumps(keep[:60], ensure_ascii=False)[:5000])
    # download the likely files
    got = 0
    for h, txt in keep:
        if re.search(r"\.(zip|xlsx|csv|txt)", h, re.I) and re.search(r"TAX|MUNTY|INC|refnis|REFNIS|POP", h) and got < 10:
            u = h if h.startswith("http") else "https://statbel.fgov.be" + h
            try:
                b = get(u, 300); fn = re.sub(r"[^A-Za-z0-9_.-]", "_", u.split("/")[-1].split("?")[0])[-80:]
                open(f"{OUT}/be_{fn}", "wb").write(b); out.append(f"downloaded {fn} {len(b)}"); got += 1
            except Exception as e: out.append(f"dl ERR {u} {str(e)[:80]}")
            time.sleep(1)
    return "\n".join(out)
step("Statbel open data", statbel)

def flanders():
    out = []
    for u in ["https://www.vlaanderen.be/statistiek-vlaanderen/sociaal-beschermd-wonen/kansarmoede", "https://www.kindengezin.be/nl/cijfers-en-rapporten/cijfers/kansarmoede",
              "https://www.vlaanderen.be/statistiek-vlaanderen/armoede/kansarmoede-bij-kinderen", "https://www.vlaanderen.be/lokaal-bestuur/gemeente-stadsmonitor",
              "https://provincies.incijfers.be/databank"]:
        try:
            t = get(u, 120).decode("utf-8", "ignore")
            ls = sorted({html.unescape(h) for h in re.findall(r'href="([^"]+)"', t) if re.search(r"kansarmoed|\.xlsx|\.csv|download", h, re.I)})
            out.append(f"{u}: {len(t)} bytes; links {ls[:25]}")
        except Exception as e: out.append(f"{u}: ERR {str(e)[:100]}")
        time.sleep(1)
    return "\n".join(out)
step("Flanders child deprivation (kansarmoede) discovery", flanders)

def portugal():
    out = []
    for q in ["rendimento social de inserção município", "beneficiários rendimento social de inserção concelho", "alunos matriculados concelho",
              "alunos ensino básico município", "rendimento declarado município", "população residente município"]:
        try:
            d = json.loads(get("https://dados.gov.pt/api/1/datasets/?page_size=20&q=" + urllib.parse.quote(q), 120))
            for ds in d.get("data", []):
                res = [(r.get("title"), r.get("format"), r.get("url")) for r in ds.get("resources", [])][:6]
                out.append(f"[{q}] {ds.get('title')} | {ds.get('organization', {}) and ds['organization'].get('name')} | {res}")
        except Exception as e: out.append(f"[{q}] ERR {str(e)[:100]}")
        time.sleep(1)
    # INE's indicator API: metadata for a few likely indicators (RSI beneficiaries, declared income, pupils)
    for v in ["0008279", "0008280", "0008351", "0008352", "0008353", "0010016", "0008282", "0009966", "0011176", "0011177"]:
        try:
            d = json.loads(get(f"https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp?varcd={v}&lang=PT", 60))
            m = d[0] if isinstance(d, list) else d
            out.append(f"INE {v}: {str(m.get('IndicadorDsg') or m)[:200]} | geo {str(m.get('Dimensao') or '')[:200]}")
        except Exception as e: out.append(f"INE {v}: ERR {str(e)[:80]}")
        time.sleep(0.5)
    return "\n".join(out)
step("Portugal discovery", portugal)
log.close()
