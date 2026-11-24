# Round 39: Czechia (MPSV unemployment by municipality, schools; GISCO LAU and NUTS3; Eurostat ages by NUTS3); Rwanda EICV7.
import os, re, json, gzip, urllib.request, urllib.parse, time, http.cookiejar, html
OUT = "fetch/out/c39"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(name, url, keep=True, limit=150e6, timeout=600):
    try:
        b = op.open(urllib.request.Request(urllib.parse.quote(url, safe=":/?=&%#"), headers=UA), timeout=timeout).read()
        if keep and len(b) < limit: open(f"{OUT}/{name}", "wb").write(b)
        log.write(f"OK {name} {len(b)} {url}\n   {b[:160]!r}\n"); return b
    except Exception as e: log.write(f"ERR {name} {e} {url}\n")
    finally: log.flush(); time.sleep(2)
M = "https://data.mpsv.cz/od/soubory/"
get("cz_unemp_12_2024.json.gz", M + "nezamestnanost-v-obcich/nezamestnanost-v-obcich-12-2024.json.gz")
get("cz_skoly.schema.json", M + "skoly/skoly.schema.json")
b = get("cz_skoly.json.gz", M + "skoly/skoly.json.gz", keep=False)
if b: open(f"{OUT}/cz_skoly_head.txt", "w").write(gzip.decompress(b)[:4000].decode("utf-8", "ignore"))
# GISCO: LAU 2024 (all of Europe) filtered to Czechia; NUTS 3 2024
b = get("lau_all.geojson", "https://gisco-services.ec.europa.eu/distribution/v2/lau/geojson/LAU_RG_01M_2024_4326.geojson", keep=False, timeout=1200)
if b:
    d = json.loads(b); d["features"] = [f for f in d["features"] if f["properties"].get("CNTR_CODE") == "CZ"]
    json.dump(d, open(f"{OUT}/lau_CZ.geojson", "w")); log.write(f"LAU CZ {len(d['features'])}\n")
b = get("nuts.geojson", "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2024_4326_LEVL_3.geojson", keep=False, timeout=600)
if b:
    d = json.loads(b); d["features"] = [f for f in d["features"] if f["properties"].get("CNTR_CODE") == "CZ"]
    json.dump(d, open(f"{OUT}/nuts3_CZ.geojson", "w")); log.write(f"NUTS3 CZ {len(d['features'])}\n")
get("cz_ages_nuts3.json", "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_r_pjangrp3?format=JSON&lang=EN&sex=T&unit=NR&time=2024&geo=CZ010&geo=CZ020&geo=CZ031&geo=CZ032&geo=CZ041&geo=CZ042&geo=CZ051&geo=CZ052&geo=CZ053&geo=CZ063&geo=CZ064&geo=CZ071&geo=CZ072&geo=CZ080&age=Y5-9&age=Y10-14&age=Y15-19&age=TOTAL")
# Rwanda: surveys pages, to find EICV7
R = "https://statistics.gov.rw"
for n, p in [("rw_surveys.html", "/surveys"), ("rw_ds.html", "/data-sources/surveys"), ("rw_eicv.html", "/data-sources/surveys/EICV"),
             ("rw_eicv7.html", "/data-sources/surveys/EICV/eicv7"), ("rw_pubsearch.html", "/statistical-publications?search=EICV7")]:
    b = get(n, R + p)
    s = (b or b"").decode("utf-8", "ignore")
    for u, t in re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>', s, re.S):
        t = re.sub(r"<[^>]+>|\s+", " ", html.unescape(t)).strip()
        if re.search(r"eicv|poverty|living conditions", u + " " + t, re.I): log.write(f"  {n} LINK {t[:90]} | {u[:180]}\n")
log.close()
