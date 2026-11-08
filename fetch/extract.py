# Temporary: Croatia poverty map, World Bank copies.
import json, os, urllib.request
OUT = "fetch/out/hr3"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for name, u in {"wb_page.html": "https://www.worldbank.org/en/country/croatia/publication/croatia-poverty-maps",
                "wb_brief.html": "https://www.worldbank.org/en/country/croatia/brief/croatia-poverty-maps-a-policy-tool-to-combat-poverty-and-social-exclusion",
                "md7891.html": "https://microdata.worldbank.org/catalog/7891/related-materials",
                "md_search.json": "https://microdata.worldbank.org/index.php/api/catalog/search?sk=croatia%20poverty%20map&ps=50",
                "dc_search.json": "https://datacatalogapi.worldbank.org/ddhxext/Search?qname=dataset&qterm=croatia%20poverty%20map&$top=20",
                "infographic.html": "https://www.worldbank.org/en/news/infographic/2016/10/19/croatia-mapping-poverty"}.items():
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=180) as r: b = r.read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"ok {name} {len(b)}\n")
    except Exception as e: log.write(f"ERR {name} {str(e)[:150]}\n")
log.close()
