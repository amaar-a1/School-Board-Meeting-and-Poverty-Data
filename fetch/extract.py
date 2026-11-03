# Temporary: find sources for Puerto Rico legislative education hearings and Canadian school board data.
import json, subprocess, sys, urllib.parse, urllib.request
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"], check=True)
out = {}
def ytlist(key, target):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--dump-json", "--ignore-errors", target], capture_output=True, text=True, timeout=900)
    items = []
    for line in r.stdout.splitlines():
        try:
            d = json.loads(line); items.append({k: d.get(k) for k in ("title", "id", "channel", "channel_id", "duration")})
        except ValueError:
            pass
    out[key] = {"target": target, "count": len(items), "items": items, "stderr": r.stderr[-800:]}
ytlist("pr_search_senado", "ytsearch40:Senado de Puerto Rico Comisión de Educación vista pública")
ytlist("pr_search_camara", "ytsearch40:Cámara de Representantes Puerto Rico Comisión de Educación vista pública")
def get(key, url, limit=600000):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research script)"}), timeout=120) as r:
            out[key] = r.read(limit).decode("utf-8", "replace")
    except Exception as e:
        out[key] = f"ERROR {e}"
q = lambda s: urllib.parse.quote(s)
for term in ["school district boundaries", "school division boundaries", "school board boundaries", "centres de services scolaires territoires", "school jurisdiction boundaries", "education district boundaries"]:
    get(f"opencanada_{term}", f"https://open.canada.ca/data/api/3/action/package_search?q={q(term)}&rows=25")
get("bc_catalog", f"https://catalogue.data.gov.bc.ca/api/3/action/package_search?q={q('school districts')}&rows=15")
get("ab_catalog", f"https://open.alberta.ca/api/3/action/package_search?q={q('school jurisdiction boundaries')}&rows=15")
get("on_catalog", f"https://data.ontario.ca/api/3/action/package_search?q={q('school board boundaries')}&rows=15")
get("on_geohub", f"https://geohub.lio.gov.on.ca/api/v3/datasets?q={q('school board')}")
get("qc_catalog", f"https://www.donneesquebec.ca/recherche/api/3/action/package_search?q={q('centres de services scolaires')}&rows=15")
get("statcan_dl_page", "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?Lang=E")
get("statcan_bnd_page", "https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21")
json.dump(out, open("fetch/out/discover.json", "w"), indent=1)
