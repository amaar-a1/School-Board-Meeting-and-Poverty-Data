# Temporary: metadata (classification ids) for census tables 10058, 10295, 10296, 9514; children 6-17 by municipality.
import json, os, time, urllib.request
OUT = "fetch/out/g8w"; os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"
log = open(f"{OUT}/log.txt", "w")
def get(url, t=600):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=t) as f: return f.read()
for t in (10058, 10295, 10296, 9514):
    for attempt in range(3):
        try:
            m = json.loads(get(f"https://servicodados.ibge.gov.br/api/v3/agregados/{t}/metadados", 300))
            json.dump(m, open(f"{OUT}/meta_{t}.json", "w"), ensure_ascii=False)
            log.write(f"{t} {m.get('nome')} | levels {m.get('nivelTerritorial')} | vars " + "; ".join(f"{v['id']}:{v['nome']}" for v in m.get("variaveis", [])) +
                      " | cls " + "; ".join(f"c{c['id']}:{c['nome']}[" + ", ".join(f"{x['id']}:{x['nome']}" for x in c.get("categorias", [])[:40]) + "]" for c in m.get("classificacoes", [])) + "\n")
            break
        except Exception as e:
            log.write(f"{t} ERR {e}\n"); time.sleep(20)
    log.flush()
for name, path in [("age_6_17", "t/9514/n6/all/v/93/p/all/c2/6794/c287/" + ",".join(str(c) for c in range(6563, 6575)))]:
    try:
        b = get("https://apisidra.ibge.gov.br/values/" + path, 900); open(f"{OUT}/{name}.json", "wb").write(b); log.write(f"{name} {len(b)}\n")
    except Exception as e: log.write(f"{name} ERR {e}\n")
log.close()
