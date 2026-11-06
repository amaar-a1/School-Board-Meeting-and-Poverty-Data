# Temporary: census table 10296 (residents by household income per capita class, c386) by municipality, one region at a time.
import json, os, urllib.request
OUT = "fetch/out/g11w"; os.makedirs(OUT, exist_ok=True)
UA = "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"
log = open(f"{OUT}/log.txt", "w")
def get(path, t=900):
    with urllib.request.urlopen(urllib.request.Request("https://apisidra.ibge.gov.br/values/" + path, headers={"User-Agent": UA}), timeout=t) as f: return f.read()
b = get("t/10296/n1/all/v/13604/p/all/c386/all"); open(f"{OUT}/income_n1.json", "wb").write(b)
log.write(" ; ".join(f"{x.get('D4C')}={x.get('D4N')}:{x['V']}" for x in json.loads(b)[1:]) + "\n")
for reg in range(1, 6):
    try:
        b = get(f"t/10296/n6/in%20n2%20{reg}/v/13604/p/all/c386/all"); open(f"{OUT}/income_region{reg}.json", "wb").write(b); log.write(f"region {reg} {len(b)}\n")
    except Exception as e: log.write(f"region {reg} ERR {e}\n")
    log.flush()
log.close()
