# Round 3: borders (Israel OSM, Argentina IGN), more source searches, Israel council meetings on YouTube.
import os, urllib.request, urllib.parse, json, time, subprocess, sys
OUT = "fetch/out/arisr3"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=300):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"== {name} OK {len(b)} {url}\n"); log.flush(); return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n"); log.flush()
    finally: time.sleep(2)
pip = lambda *p: subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", *p], capture_output=True, text=True)
r = pip("osmium", "shapely", "yt-dlp"); log.write(f"== pip rc {r.returncode} {r.stderr[-400:]}\n")
r = subprocess.run([sys.executable, "fetch/borders.py", OUT], capture_output=True, text=True, timeout=3600)
log.write(f"== borders rc {r.returncode} {r.stdout[-300:]} {r.stderr[-800:]}\n"); log.flush()
# Argentina: other sources of pupils by province
for q in ["anuario", "alumnos", "estudiantes", "matricula provincia", "relevamiento anual"]:
    get(f"ar_datos_{q.replace(' ', '_')}.json", "https://datos.gob.ar/api/3/action/package_search?rows=50&q=" + urllib.parse.quote(q))
for u in ["https://www.argentina.gob.ar/educacion/evaluacion-informacion/anuarios", "https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/anuario-estadistico",
          "https://www.argentina.gob.ar/educacion/evaluacion-informacion-educativa/bdd", "https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/series-y-anuarios"]:
    get("ar_page_" + u.rstrip("/").split("/")[-1] + ".html", u)
# Israel: population by locality and newer education data
get("il_org_edu.json", "https://data.gov.il/api/3/action/organization_show?id=ministry_of_education&include_datasets=true")
for q in ["אוכלוסייה", "תושבים לפי יישוב", "מספר תושבים", "population"]:
    get("il_ckan_" + str(abs(hash(q)) % 10**6) + ".json", "https://data.gov.il/api/3/action/package_search?rows=40&q=" + urllib.parse.quote(q))
# Israel: council meetings on YouTube
r = subprocess.run([sys.executable, "fetch/il_yt.py", "fetch/out/arisr2/il_authorities.csv", OUT], capture_output=True, text=True, timeout=4 * 3600)
log.write(f"== il_yt rc {r.returncode} {r.stderr[-500:]}\n")
for fn in os.listdir(OUT):
    if os.path.getsize(f"{OUT}/{fn}") > 90e6: log.write(f"== dropped {fn}\n"); os.remove(f"{OUT}/{fn}")
