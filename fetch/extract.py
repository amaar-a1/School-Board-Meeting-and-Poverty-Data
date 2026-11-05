# Temporary: Chile enrollment by comuna (2026 rar); Colombia municipal poverty (census) and MEN 2024.
import csv, glob, io, json, os, re, subprocess, time, urllib.parse, urllib.request
OUT = "fetch/out/clph3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research script; github.com/amaar-a1)", "Accept": "text/html,application/json,*/*"}
log = []
def get(url, name=None):
    time.sleep(1.5)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300); d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {r.geturl()[:200]}"); return d, r.geturl()
    except Exception as e:
        log.append(f"FAIL {url[:200]}: {e}"); return None, url
# Chile: unpack and add up by comuna
subprocess.run("sudo apt-get install -y -qq unar >/dev/null 2>&1 || sudo apt-get install -y -qq p7zip-full >/dev/null 2>&1", shell=True)
rar = "fetch/out/clph2/cl_Resumen-de-Matricula-EE-2026.rar"
os.makedirs("/tmp/clrar", exist_ok=True)
subprocess.run(f"unar -q -o /tmp/clrar {rar} || 7z x -y -o/tmp/clrar {rar}", shell=True)
files = glob.glob("/tmp/clrar/**/*.csv", recursive=True) + glob.glob("/tmp/clrar/**/*.txt", recursive=True)
log.append("rar files: " + ", ".join(files))
if files:
    raw = open(files[0], "rb").read()
    txt = raw.decode("utf-8", errors="ignore") if b"\xc3" in raw[:200000] else raw.decode("latin-1")
    sep = ";" if txt[:2000].count(";") > txt[:2000].count(",") else ","
    rows = list(csv.DictReader(io.StringIO(txt), delimiter=sep))
    log.append("columns: " + ", ".join(rows[0].keys()))
    open(f"{OUT}/cl_enrol_head.csv", "w").write(txt[:3000])
    key = next(k for k in rows[0] if re.fullmatch(r"COD_COM_RBD|COD_COMUNA", k.strip(), re.I))
    tot = next(k for k in rows[0] if re.fullmatch(r"MAT_TOTAL", k.strip(), re.I))
    dep = next((k for k in rows[0] if re.fullmatch(r"COD_DEPE2?|COD_DEPE", k.strip(), re.I)), None)
    agg = {}
    for r in rows:
        try: n = int(float((r[tot] or "0").replace(",", ".")))
        except ValueError: continue
        a = agg.setdefault(r[key].strip(), {"total": 0, "by_dependency": {}})
        a["total"] += n
        if dep: a["by_dependency"][r[dep]] = a["by_dependency"].get(r[dep], 0) + n
    json.dump(agg, open(f"{OUT}/cl_enrol_by_comuna_2026.json", "w"))
# Colombia: census-based municipal multidimensional poverty
d, f = get("https://www.dane.gov.co/index.php/estadisticas-por-tema/pobreza-y-condiciones-de-vida/pobreza-y-desigualdad/medida-de-pobreza-multidimensional-de-fuente-censal", "co_censal.html")
ls = sorted({urllib.parse.urljoin(f, l.decode(errors="ignore")) for l in re.findall(rb'href="([^"]+)"', d or b"")} )
open(f"{OUT}/co_censal_links.txt", "w").write("\n".join(ls))
for l in [x for x in ls if re.search(r"\.xlsx?$", x) and re.search(r"munic|mpio|censal|cnpv|anexo", x, re.I)][:4]:
    get(l, "co_" + os.path.basename(urllib.parse.urlparse(l).path)[:80])
# MEN statistics by municipality, 2024 (and field list)
get("https://www.datos.gov.co/resource/nudc-7mev.json?$where=a_o%3D%272024%27&$limit=5000", "co_men_2024.json")
get("https://www.datos.gov.co/api/views/nudc-7mev.json", "co_men_meta.json")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
