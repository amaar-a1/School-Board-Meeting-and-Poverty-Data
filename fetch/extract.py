# Round 8: data files for Slovenia, Taiwan, Costa Rica, Uruguay.
import os, re, urllib.request, urllib.parse, json, time, html
OUT = "fetch/out/new4b"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
links = {}
def get(name, url, data=None, timeout=300, hdr=None):
    try:
        req = urllib.request.Request(url, headers={**UA, **(hdr or {})}, data=data)
        b = urllib.request.urlopen(req, timeout=timeout).read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"== {name} OK {len(b)} {url}\n"); log.flush()
        if name.endswith(".html"):
            t = b.decode("utf-8", "replace")
            links[name] = [[urllib.parse.urljoin(url, html.unescape(m.group(1))), re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()[:150]]
                           for m in re.finditer(r'href="([^"]+)"[^>]*>(.*?)</a>', t, re.S)
                           if re.search(r"\.(xlsx?|csv|ods|zip|pdf|json)(\?|$)|download|descarg|/book/|base|datos", m.group(1) + m.group(2), re.I)]
        return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n"); log.flush()
    finally: time.sleep(2)
# Slovenia: SiStat tables (metadata, then every value of every variable but only the latest two periods)
PX = "https://pxweb.stat.si/SiStatData/api/v1/en/Data/"
for t in ["2640010S", "05C4006S", "05C4004S", "0952780S"]:
    m = get(f"si_{t}_meta.json", PX + t + ".px")
    if not m: continue
    meta = json.loads(m); q = []
    for v in meta["variables"]:
        vals = v["values"]
        if v.get("time") or re.search(r"year|half|leto|time", v["code"] + v["text"], re.I): vals = vals[-2:]
        q.append({"code": v["code"], "selection": {"filter": "item", "values": vals}})
    get(f"si_{t}.json", PX + t + ".px", data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode(), hdr={"Content-Type": "application/json"})
# Taiwan
for n, u in [("tw_lowincome_111.xlsx", "https://www.mohw.gov.tw/dl-27850-056a753c-fbce-4fff-a373-530accaf6572.html"),
             ("tw_lowincome_age_113.xlsx", "https://www.mohw.gov.tw/dl-22056-31689a70-b490-4f7e-8823-77bee9b4adf2.html"),
             ("tw_midlow_115.xlsx", "https://www.mohw.gov.tw/dl-22058-0e1cd81e-d145-45ef-8ee8-43fbb074c2b8.html"),
             ("tw_weakchildren_211.xlsx", "https://www.mohw.gov.tw/dl-97097-0d915486-88d0-47dd-9b44-f5bf8902ec25.html")]:
    get(n, u)
for a in range(1, 4):
    for b in range(1, 13):
        get(f"tw_edu_B_{a}_{b}.csv", f"https://stats.moe.gov.tw/files/opendata/edu_B_{a}_{b}.csv")
d = get("tw_ds_8411.json", "https://data.gov.tw/api/v2/rest/dataset/8411")
if d:
    dist = [x for x in json.loads(d)["result"]["distribution"] if "單一年齡" in (x.get("resourceDescription") or "")]
    dist.sort(key=lambda x: re.findall(r"\d{5}", x["resourceDescription"])[-1] if re.findall(r"\d{5}", x["resourceDescription"]) else "")
    if dist: get("tw_village_age_latest.csv", dist[-1]["resourceDownloadUrl"]); log.write("== latest " + dist[-1]["resourceDescription"] + "\n")
# Costa Rica: UNDP cantonal atlas pages
for u in ["https://www.undp.org/es/costa-rica/atlas-de-desarrollo-humano-cantonal-costa-rica-2026", "https://www.undp.org/es/costa-rica/atlas-de-desarrollo-humano-cantonal",
          "https://www.undp.org/es/node/550741", "https://www.undp.org/es/node/554351", "https://www.undp.org/es/node/597761", "https://www.undp.org/es/node/597571"]:
    get("cr_" + re.sub(r"\W+", "_", u.split("undp.org/")[1])[-50:] + ".html", u)
# Uruguay
B = "https://www5.ine.gub.uy/documents/ANUARIOS/Anuario%202025/"
for n, p in [("uy_3.1.3.xls", "3%20-%20ASPECTOS%20SOCIALES/3.1%20Educación%20e%20Invest.%20Cient.%20y%20Tecn/3.1.3ok.xls"),
             ("uy_3.1.6.xls", "3%20-%20ASPECTOS%20SOCIALES/3.1%20Educación%20e%20Invest.%20Cient.%20y%20Tecn/3.1.6ok.xls"),
             ("uy_3.1.10.xls", "3%20-%20ASPECTOS%20SOCIALES/3.1%20Educación%20e%20Invest.%20Cient.%20y%20Tecn/3.1.10ok.xls"),
             ("uy_2.2.4.xls", "2%20-%20POBLACIÓN/2.2%20Proyecciones/2.2.4.xls")]:
    get(n, B + urllib.parse.quote(urllib.parse.unquote(p)))
for u in ["https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/39-desarrollo-social",
          "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/capitulo-3-aspectos-sociales",
          "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/capitulo-3-aspectos-sociales-2",
          "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/31-educacion-investigacion-3",
          "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/anuario-estadistico-nacional-2025-vol-102/31-educacion-investigacion-8"]:
    get("uy_" + u.rstrip("/").split("/")[-1] + ".html", u)
json.dump(links, open(f"{OUT}/links.json", "w"), ensure_ascii=False, indent=1)
for fn in os.listdir(OUT):
    if os.path.getsize(f"{OUT}/{fn}") > 90e6: os.remove(f"{OUT}/{fn}")
