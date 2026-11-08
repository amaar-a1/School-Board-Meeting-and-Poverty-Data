# Temporary: Croatia's counties (NUTS 3, 2024) from GISCO, to place each city and municipality in its county.
import json, os, urllib.request
OUT = "fetch/out/hr5"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
with urllib.request.urlopen(urllib.request.Request("https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2024_4326_LEVL_3.geojson", headers=UA), timeout=600) as r:
    g = json.loads(r.read())
json.dump({"type": "FeatureCollection", "features": [f for f in g["features"] if f["properties"].get("CNTR_CODE") == "HR"]}, open(f"{OUT}/nuts3_HR.geojson", "w"))
