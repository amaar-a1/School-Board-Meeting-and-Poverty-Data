# Round 4 (second branch): Argentina's provincial legislatures on YouTube with dates; province populations (Census 2022).
import os, urllib.request, urllib.parse, json, time, subprocess, sys
OUT = "fetch/out/ar4"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
def get(name, url, timeout=300):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"== {name} OK {len(b)} {url}\n"); log.flush(); return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n"); log.flush()
    finally: time.sleep(2)
W = "https://es.wikipedia.org/w/api.php?action=parse&format=json&prop=wikitext&page="
for p in ["Anexo:Provincias de Argentina por población", "Censo de Argentina de 2022", "Anexo:Provincias de Argentina por superficie"]:
    get("wiki_" + p.split(":")[-1].replace(" ", "_") + ".json", W + urllib.parse.quote(p))
for u in ["https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165", "https://censo.gob.ar/index.php/datos_definitivos_total_pais/"]:
    get("page_" + str(abs(hash(u)) % 10**6) + ".html", u)
r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], capture_output=True, text=True)
log.write(f"== pip rc {r.returncode}\n"); log.flush()
r = subprocess.run([sys.executable, "fetch/ar_yt2.py", OUT], capture_output=True, text=True, timeout=5 * 3600)
log.write(f"== ar_yt2 rc {r.returncode} {r.stderr[-600:]}\n")
