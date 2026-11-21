# Round 10: Slovenia income/unemployment, Uruguay poverty report, meetings on YouTube for Slovenia, Uruguay, Costa Rica, Taiwan.
import os, re, urllib.request, urllib.parse, json, time, html, subprocess, sys
OUT = "fetch/out/new4d"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
links = {}
def get(name, url, data=None, timeout=300, hdr=None):
    try:
        b = urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(hdr or {})}, data=data), timeout=timeout).read()
        open(f"{OUT}/{name}", "wb").write(b); log.write(f"== {name} OK {len(b)} {url}\n"); log.flush()
        if name.endswith(".html"):
            t = b.decode("utf-8", "replace")
            links[name] = [[urllib.parse.urljoin(url, html.unescape(m.group(1))), re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()[:160]] for m in re.finditer(r'href="([^"]+)"[^>]*>(.*?)</a>', t, re.S)]
        return b
    except Exception as e:
        log.write(f"== {name} ERR {e} {url}\n"); log.flush()
    finally: time.sleep(2)
PX = "https://pxweb.stat.si/SiStatData/api/v1/en/Data/"
for t in ["0883206S", "0883205S", "0700960S", "0775360S"]:
    m = get(f"si_{t}_meta.json", PX + t + ".px")
    if not m: continue
    meta = json.loads(m); q = []
    for v in meta["variables"]:
        vals = v["values"]
        if v.get("time") or re.search(r"year|month|leto|mesec|time", v["code"] + v["text"], re.I): vals = vals[-1:]
        q.append({"code": v["code"], "selection": {"filter": "item", "values": vals}})
    get(f"si_{t}.json", PX + t + ".px", data=json.dumps({"query": q, "response": {"format": "json-stat2"}}).encode(), hdr={"Content-Type": "application/json"})
get("si_px_atrisk.json", "https://pxweb.stat.si/SiStatData/api/v1/en/Data?query=" + urllib.parse.quote("at-risk-of-poverty rate statistical regions"))
G = "https://www.gub.uy/instituto-nacional-estadistica/comunicacion/publicaciones/"
for p in ["estimacion-pobreza-metodo-del-ingreso-ano-2025", "estimacion-pobreza-metodo-del-ingreso-primer-semestre-2026"]:
    get(f"uy_{p}.html", G + p)
n = 0
for k, v in list(links.items()):
    for u, t in v:
        if re.search(r"/book/\d+/download|\.pdf|\.xlsx?", u) and not re.search(r"facebook|twitter", u):
            n += 1; get(f"uy_pob_{n}" + (".xlsx" if ".xls" in u else ".pdf"), u); log.write(f"   ({t[:120]})\n")
# meetings
r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "yt-dlp"], capture_output=True, text=True)
env = {**os.environ, "NORDIC_DATA": "fetch/lists", "NORDIC_DEADLINE": str(time.time() + 4.5 * 3600)}
p1 = subprocess.Popen([sys.executable, "fetch/nyt.py", OUT, "SI:0/2", "SI:1/2", "UY", "CR:0/2", "CR:1/2"], env=env, stdout=open(f"{OUT}/nyt_log.txt", "w"), stderr=subprocess.STDOUT)
p2 = subprocess.Popen([sys.executable, "fetch/tw_yt.py", OUT], stdout=open(f"{OUT}/tw_log.txt", "w"), stderr=subprocess.STDOUT)
p1.wait(); p2.wait()
json.dump(links, open(f"{OUT}/links.json", "w"), ensure_ascii=False, indent=1)
for fn in os.listdir(OUT):
    if os.path.getsize(f"{OUT}/{fn}") > 90e6: os.remove(f"{OUT}/{fn}")
