# Round 13: Costa Rica population and pupils by canton (MEP statistics pages and files; Wikipedia's canton list).
import os, re, urllib.request, urllib.parse, time
OUT = "fetch/out/cr13"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
def get(n, u):
    try:
        b = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=300).read()
        open(f"{OUT}/{n}", "wb").write(b); log.write(f"== {n} OK {len(b)} {u}\n"); return b
    except Exception as e: log.write(f"== {n} ERR {e} {u}\n")
    finally: time.sleep(2)
get("wiki_es.html", "https://es.wikipedia.org/w/index.php?title=Anexo:Cantones_de_Costa_Rica&action=render")
get("wiki_en.html", "https://en.wikipedia.org/w/index.php?title=List_of_cantons_of_Costa_Rica&action=render")
get("mep_cantonales.pdf", "https://www.mep.go.cr/sites/default/files/2024-05/IndicadoresEducativosCantonales20102018.pdf")
seen = set()
for n, u in [("mep_est.html", "https://www.mep.go.cr/acerca-del-mep/analisis-estadistico/estadisticas-educativas"),
             ("mep_censo.html", "https://www.mep.go.cr/acerca-del-mep/analisis-estadistico/censo-escolar"),
             ("mep_ind.html", "https://mep.go.cr/indicadores-educativos")]:
    b = get(n, u)
    if not b: continue
    for l, t in re.findall(rb'href="([^"]+)"[^>]*>([^<]{0,120})', b):
        s = (l + b" " + t).decode("utf-8", "replace")
        if re.search(r"\.(xlsx?|csv|pdf|zip)\b", l.decode("utf-8", "replace"), re.I) or re.search(r"matr|cant", s, re.I): log.write("   link " + s + "\n")
        full = urllib.parse.urljoin(u, l.decode("utf-8", "replace"))
        if re.search(r"\.(xlsx?|csv)\b", full, re.I) and re.search(r"cant|matr", s, re.I) and full not in seen and len(seen) < 25:
            seen.add(full); get("dl_%02d_" % len(seen) + re.sub(r"[^A-Za-z0-9._-]", "_", full.rsplit("/", 1)[-1])[-60:], full)
