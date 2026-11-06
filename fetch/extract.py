# Temporary: Brazil census 2022, children 6-17 by municipality, and which census tables cover school attendance.
import json, os, time, urllib.request
OUT = "fetch/out/g7w"; os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"
log = open(f"{OUT}/log.txt", "w")
def get(path, t=900):
    with urllib.request.urlopen(urllib.request.Request("https://apisidra.ibge.gov.br/values/" + path, headers={"User-Agent": UA}), timeout=t) as f: return f.read()
ages = ",".join(str(c) for c in range(6563, 6575))
try:
    b = get(f"t/9514/n6/all/v/93/p/all/c2/6794/c287/{ages}/c286/113635"); open(f"{OUT}/age_6_17.json", "wb").write(b); log.write(f"ages {len(b)}\n")
except Exception as e: log.write(f"ages ERR {e}\n")
for t in list(range(9600, 9620)) + list(range(10050, 10135)) + list(range(10280, 10300)):
    try:
        d = json.loads(get(f"t/{t}/n1/all/v/all/p/all", 120))
        log.write(f"{t} | " + " ; ".join(sorted({x.get('D2N', '') for x in d[1:]}))[:400] + " | dims " + " ".join(v for k, v in d[0].items() if k.endswith("N") and k.startswith("D")) + "\n")
    except Exception as e: log.write(f"{t} ERR {str(e)[:80]}\n")
    log.flush(); time.sleep(0.5)
log.close()
