# Temporary: Pitcairn's school: is it open, and how many pupils? Wikipedia, the government's sites, news.
import os, re, html, json, urllib.request, urllib.parse
OUT = "fetch/out/pcn1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=60):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return r.read().decode("utf-8", "replace")
for u in ["https://en.wikipedia.org/w/index.php?title=Pitcairn_Islands&action=raw", "https://en.wikipedia.org/w/index.php?title=Adamstown,_Pitcairn_Islands&action=raw",
          "https://en.wikipedia.org/w/index.php?title=Education_in_the_Pitcairn_Islands&action=raw",
          "https://www.government.pn", "https://www.government.pn/departments", "https://www.immigration.gov.pn", "https://www.visitpitcairn.pn"]:
    try:
        t = get(u); txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
        hits = [m.group(0) for m in re.finditer(r".{0,200}\b(Pulawana|school|pupils?|students?|teacher)\b.{0,220}", txt, re.I)][:8]
        log.write(f"OK {u}\n  " + "\n  ".join(hits) + "\n")
    except Exception as e: log.write(f"ERR {u} {str(e)[:100]}\n")
try:
    q = urllib.parse.quote('Pitcairn school "no children" OR "no students" OR "pupils" teacher')
    d = json.loads(get("https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srlimit=10&srsearch=" + urllib.parse.quote("Pulawana School Pitcairn")))
    log.write("WIKI search " + json.dumps([(x["title"], re.sub("<[^>]+>", "", x["snippet"])) for x in d["query"]["search"]])[:2000] + "\n")
except Exception as e: log.write(f"ERR search {e}\n")
log.close()
