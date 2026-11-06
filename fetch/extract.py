# Temporary: debug Spain's ADRH API with metadata, the HDX download, and Spain's municipal borders.
import json, os, urllib.request
OUT = "fetch/out/pe_es4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=600):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.status, r.geturl(), r.headers.get("Content-Type", ""), r.read()
for name, u in [("ES AM nult1", "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/30662?nult=1&tip=AM"),
                ("ES M nult1", "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/30662?nult=1&tip=M"),
                ("ES A nult6", "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/30662?nult=6&tip=A"),
                ("HDX geojson zip", "https://data.humdata.org/dataset/54fc7f4d-f4c0-4892-91f6-2fe7c1ecf363/resource/63647792-0951-40d2-a30e-4a0e60f7a176/download/per_admin_boundaries.geojson.zip")]:
    try:
        s, fu, ct, b = get(u); log.write(f"== {name} {s} {fu} {ct} {len(b)}\n{b[:1500]!r}\n\n")
        if name.startswith("ES"):
            d = json.loads(b); log.write(f"type {type(d).__name__}; first {json.dumps(d[0] if isinstance(d, list) else d, ensure_ascii=False)[:1500]}\n\n")
    except Exception as e: log.write(f"== {name} ERR {e}\n\n")
    log.flush()
log.close()
