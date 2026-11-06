# Temporary: Spain ADRH municipal figures (poverty by age, demographics); Peru poverty map 2018 text and district borders.
import json, os, re, subprocess, time, traceback, urllib.request, zipfile, glob
OUT = "fetch/out/pe_es5"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=600):
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
        except Exception as e:
            err = e; time.sleep(20)
    raise err
def step(name, f):
    t = time.time()
    try: log.write(f"== {name} ({time.time()-t:.0f}s)\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-800:]}\n\n")
    log.flush()
def municipal(d):
    # keep series whose territory is a municipality (codes in MetaData: Variable "Municipios")
    out = []
    for s in d:
        if not isinstance(s, dict): continue
        md = s.get("MetaData") or []
        terr = [m for m in md if m.get("T3_Variable") == "Municipios"]
        if not terr: continue
        out.append({"code": terr[0].get("Codigo"), "name": terr[0].get("Nombre"),
                    "meta": [m.get("Nombre") for m in md if m not in terr],
                    "data": {str(x["Anyo"]): x["Valor"] for x in s.get("Data", []) if x.get("Valor") is not None}})
    return out
def es_pov():
    res, n = [], 0
    for tid in json.load(open("fetch/es_rel_age_ids.json")):
        d = json.loads(get(f"https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{tid}?nult=6&tip=AM"))
        if not isinstance(d, list): log.write(f"table {tid}: {str(d)[:200]}\n"); continue
        m = [x for x in municipal(d) if "Total" in x["meta"] and "Población con ingresos por unidad de consumo por debajo 60% de la mediana" in x["meta"]]
        res += m; n += 1; time.sleep(1)
    json.dump(res, open(f"{OUT}/es_poverty_60_by_age.json", "w"), ensure_ascii=False)
    return f"{n} tables; {len(res)} municipal series; example {res[:2]}"
def es_dem():
    res = []
    for tid in json.load(open("fetch/es_dem_ids.json")):
        d = json.loads(get(f"https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/{tid}?nult=2&tip=AM"))
        if not isinstance(d, list): log.write(f"table {tid}: {str(d)[:200]}\n"); continue
        res += municipal(d); time.sleep(1)
    json.dump(res, open(f"{OUT}/es_demographics.json", "w"), ensure_ascii=False)
    return f"{len(res)} municipal series; kinds {sorted(set(' | '.join(x['meta']) for x in res))[:20]}"
step("Spain poverty by age", es_pov)
step("Spain demographics", es_dem)
def pe_pdf():
    open("/tmp/map.pdf", "wb").write(get("https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1718/Libro.pdf"))
    subprocess.run(["sudo", "apt-get", "install", "-y", "-qq", "poppler-utils"], capture_output=True)
    r = subprocess.run(["pdftotext", "-layout", "/tmp/map.pdf", f"{OUT}/pe_mapa_pobreza_2018.txt"], capture_output=True, text=True)
    t = open(f"{OUT}/pe_mapa_pobreza_2018.txt", encoding="utf-8", errors="replace").read()
    return f"{r.returncode} {r.stderr[:200]} chars {len(t)}; sample: {t[len(t)//2:len(t)//2+2500]}"
def pe_geo():
    b = get("https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_distrital_simple.geojson")
    open(f"{OUT}/pe_districts.geojson", "wb").write(b); g = json.loads(b)
    return f"{len(b)} bytes; {len(g['features'])} features; props {g['features'][0]['properties']}"
step("Peru district borders", pe_geo)
def es_geo():
    b = get("https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ESP/ADM3/geoBoundaries-ESP-ADM3_simplified.geojson")
    open(f"{OUT}/gb_ESP_ADM3.geojson", "wb").write(b); g = json.loads(b)
    b2 = get("https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/ESP/ADM2/geoBoundaries-ESP-ADM2_simplified.geojson")
    open(f"{OUT}/gb_ESP_ADM2.geojson", "wb").write(b2)
    return f"{len(b)} bytes; {len(g['features'])} features; props {g['features'][0]['properties']}"
step("Spain municipal borders", es_geo)
log.close()
