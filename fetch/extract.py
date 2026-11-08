# Temporary: Croatia, from the Ministry of Regional Development: the World Bank / DZS poverty-map report and the 2024
# development index with its indicators (unemployment rate, income per inhabitant) for every city and municipality.
import os, urllib.parse, urllib.request
OUT = "fetch/out/hr2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
q = lambda u: urllib.parse.quote(u, safe=":/%?=&")
for name, u in {"wb_sae.pdf": "https://razvoj.gov.hr/UserDocsImages/Istaknute%20teme/Kartom%20siroma%C5%A1tva/Croatia%20Small-Area%20Estimation%20of%20Consumption-Based%20Poverty%20(Poverty%20Maps).pdf",
                "ir_2024.pdf": q("https://razvoj.gov.hr/UserDocsImages/O ministarstvu/Regionalni razvoj/indeks razvijenosti/Vrijednosti indeksa razvijenosti i pokazatelja za izračun indeksa razvijenosti.pdf"),
                "ir_page.html": "https://razvoj.gov.hr/o-ministarstvu/regionalni-razvoj/indeks-razvijenosti/112",
                "kartom.html": "https://razvoj.gov.hr/istaknute-teme/kartom-siromastva/3949",
                "dzs_en.pdf": "https://web.dzs.hr/Eng/important/PressCorner/Mapping%20and%20estimation%20of%20the%20geographical%20distribution%20of%20risk%20of%20poverty%20and%20social%20exclusion%20for%20small%20areas%20of%20the%20Republic%20of%20Croatia.pdf"}.items():
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300) as r: b = r.read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"ok {name} {len(b)}\n")
    except Exception as e: log.write(f"ERR {name} {str(e)[:150]}\n")
log.close()
