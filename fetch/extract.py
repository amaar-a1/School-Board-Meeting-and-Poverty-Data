# Temporary: Iceland part 2: Statistics Iceland table lists, unemployment links.
import json, os, re, time, urllib.request
OUT = "fetch/out/is2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)", "Accept": "application/json, text/html, */*"}
log = []
def get(url, name=None):
    time.sleep(1.2)
    try:
        d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300).read()
        if name: open(f"{OUT}/{name}", "wb").write(d)
        log.append(f"ok {len(d)} {url[:200]}"); return d
    except Exception as e:
        log.append(f"FAIL {url[:200]}: {e}"); return None
HG = "https://px.hagstofa.is/pxis/api/v1/is/"
tree = {}
def walk(path, depth=0):
    d = get(HG + path)
    if not d or depth > 3: return
    for x in json.loads(d):
        p = f"{path}/{x['id']}"
        tree[p] = x["text"]
        if x["type"] == "l": walk(p, depth + 1)
for root in ("Samfelag/skolamal/2_grunnskolastig", "Ibuar/mannfjoldi/2_byggdir", "Samfelag/vinnumarkadur", "Samfelag/lifskjor", "Efnahagur/tekjur"):
    walk(root)
json.dump(tree, open(f"{OUT}/hg_tree.json", "w"), ensure_ascii=False, indent=0)
for u in ("https://vinnumalastofnun.is/", "https://vinnumalastofnun.is/tolfraedi", "https://www.vinnumalastofnun.is/um-okkur/tolfraedi/atvinnuleysistolur"):
    d = get(u, re.sub(r"\W+", "_", u)[-40:] + ".html")
open(f"{OUT}/log.txt", "w").write("\n".join(log))
