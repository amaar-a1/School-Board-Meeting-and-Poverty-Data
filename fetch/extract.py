# Round 9: Slovenia income/unemployment search, Taiwan senior-high files, Uruguay poverty by department, Costa Rica PDFs.
import os, re, urllib.request, urllib.parse, json, time, html
OUT = "fetch/out/new4c"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
links = {}
def get(name, url, timeout=300):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"== {name} OK {len(b)} {url}\n"); log.flush()
        if name.endswith(".html"):
            t = b.decode("utf-8", "replace")
            links[name] = [[urllib.parse.urljoin(url, html.unescape(m.group(1))), re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()[:160]]
                           for m in re.finditer(r'href="([^"]+)"[^>]*>(.*?)</a>', t, re.S)]
        return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n"); log.flush()
    finally: time.sleep(2)
PX = "https://pxweb.stat.si/SiStatData/api/v1/en/Data?query="
for q in ["unemployed municipalities", "income tax municipalities", "income per capita municipalities", "registered unemployment rate municipalities", "net earnings municipalities", "social", "poverty"]:
    get("si_px_" + q.replace(" ", "_") + ".json", PX + urllib.parse.quote(q))
for a in range(4, 7):
    for b in range(1, 13):
        get(f"tw_edu_B_{a}_{b}.csv", f"https://stats.moe.gov.tw/files/opendata/edu_B_{a}_{b}.csv")
G = "https://www.gub.uy/instituto-nacional-estadistica/"
pages = [G + "comunicacion/noticias/linea-pobreza-indigencia-2025", G + "comunicacion/noticias/linea-pobreza-indigencia-2024",
         G + "comunicacion/publicaciones/estimacion-pobreza-metodo-del-ingreso-2025", G + "comunicacion/publicaciones/estimacion-pobreza-metodo-del-ingreso-2024",
         G + "datos-y-estadisticas/estadisticas/pobreza-desigualdad", G + "tematica/pobreza"]
pages += [G + f"comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/capitulo-3-aspectos-sociales-{i}" for i in range(3, 9)]
for u in pages: get("uy_" + u.rstrip("/").split("/")[-1][-60:] + ".html", u)
seen = set()
for k, v in list(links.items()):
    for u, t in v:
        if (re.search(r"/book/\d+/download", u) and re.search(r"pobre|ingreso", t + u, re.I)) or (re.search(r"\.xls", u) and re.search(r"pobre|departamento|ingreso", t, re.I) and "3.5" in t):
            if u in seen: continue
            seen.add(u); get("uy_dl_" + str(len(seen)) + (".xls" if ".xls" in u else ".pdf"), u); log.write(f"   ({t[:120]})\n")
for n, u in [("cr_atlas_reporte2.pdf", "https://hdr.undp.org/system/files/documents/national-report-document/atlas-cantonal-reporte-2.pdf"),
             ("cr_mep_cantonales_2010_2018.pdf", "https://devmep.mep.go.cr/sites/default/files/2024-05/IndicadoresEducativosCantonales20102018.pdf"),
             ("cr_mep_estadisticas.html", "https://www.mep.go.cr/estadisticas-educativas"), ("cr_mep_dae.html", "https://www.mep.go.cr/departamento-analisis-estadistico")]:
    get(n, u)
json.dump(links, open(f"{OUT}/links.json", "w"), ensure_ascii=False, indent=1)
for fn in os.listdir(OUT):
    if os.path.getsize(f"{OUT}/{fn}") > 90e6: os.remove(f"{OUT}/{fn}")
