# Round 48: earlier years for change over time: Poland (BDL family benefit, 2015-2023), Chile (comunal poverty
# estimates, every edition), Italy (IRPEF by comune, 2015-2022), the Netherlands (CBS pupils by municipality, every
# school year; CBS child poverty, every year; DUO primary pupils by municipality, every year).
import os, re, json, urllib.request, urllib.parse, time, zipfile, io, html
OUT = "fetch/out/c48"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def raw(url, timeout=300, tries=5):
    for t in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(20 * (t + 1)); continue
            raise
    raise RuntimeError("429 " + url)
def get(name, url, timeout=300):
    try:
        b = raw(url, timeout)
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(1.5)
# Poland: BDL, family benefit share (259889) and children with it (259888), gminy (level 6), 2015-2023
BDL = "https://bdl.stat.gov.pl/api/v1"
pl = {}
for vid in ("259889", "259888"):
    vals = {}
    for yr in range(2015, 2024):
        page, got = 0, 0
        while True:
            try: d = json.loads(raw(f"{BDL}/data/by-variable/{vid}?unit-level=6&year={yr}&page-size=100&page={page}&format=json&lang=pl"))
            except Exception as e: log.write(f"PL {vid} {yr} ERR {str(e)[:120]}\n"); break
            for r in d.get("results", []):
                for x in r.get("values", []):
                    if x.get("val") is not None: vals.setdefault(r["id"], {})[str(x.get("year", yr))] = x["val"]; got += 1
            if not d.get("links", {}).get("next"): break
            page += 1; time.sleep(1.2)
        log.write(f"PL {vid} {yr}: {got}\n"); log.flush()
    pl[vid] = vals
json.dump(pl, open(f"{OUT}/pl_bdl_history.json", "w"))
# Chile: every comunal poverty page, and the Excel files it links
for y in ("2011", "2013", "2015", "2017", "2020", "2022"):
    b = get(f"cl_page_{y}.html", f"https://observatorio.ministeriodesarrollosocial.gob.cl/pobreza-comunal-{y}")
    if not b: continue
    t = b.decode("utf-8", "ignore")
    links = sorted(set(html.unescape(x) for x in re.findall(r'href="([^"]+\.(?:xlsx?|zip))"', t, re.I)))
    log.write(f"  CL {y} links {links}\n")
    for l in links:
        u = urllib.parse.urljoin("https://observatorio.ministeriodesarrollosocial.gob.cl/", l)
        get(f"cl_{y}_" + os.path.basename(urllib.parse.urlparse(u).path)[-90:], u)
# Italy: IRPEF by comune, tax years 2015-2022 (only the CSV inside the zip is kept)
for yr in range(2015, 2023):
    b = get(None, f"https://www1.finanze.gov.it/finanze/analisi_stat/public/v_4_0_0/contenuti/Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_{yr}.zip", timeout=600)
    if b:
        try:
            z = zipfile.ZipFile(io.BytesIO(b))
            for n in z.namelist():
                if n.lower().endswith(".csv"): open(f"{OUT}/it_irpef_{yr}.csv", "wb").write(z.read(n))
        except Exception as e: log.write(f"IT {yr} zip ERR {e}\n")
# Netherlands: CBS 85701NED pupils by municipality of residence, every school year (one request per year)
for y in range(2011, 2026):
    f = urllib.parse.quote(f"Geslacht eq 'T001038' and Perioden eq '{y}SJ00' and (Onderwijssoort eq 'A025279' or Onderwijssoort eq 'A025282' or Onderwijssoort eq 'T001345') and substringof('GM',Regiokenmerken)")
    get(f"nl_pupils_{y}.json", f"https://opendata.cbs.nl/ODataApi/odata/85701NED/TypedDataSet?$format=json&$filter={f}")
get("nl_85701_Onderwijssoort.json", "https://opendata.cbs.nl/ODataApi/odata/85701NED/Onderwijssoort?$format=json")
# CBS 86132NED child poverty, every year
p = json.loads(get(None, "https://opendata.cbs.nl/ODataApi/odata/86132NED/PersoonsEnHuishoudenskenmerken?$format=json") or b'{"value":[]}')["value"]
tot = next((x["Key"].strip() for x in p if re.search(r"totaal", x["Title"], re.I)), p[0]["Key"].strip() if p else "")
get("nl_86132_Perioden.json", "https://opendata.cbs.nl/ODataApi/odata/86132NED/Perioden?$format=json")
f = urllib.parse.quote(f"PersoonsEnHuishoudenskenmerken eq '{tot}' and substringof('GM',RegioS)")
get("nl_childpoverty_all.json", f"https://opendata.cbs.nl/ODataApi/odata/86132NED/TypedDataSet?$format=json&$filter={f}")
# DUO: primary pupils by municipality, every year
get("nl_duo_po_gemeenten.csv", "https://onderwijsdata.duo.nl/dataset/323841f2-75b9-4f03-9fe9-c4d2679f2b2b/resource/947ecf4a-3744-4f59-ad98-6ce4107dafa2/download/06-historische-leerlingenaantallen-po-gemeenten-api.csv")
log.close()
