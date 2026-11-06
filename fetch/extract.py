# Temporary: Brazil census 2022 by municipality: attending school 6-17 (10058), children 6-17 (9514), and the code of
# the per-capita income class classification in 10296 (found by trying ids at national level).
import json, os, time, urllib.request, urllib.error, concurrent.futures as cf
OUT = "fetch/out/g9w"; os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"
log = open(f"{OUT}/log.txt", "w")
def get(path, t=900):
    with urllib.request.urlopen(urllib.request.Request("https://apisidra.ibge.gov.br/values/" + path, headers={"User-Agent": UA}), timeout=t) as f: return f.read()
def save(name, path):
    try: b = get(path); open(f"{OUT}/{name}.json", "wb").write(b); log.write(f"{name} {len(b)} {b[:400]!r}\n")
    except Exception as e: log.write(f"{name} ERR {e}\n")
    log.flush()
save("attending_6_17", "t/10058/n6/all/v/all/p/all")
save("age_6_11", "t/9514/n6/all/v/93/p/all/c2/6794/c287/" + ",".join(str(c) for c in range(6563, 6569)))
save("age_12_17", "t/9514/n6/all/v/93/p/all/c2/6794/c287/" + ",".join(str(c) for c in range(6569, 6575)))
def probe(c):
    try: return c, get(f"t/10296/n1/all/v/all/p/all/c{c}/all", 60)
    except urllib.error.HTTPError as e: return c, None
    except Exception as e: return c, None
found = None
with cf.ThreadPoolExecutor(6) as ex:
    for c, b in ex.map(probe, range(1, 2600)):
        if b and not found:
            found = c; open(f"{OUT}/income_classes_n1.json", "wb").write(b); log.write(f"10296 classification c{c}\n"); log.flush()
log.write(f"found {found}\n")
if found:
    d = json.loads(get(f"t/10296/n1/all/v/all/p/all/c{found}/all"))
    log.write(" ; ".join(sorted({f"{x.get('D2C')}:{x.get('D2N')}" for x in d[1:]})) + "\n")
    cats = sorted({x[k] for x in d[1:] for k in x if k.endswith("C") and k not in ("NC", "MC", "D1C", "D2C", "D3C")})
    log.write("cats " + str(cats) + "\n")
    save("income_classes_mun", f"t/10296/n6/all/v/all/p/all/c{found}/all")
log.close()
