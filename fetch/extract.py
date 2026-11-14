# Temporary: (1) Statistics Iceland SKO02202, 2025: private schools and their pupils (national); (2) Statistics Finland
# comprehensive-school tables (StatFin/kjarj): variables, to find a provider (ylläpitäjä) breakdown by municipality.
import json, os, time, urllib.request
OUT = "fetch/out/isfi2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
def get(u, data=None, t=60):
    h = dict(UA)
    if data is not None: h["Content-Type"] = "application/json"
    with urllib.request.urlopen(urllib.request.Request(u, data=data, headers=h), timeout=t) as r: return r.read()
try:
    q = {"query": [{"code": "Ár", "selection": {"filter": "item", "values": ["2025"]}}], "response": {"format": "csv"}}
    log.write("IS SKO02202 " + get("https://px.hagstofa.is/pxis/api/v1/is/Samfelag/skolamal/2_grunnskolastig/2_gsSkolahald/SKO02202.px", json.dumps(q).encode()).decode("utf-8-sig") + "\n")
except Exception as e: log.write(f"ERR IS {e}\n")
time.sleep(3)
try:
    items = json.loads(get("https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/"))
    log.write("FI dbs " + json.dumps([(i["id"], i["text"]) for i in items if any(k in i["text"].lower() for k in ("koulu", "oppil", "opetu", "koulutu"))], ensure_ascii=False) + "\n")
    for db in [i["id"] for i in items if any(k in i["text"].lower() for k in ("peruskoul", "oppilaitos", "koulutuksen järj", "esi- ja perusop"))][:3]:
        time.sleep(2)
        for t in json.loads(get(f"https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/{db}/")):
            time.sleep(1)
            try:
                m = json.loads(get(f"https://pxdata.stat.fi/PxWeb/api/v1/fi/StatFin/{db}/{t['id']}"))
                log.write(f"FI {db}/{t['id']} | {t['text'][:100]}\n   {json.dumps([(v['code'], v['text'], v['valueTexts'][:5], len(v['values'])) for v in m['variables']], ensure_ascii=False)[:600]}\n")
            except Exception as e: log.write(f"ERR FI {t['id']} {e}\n")
except Exception as e: log.write(f"ERR FI {e}\n")
log.close()
