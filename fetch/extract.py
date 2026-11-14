# Temporary: Sweden, Kolada N15831 (pupils F-9 in an independent school in the municipality or a school in another
# municipality, home municipality, share %), 2025 and 2024, every municipality.
import json, os, urllib.request
OUT = "fetch/out/se_pub1"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
for y in (2025, 2024):
    try:
        u = f"https://api.kolada.se/v3/data/kpi/N15831/year/{y}"; vals = []
        while u:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read())
            vals += d.get("values", []); u = d.get("next_url") or d.get("next_page")
        json.dump({"kpi": "N15831", "year": y, "values": vals}, open(f"{OUT}/se_N15831_{y}.json", "w")); log.write(f"{y}: {len(vals)} sample {vals[:2]}\n")
        if len(vals) > 250: break
    except Exception as e: log.write(f"ERR {y} {e}\n")
try:
    d = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.kolada.se/v3/kpi/N15831", headers=UA), timeout=60).read())
    log.write("KPI " + json.dumps(d, ensure_ascii=False)[:1500] + "\n")
except Exception as e: log.write(f"ERR kpi {e}\n")
log.close()
