# Round 66: census population by canton/department/county/district from Wikipedia's tables (which cite the national
# statistics offices), through the MediaWiki API's parse action (rendered HTML): Costa Rica, Uruguay, Kenya, Rwanda,
# Ecuador, and Peru's provinces/districts lists. English and Spanish pages.
import os, json, urllib.request, urllib.parse, time
OUT = "fetch/out/c66"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "school-board-research-project/1.0 (github.com/amaar-a1)", "Accept": "*/*"}
pages = [("en", "Cantons of Costa Rica"), ("es", "Anexo:Cantones de Costa Rica"), ("es", "Anexo:Cantones de Costa Rica por población"),
         ("en", "Departments of Uruguay"), ("es", "Departamentos de Uruguay"),
         ("en", "Counties of Kenya"), ("en", "Districts of Rwanda"),
         ("es", "Anexo:Cantones de Ecuador"), ("es", "Anexo:Cantones de Ecuador por población"), ("en", "Cantons of Ecuador"),
         ("es", "Anexo:Distritos del Perú"), ("es", "Anexo:Provincias del Perú")]
for lang, t in pages:
    u = f"https://{lang}.wikipedia.org/w/api.php?action=parse&format=json&prop=text|revid&redirects=1&page=" + urllib.parse.quote(t)
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
        j = json.loads(b)
        if "parse" in j:
            open(f"{OUT}/wp_{lang}_{t.replace(':', '_').replace(' ', '_')}.html", "w", encoding="utf-8").write(j["parse"]["text"]["*"])
            log.write(f"OK {lang} {t} rev {j['parse'].get('revid')} {len(b)}\n")
        else: log.write(f"MISS {lang} {t} {str(j)[:200]}\n")
    except Exception as e: log.write(f"ERR {lang} {t} {e}\n")
    log.flush(); time.sleep(1.5)
log.close()
