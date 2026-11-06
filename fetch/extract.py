# Temporary: the income class classification of census table 10296 (any id that works, other than sex c2 and race c86),
# then its values by municipality.
import json, os, urllib.request, urllib.error, concurrent.futures as cf
OUT = "fetch/out/g10w"; os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"
log = open(f"{OUT}/log.txt", "w")
def get(path, t=900):
    with urllib.request.urlopen(urllib.request.Request("https://apisidra.ibge.gov.br/values/" + path, headers={"User-Agent": UA}), timeout=t) as f: return f.read()
def probe(c):
    try: return c, get(f"t/10296/n1/all/v/13604/p/all/c{c}/all", 60)
    except Exception: return c, None
ok = []
with cf.ThreadPoolExecutor(6) as ex:
    for c, b in ex.map(probe, [c for c in range(1, 3000) if c not in (2, 86)]):
        if b:
            ok.append(c); d = json.loads(b)
            log.write(f"c{c}: " + " ; ".join(f"{x.get('D6C') or x.get('D5C') or x.get('D4C')}={x.get('D6N') or x.get('D5N') or x.get('D4N')}:{x['V']}" for x in d[1:])[:1500] + "\n"); log.flush()
log.write(f"ok {ok}\n")
for c in ok:
    if c in (2, 86): continue
    try:
        b = get(f"t/10296/n6/all/v/13604/p/all/c{c}/all"); open(f"{OUT}/income_c{c}.json", "wb").write(b); log.write(f"saved c{c} {len(b)}\n")
    except Exception as e: log.write(f"c{c} mun ERR {e}\n")
    break
log.close()
