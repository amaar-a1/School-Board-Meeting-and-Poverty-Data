# Temporary: Belgian pupils by municipality for Brussels (BISA / IBSA) and Flanders (other routes).
import html, json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/bep3"; os.makedirs(OUT, exist_ok=True)
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
    return t, sorted({(html.unescape(h), re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip()[:90]) for h, x in re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>', t, re.S) if re.search(pat, h + x, re.I)})

def brussels():
    out = []
    for u in ["https://bisa.brussels/themas/onderwijs/herkomst-bestemming-van-de-leerlingen", "https://ibsa.brussels/themes/enseignement/origine-destination-des-eleves",
              "https://bisa.brussels/themas/onderwijs", "https://ibsa.brussels/themes/enseignement"]:
        try:
            t, ls = links(u, r"\.xlsx|\.xls|\.csv")
            out.append(f"{u}: {len(t)} bytes; {ls[:30]}")
            for h, x in ls[:8]:
                v = h if h.startswith("http") else "https://" + urllib.parse.urlsplit(u).netloc + h
                fn = re.sub(r"[^A-Za-z0-9_.-]", "_", v.split("/")[-1])[-80:]
                if os.path.exists(f"{OUT}/bx_{fn}"): continue
                try: b = get(v, 300); open(f"{OUT}/bx_{fn}", "wb").write(b); out.append(f"   downloaded {fn} {len(b)} ({x})")
                except Exception as e: out.append(f"   dl ERR {fn} {str(e)[:60]}")
        except Exception as e: out.append(f"{u}: ERR {str(e)[:100]}")
        time.sleep(1)
    return "\n".join(out)
step("Brussels", brussels)

def flanders():
    out = []
    for u in ["http://data-onderwijs.vlaanderen.be/onderwijsaanbod/", "https://data-onderwijs.vlaanderen.be/onderwijsaanbod/lijst.aspx?hs=311",
              "https://www.vlaanderen.be/statistiek-vlaanderen/onderwijs-en-vorming/leerlingenkenmerken",
              "https://www.vlaanderen.be/statistiek-vlaanderen/onderwijs-en-vorming/leerling-leerkrachtratio",
              "https://onderwijs.vlaanderen.be/nl/onderwijsprofessionals/regelgeving-data-en-onderzoek/data-en-onderzoek/kennisplatform-onderwijs/dataloeptoepassingen/dataloep-leerlingenkenmerken-basis-en-secundair-onderwijs",
              "https://onderwijs.vlaanderen.be/nl/onderwijsprofessionals/regelgeving-data-en-onderzoek/data-en-onderzoek/onderwijsstatistieken/statistisch-jaarboek-van-het-vlaams-onderwijs"]:
        try:
            t, ls = links(u, r"\.xlsx|\.xls|\.csv|\.zip|leerling|jaarboek|gemeente|dataloep")
            out.append(f"{u}: {len(t)} bytes; {ls[:30]}")
        except Exception as e: out.append(f"{u}: ERR {str(e)[:100]}")
        time.sleep(1)
    return "\n".join(out)
step("Flanders", flanders)
log.close()
