# Round 7: discovery for Slovenia, Taiwan, Costa Rica, Uruguay. Saves each page and a list of its data-file links.
import os, re, urllib.request, urllib.parse, json, time, html
OUT = "fetch/out/new4"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*", "Accept-Language": "en,es;q=0.8,zh-TW;q=0.7,sl;q=0.6"}
links = {}
def get(name, url, timeout=180):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"== {name} OK {len(b)} {url}\n"); log.flush()
        if name.endswith(".html"):
            t = b.decode("utf-8", "replace")
            ls = []
            for m in re.finditer(r'href="([^"]+)"[^>]*>(.*?)</a>', t, re.S):
                h = html.unescape(m.group(1)); txt = re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()
                if re.search(r"\.(xlsx?|csv|ods|zip|pdf|json)(\?|$)|download|descarg|dl-|/book/", h, re.I): ls.append([urllib.parse.urljoin(url, h), txt[:150]])
            links[name] = ls
        return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n"); log.flush()
    finally: time.sleep(2)
# Slovenia: SiStat PxWeb search and the national open-data portal
PX = "https://pxweb.stat.si/SiStatData/api/v1/en/Data?query="
for q in ["social assistance municipalities", "financial social assistance", "pupils basic school municipalities", "population age groups municipalities", "children municipalities", "at-risk-of-poverty municipalities"]:
    get("si_px_" + q.replace(" ", "_")[:40] + ".json", PX + urllib.parse.quote(q))
for q in ["denarna socialna pomoč", "učenci osnovna šola občine", "prebivalstvo občine starost"]:
    get("si_ckan_" + str(abs(hash(q)) % 10**6) + ".json", "https://podatki.gov.si/api/3/action/package_search?rows=50&q=" + urllib.parse.quote(q))
# Taiwan
for d in ["40121", "6516", "31442", "7671", "8411", "117985", "32970", "18683"]:
    get(f"tw_ds_{d}.json", f"https://data.gov.tw/api/v2/rest/dataset/{d}")
    get(f"tw_ds_{d}.html", f"https://data.gov.tw/dataset/{d}")
get("tw_mohw_lowincome.html", "https://dep.mohw.gov.tw/dos/cp-5337-62357-113.html")
get("tw_moe_stats.html", "https://stats.moe.gov.tw/")
get("tw_moe_ed4500.html", "https://depart.moe.edu.tw/ED4500/News.aspx?n=5A930C32CC6C3818&sms=91B3AAE8C6388B96")
for q in ["低收入戶", "各級學校縣市別學生人數", "縣市人口 年齡"]:
    get("tw_search_" + str(abs(hash(q)) % 10**6) + ".json", "https://data.gov.tw/api/v2/rest/dataset?q=" + urllib.parse.quote(q))
# Costa Rica
for u in ["https://inec.cr/censos/censo-2022", "https://inec.cr/estadisticas-fuentes/censos/censo-2022", "https://www.mideplan.go.cr/indice-desarrollo-social",
          "https://mep.go.cr/indicadores-educativos", "https://mep.go.cr/estadisticas", "https://mep.go.cr/analisis-estadistico", "https://datosabiertos.mep.go.cr/",
          "https://www.mep.go.cr/datos-abiertos"]:
    get("cr_" + re.sub(r"\W+", "_", u.split("//")[1])[:60] + ".html", u)
# Uruguay
for u in ["https://www.gub.uy/instituto-nacional-estadistica/comunicacion/noticias/linea-pobreza-indigencia-2024",
          "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/31-educacion-investigacion-2",
          "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/31-educacion-investigacion-5",
          "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/31-educacion-investigacion-9",
          "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/22-proyecciones-estimaciones-2",
          "https://www.gub.uy/ministerio-educacion-cultura/datos-y-estadisticas/datos/anuario-estadistico-educacion-2022",
          "https://www.gub.uy/ministerio-educacion-cultura/datos-y-estadisticas/datos",
          "https://www.gub.uy/instituto-nacional-estadistica/datos-y-estadisticas/estadisticas/pobreza"]:
    get("uy_" + re.sub(r"\W+", "_", u.split("gub.uy/")[1])[-60:] + ".html", u)
get("uy_book_4150.bin", "https://www.gub.uy/instituto-nacional-estadistica/book/4150/download")
json.dump(links, open(f"{OUT}/links.json", "w"), ensure_ascii=False, indent=1)
for fn in os.listdir(OUT):
    if os.path.getsize(f"{OUT}/{fn}") > 90e6: os.remove(f"{OUT}/{fn}")
