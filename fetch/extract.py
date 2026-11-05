# Temporary: check the free visitor-counter API the site would use.
import json, os, urllib.request
OUT = "fetch/out/cnt"; os.makedirs(OUT, exist_ok=True)
res = {}
for u in ("https://api.counterapi.dev/v1/sbmpd-test-check/visitors/up", "https://api.counterapi.dev/v1/sbmpd-test-check/visitors/"):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0", "Origin": "https://amaar-a1.github.io"}), timeout=60)
        res[u] = {"status": r.status, "body": r.read().decode()[:500], "cors": r.headers.get("Access-Control-Allow-Origin")}
    except Exception as e:
        res[u] = {"error": str(e)[:300]}
json.dump(res, open(f"{OUT}/check.json", "w"), indent=1)
