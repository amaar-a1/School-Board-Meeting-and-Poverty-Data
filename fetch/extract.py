# Temporary: where Belgium's pupil counts by municipality are published, in each language community.
import html, json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/bep1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1200:]}\n\n")
    log.flush()

def french():
    out = []
    for q in ["élèves", "population scolaire", "inscrits", "fondamental", "élèves par commune"]:
        try:
            d = json.loads(get("https://www.odwb.be/api/explore/v2.1/catalog/datasets?limit=50&where=" + urllib.parse.quote(f'search("{q}")')))
            for ds in d.get("results", []):
                m = ds.get("metas", {}).get("default", {})
                out.append(f"[{q}] {ds.get('dataset_id')} | {m.get('title')} | {m.get('publisher')} | records {m.get('records_count')} | fields {[f.get('name') for f in ds.get('fields', [])][:14]}")
        except Exception as e: out.append(f"[{q}] ERR {str(e)[:100]}")
        time.sleep(1)
    return "\n".join(sorted(set(out)))
step("French Community: odwb.be", french)

def flemish():
    out = []
    for u in ["https://data-onderwijs.vlaanderen.be/", "https://data-onderwijs.vlaanderen.be/onderwijsaanbod/", "https://onderwijs.vlaanderen.be/nl/onderwijsstatistieken/dataloep-aan-de-slag-met-cijfers-over-onderwijs",
              "https://onderwijs.vlaanderen.be/nl/onderwijsstatistieken/statistisch-jaarboek-van-het-vlaams-onderwijs"]:
        try:
            t = get(u).decode("utf-8", "ignore")
            ls = sorted({html.unescape(h) for h in re.findall(r'href="([^"]+)"', t) if re.search(r"leerling|\.xlsx|\.csv|\.zip|gemeente|jaarboek|download|dataset", h, re.I)})
            out.append(f"{u}: {len(t)} bytes; {ls[:40]}")
        except Exception as e: out.append(f"{u}: ERR {str(e)[:100]}")
        time.sleep(1)
    for q in ["leerlingen basisonderwijs gemeente", "leerlingenaantallen", "leerlingen per gemeente"]:
        for api in [f"https://opendata.vlaanderen.be/api/3/action/package_search?rows=20&q={urllib.parse.quote(q)}",
                    f"https://data.vlaanderen.be/api/3/action/package_search?rows=20&q={urllib.parse.quote(q)}"]:
            try:
                d = json.loads(get(api))
                for ds in d.get("result", {}).get("results", []):
                    out.append(f"[{q}] {ds.get('title')} | {[(r.get('format'), r.get('url')) for r in ds.get('resources', [])][:4]}")
            except Exception as e: out.append(f"[{q}] {api[:40]} ERR {str(e)[:80]}")
            time.sleep(1)
    return "\n".join(out)
step("Flemish Community", flemish)

def german():
    out = []
    for u in ["https://ostbelgienstatistik.be/desktopdefault.aspx/tabid-2507/", "https://www.ostbelgienstatistik.be/", "https://ostbelgienbildung.be/"]:
        try:
            t = get(u).decode("utf-8", "ignore")
            ls = sorted({html.unescape(h) for h in re.findall(r'href="([^"]+)"', t) if re.search(r"sch[üu]ler|bildung|unterricht|\.xlsx|\.csv", h, re.I)})
            out.append(f"{u}: {len(t)} bytes; {ls[:30]}")
        except Exception as e: out.append(f"{u}: ERR {str(e)[:100]}")
        time.sleep(1)
    return "\n".join(out)
step("German-speaking Community", german)
log.close()
