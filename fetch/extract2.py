# Round 52: the Netherlands' child poverty by municipality, every year (CBS 86132NED, republished 25 November 2026;
# round 48 found it closed for the republication). Also its metadata, and CBS's table list in case the ID changed.
import os, re, json, urllib.request, urllib.parse, time
OUT = "fetch/out/c52"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=600):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        if name: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n"); return b
    except Exception as e: log.write(f"ERR {name} {str(e)[:200]} {url}\n")
    finally: log.flush(); time.sleep(1.5)
B = "https://opendata.cbs.nl/ODataApi/odata/86132NED"
for part in ("TableInfos", "DataProperties", "Perioden", "PersoonsEnHuishoudenskenmerken"):
    get(f"nl_86132_{part}.json", f"{B}/{part}?$format=json")
p = json.loads(open(f"{OUT}/nl_86132_PersoonsEnHuishoudenskenmerken.json").read())["value"] if os.path.exists(f"{OUT}/nl_86132_PersoonsEnHuishoudenskenmerken.json") else []
tot = next((x["Key"].strip() for x in p if re.search(r"totaal", x["Title"], re.I)), p[0]["Key"].strip() if p else "")
per = json.loads(open(f"{OUT}/nl_86132_Perioden.json").read())["value"] if os.path.exists(f"{OUT}/nl_86132_Perioden.json") else []
for y in [x["Key"].strip() for x in per]:
    f = urllib.parse.quote(f"PersoonsEnHuishoudenskenmerken eq '{tot}' and Perioden eq '{y}' and substringof('GM',RegioS)")
    get(f"nl_childpoverty_{y}.json", f"{B}/TypedDataSet?$format=json&$filter={f}")
# If the table moved: CBS's catalogue entries about children in poverty
get("nl_catalog_armoede.json", "https://opendata.cbs.nl/ODataCatalog/Tables?$format=json&$filter=" + urllib.parse.quote("substringof('armoede',Title) or substringof('laag inkomen',Title)"))
log.close()
