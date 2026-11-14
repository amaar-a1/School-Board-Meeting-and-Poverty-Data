# Temporary: public/private pupils by municipality: Statistics Iceland (compulsory-school tables) and Statistics
# Finland (comprehensive-school tables): list tables and their variables.
import json, os, urllib.request
OUT = "fetch/out/isfi1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=60):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r: return json.loads(r.read())
def walk(base, path, depth, tag):
    try: items = get(base + path)
    except Exception as e: log.write(f"ERR {tag} {path} {e}\n"); return
    for it in items:
        p = path + it["id"] + ("/" if it["type"] == "l" else "")
        if it["type"] == "l" and depth < 3: walk(base, p, depth + 1, tag)
        elif it["type"] == "t":
            try:
                m = get(base + p)
                vars_ = [(v["code"], v["text"], v["valueTexts"][:6], len(v["values"])) for v in m["variables"]]
                log.write(f"{tag} {p} | {it['text'][:110]}\n   {json.dumps(vars_, ensure_ascii=False)[:700]}\n")
            except Exception as e: log.write(f"ERR {tag} {p} {e}\n")
walk("https://px.hagstofa.is/pxis/api/v1/is/", "Samfelag/skolamal/2_grunnskolastig/", 0, "IS")
walk("https://pxdata.stat.fi/PxWeb/api/v1/fi/", "StatFin/pop/", 0, "FI")
log.close()
