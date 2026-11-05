# Temporary: probe sources for Chile and the Philippines (poverty, enrollment, borders).
import json, os, re, time, urllib.parse, urllib.request
OUT = "fetch/out/clph1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research script; github.com/amaar-a1)", "Accept": "text/html,application/json,*/*"}
log = []
def get(url, name=None):
    time.sleep(1.5)
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180); d = r.read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {r.geturl()[:200]}"); return d, r.geturl()
    except Exception as e:
        log.append(f"FAIL {url[:200]}: {e}"); return None, url
def links(d, base, pat):
    return sorted({urllib.parse.urljoin(base, l.decode(errors="ignore")) for l in re.findall(rb'href="([^"]+)"', d or b"") if re.search(pat, l.decode(errors="ignore"), re.I)})
# Borders (geoBoundaries)
for iso in ("CHL", "PHL"):
    d, _ = get(f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/ADM3/", f"gb_{iso}_ADM3.json")
    if d:
        j = json.loads(d); log.append(f"{iso} ADM3 {j.get('boundaryName')} {j.get('admUnitCount')} {j.get('simplifiedGeometryGeoJSON')}")
        u = j.get("simplifiedGeometryGeoJSON")
        if u: get(u, f"gb_{iso}_ADM3_simplified.geojson")
# Chile poverty (Ministerio de Desarrollo Social, pobreza comunal)
for u in ("https://observatorio.ministeriodesarrollosocial.gob.cl/pobreza-comunal", "https://observatorio.ministeriodesarrollosocial.gob.cl/pobreza-comunal-2022"):
    d, f = get(u, re.sub(r"\W+", "_", u)[-40:] + ".html")
    found = links(d, f, r"\.xlsx|\.xls|\.csv|pobreza")
    open(f"{OUT}/cl_poverty_links.txt", "a").write("\n".join(found) + "\n")
    for l in [x for x in found if re.search(r"\.xlsx?$", x)][:4]:
        get(l, "cl_" + os.path.basename(urllib.parse.urlparse(l).path)[:80])
# Chile enrollment (Mineduc open data)
for u in ("https://datosabiertos.mineduc.cl/matricula-en-educacion-escolar/", "https://datosabiertos.mineduc.cl/resumen-de-matricula-por-establecimiento-educacional/"):
    d, f = get(u, re.sub(r"\W+", "_", u)[-40:] + ".html")
    open(f"{OUT}/cl_enrol_links.txt", "a").write("\n".join(links(d, f, r"\.zip|\.csv|\.rar|resumen|matr")) + "\n")
# Philippines poverty (PSA small area estimates)
for u in ("https://psa.gov.ph/statistics/poverty", "https://psa.gov.ph/statistics/poverty/small-area-estimates", "https://psa.gov.ph/content/2021-city-and-municipal-level-poverty-estimates"):
    d, f = get(u, re.sub(r"\W+", "_", u)[-40:] + ".html")
    open(f"{OUT}/ph_poverty_links.txt", "a").write("\n".join(links(d, f, r"\.xlsx|\.xls|\.pdf|small-area|municipal")) + "\n")
# Philippines enrollment (DepEd)
for u in ("https://www.deped.gov.ph/learner-information-system/", "https://data.gov.ph/index/public/dataset/search?q=enrollment"):
    d, f = get(u, re.sub(r"\W+", "_", u)[-40:] + ".html")
    open(f"{OUT}/ph_enrol_links.txt", "a").write("\n".join(links(d, f, r"\.xlsx|\.csv|enrol")) + "\n")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
