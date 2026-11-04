# Temporary: world fetch part 5: the six German districts missed by name search.
import os, urllib.request
OUT = "fetch/out/w5"; os.makedirs(OUT, exist_ok=True)
u = "https://www.wegweiser-kommune.de/data-api/rest/export/kinderarmut+berlin+hamburg+weiden-in-der-oberpfalz+dillingen-an-der-donau-lk+neumarkt-in-der-oberpfalz-lk+regen-lk+2021-2023+tabelle.csv"
req = urllib.request.Request(u, headers={"User-Agent": "school-board-research-script (github.com/amaar-a1)"})
open(f"{OUT}/de_ww_fix.csv", "wb").write(urllib.request.urlopen(req, timeout=300).read())
