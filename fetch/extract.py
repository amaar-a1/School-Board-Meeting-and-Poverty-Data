# Temporary: CSO Census 2022 local authority layer (31 boundaries, population aged 0-19 by single year).
import json, os, time, urllib.request
OUT = "fetch/out/ie3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
u = "https://services-eu1.arcgis.com/BuS9rtTsYEV5C0xh/arcgis/rest/services/CensusHub2022_T1_1_LA/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson&maxAllowableOffset=0.003"
with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r:
    open(f"{OUT}/ie_la_census2022_t1_1.geojson", "wb").write(r.read())
