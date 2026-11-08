# Temporary: Belgian pupils by municipality. Wallonia: IWEPS WalStat on odwb.be (download). Flanders, Brussels and the
# German-speaking Community: find the files.
import html, json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/bep2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) school-board research project; github.com/amaar-a1", "Accept": "*/*", "Accept-Language": "nl,fr,en"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=120):
    err = None
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
        except Exception as e: err = e; time.sleep(10 * (a + 1))
    raise err
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1200:]}\n\n")
    log.flush()
def links(u, pat):
    t = get(u).decode("utf-8", "ignore")
    return t, sorted({(html.unescape(h), re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()[:80]) for h, x in re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>', t, re.S) if re.search(pat, h + x, re.I)})

def wallonia():
    out = []
    for ds in ("2432000", "243300", "2434000"):
        try:
            b = get(f"https://www.odwb.be/api/explore/v2.1/catalog/datasets/{ds}/exports/json?select=ins,entite,type_entite,periode,%2A")
            d = json.loads(b); open(f"{OUT}/walstat_{ds}.json", "wb").write(b)
            out.append(f"{ds}: {len(d)} records; sample {str(d[0])[:300]}")
        except Exception as e: out.append(f"{ds}: ERR {str(e)[:100]}")
    return "\n".join(out)
step("Wallonia: WalStat pupils", wallonia)

def flanders():
    out = []
    for u in ["https://data-onderwijs.vlaanderen.be/onderwijsaanbod/lijst.aspx", "https://data-onderwijs.vlaanderen.be/",
              "https://onderwijs.vlaanderen.be/nl/onderwijsprofessionals/regelgeving-data-en-onderzoek/data-en-onderzoek/onderwijsstatistieken",
              "https://onderwijs.vlaanderen.be/nl/onderwijsstatistieken/leerlingen-in-het-basisonderwijs",
              "https://www.vlaanderen.be/statistiek-vlaanderen/onderwijs-en-vorming", "https://www.vlaanderen.be/statistiek-vlaanderen/onderwijs-en-vorming/leerlingen-in-het-basisonderwijs",
              "https://www.vlaanderen.be/gemeente-en-stadsmonitor", "https://gemeente-en-stadsmonitor.vlaanderen.be/"]:
        try:
            t, ls = links(u, r"leerling|basisonderwijs|\.xlsx|\.csv|\.zip|download|gemeente")
            out.append(f"{u}: {len(t)} bytes; {ls[:30]}")
        except Exception as e: out.append(f"{u}: ERR {str(e)[:100]}")
        time.sleep(1)
    return "\n".join(out)
step("Flanders", flanders)

def brussels():
    out = []
    for u in ["https://ibsa.brussels/themes/enseignement", "https://ibsa.brussels/themes/education", "https://bisa.brussels/themas/onderwijs",
              "https://ibsa.brussels/chiffres/chiffres-cles-par-commune"]:
        try:
            t, ls = links(u, r"\.xlsx|\.xls|\.csv|élève|eleve|leerling|commune|enseignement")
            out.append(f"{u}: {len(t)} bytes; {ls[:40]}")
        except Exception as e: out.append(f"{u}: ERR {str(e)[:100]}")
        time.sleep(1)
    return "\n".join(out)
step("Brussels: IBSA", brussels)

def german():
    out = []
    for tab in ("2295", "2302", "2294", "2296", "2326", "2335", "2517", "3374"):
        u = f"https://ostbelgienstatistik.be/desktopdefault.aspx/tabid-{tab}/"
        try:
            t = get(u).decode("utf-8", "ignore")
            title = (re.search(r"<title>(.*?)</title>", t, re.S) or [None, ""])[1].strip()[:80]
            ls = sorted({html.unescape(h) for h in re.findall(r'href="([^"]+)"', t) if re.search(r"\.xlsx|\.xls|\.csv|\.pdf|sch[üu]ler", h, re.I)})
            out.append(f"{tab} {title}: {ls[:15]}")
        except Exception as e: out.append(f"{tab}: ERR {str(e)[:80]}")
        time.sleep(1)
    return "\n".join(out)
step("German-speaking Community", german)
log.close()
