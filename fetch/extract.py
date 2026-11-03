# Temporary: Puerto Rico legislature channel listings, and remaining Canadian source discovery.
import json, re, subprocess, sys, urllib.parse, urllib.request
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp"], check=True)
out = {}
def ytlist(key, target):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--dump-json", "--ignore-errors", target], capture_output=True, text=True, timeout=1800)
    items = []
    for line in r.stdout.splitlines():
        try:
            d = json.loads(line); items.append({k: d.get(k) for k in ("title", "id", "duration", "upload_date")})
        except ValueError:
            pass
    out[key] = {"target": target, "count": len(items), "items": items, "stderr": r.stderr[-500:]}
for ch, cid in [("senado", "UCg90Gzk-QoCxYUNYmAUasWA"), ("camara", "UCm0SWjunIA5PDT9l4qW59Kw")]:
    for tab in ("videos", "streams"):
        ytlist(f"pr_{ch}_{tab}", f"https://www.youtube.com/channel/{cid}/{tab}")
def get(key, url, limit=300000):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research script)"}), timeout=120) as r:
            out[key] = r.read(limit).decode("utf-8", "replace")
    except Exception as e:
        out[key] = f"ERROR {e}"
q = urllib.parse.quote
def ckan(key, base, term, rows=10):
    get(key, f"{base}/api/3/action/package_search?q={q(term)}&rows={rows}", 2000000)
    try:
        res = json.loads(out[key])["result"]["results"]
        out[key] = [{"title": p.get("title"), "resources": [(r.get("format"), r.get("name"), r.get("url")) for r in p.get("resources", [])][:12]} for p in res]
    except Exception as e:
        out[key] = f"PARSE {e} {str(out[key])[:200]}"
ckan("on_service_area", "https://data.ontario.ca", "board service area")
ckan("on_regions", "https://data.ontario.ca", "district school board regions")
ckan("qc", "https://www.donneesquebec.ca/recherche", "centres de services scolaires")
ckan("qc2", "https://www.donneesquebec.ca/recherche", "commissions scolaires territoires")
ckan("bc_sd", "https://catalogue.data.gov.bc.ca", "School Districts of BC", 3)
ckan("bc_contacts", "https://catalogue.data.gov.bc.ca", "school district information", 3)
ckan("ab_auth", "https://open.alberta.ca", "Education - Authorities Public", 5)
ckan("ab_list", "https://open.alberta.ca", "Alberta schools and authorities", 3)
ckan("canada_sk", "https://open.canada.ca/data", "Saskatchewan school divisions", 10)
ckan("canada_nb", "https://open.canada.ca/data", "New Brunswick school districts", 10)
ckan("canada_ns", "https://open.canada.ca/data", "Nova Scotia regional centres for education", 10)
ckan("canada_mb", "https://open.canada.ca/data", "Manitoba School Divisions", 3)
get("statcan_dl_page", "https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?Lang=E")
get("statcan_bnd_page", "https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21")
for k in ("statcan_dl_page", "statcan_bnd_page"):
    v = out[k]
    out[k] = v[:200] if v.startswith("ERROR") else sorted(set(re.findall(r'href="([^"]+\.(?:zip|ZIP|csv|CSV)[^"]*)"', v)))
json.dump(out, open("fetch/out/discover2.json", "w"), indent=1)
