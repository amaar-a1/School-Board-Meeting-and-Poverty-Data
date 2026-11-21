# Round 4b: Argentina's provinces' Census 2022 population (Wikipedia table citing INDEC; INDEC's own census site fails TLS).
import os, urllib.request, urllib.parse, time
OUT = "fetch/out/ar4b"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
W = "https://es.wikipedia.org/w/api.php?action=parse&format=json&prop=wikitext&page="
for n, p in [("wiki_jurisdicciones.json", "Anexo:Jurisdicciones de primer orden de Argentina por superficie, población y densidad (2022)")]:
    try:
        b = urllib.request.urlopen(urllib.request.Request(W + urllib.parse.quote(p), headers=UA), timeout=120).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)}\n")
    except Exception as e: log.write(f"== {n} ERR {e}\n")
