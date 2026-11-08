# Temporary: Croatia. DZS small-area poverty estimates (report and presentation), GISCO LAU 2024 borders for HR.
import json, os, traceback, urllib.request
OUT = "fetch/out/hr1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=900):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read()
for name, u in {"dzs_sae.pdf": "https://web.dzs.hr/hrv/important/PressCorner/Mapiranje%20i%20procjena%20geografske%20raspodjele%20rizika%20od%20siromastva%20i%20socijalne%20iskljucenosti%20za%20mala%20podrucja%20Republike%20Hrvatske.pdf",
                "dzs_sae_pres.pdf": "https://web.dzs.hr/Hrv/important/PressCorner/Prezentacije/Mapiranje%20i%20procjena%20geografske%20raspodjele%20rizika%20od%20siromastva%20i%20socijalne%20iskljucenosti%20za%20mala%20podrucja%20RH%20-%20Prezentacija.pdf",
                "dzs_2022.pdf": "https://novi-web.dzs.hr/media/pprhctvu/zudp-2023-1-1-pokazatelji-siromaštva-i-socijalne-isključenosti-u-2022.pdf".replace("š", "%C5%A1").replace("č", "%C4%8D")}.items():
    try:
        b = get(u); open(f"{OUT}/{name}", "wb").write(b); log.write(f"ok {name} {len(b)}\n")
    except Exception as e: log.write(f"ERR {name} {str(e)[:150]}\n")
log.flush()
try:
    g = json.loads(get("https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_2024_4326.geojson", 1800))
    hr = [f for f in g["features"] if f["properties"].get("CNTR_CODE") == "HR"]
    json.dump({"type": "FeatureCollection", "features": hr}, open(f"{OUT}/lau_HR.geojson", "w"))
    log.write(f"lau HR {len(hr)} {hr[0]['properties'] if hr else ''}\n")
except Exception: log.write(traceback.format_exc()[-800:])
log.close()
