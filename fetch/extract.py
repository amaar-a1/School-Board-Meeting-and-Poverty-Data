# Temporary: Saint-Pierre-et-Miquelon (education statistics, outline, Territorial Council videos).
import json, os, subprocess, sys, time, urllib.request
OUT = "fetch/out/spm"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "school-board-research-script (github.com/amaar-a1)"}
log = []
def get(url, name):
    time.sleep(3)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
            data = r.read()
        open(f"{OUT}/{name}", "wb").write(data); log.append(f"ok {len(data)} {url}")
    except Exception as e:
        log.append(f"FAIL {url}: {e}")
get("https://www.education.gouv.fr/sites/default/files/2025-07/rers2025-chapitre-11-441744.pdf", "rers2025_ch11.pdf")
get("https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/SPM/ADM0/geoBoundaries-SPM-ADM0_simplified.geojson", "spm_adm0.geojson")
get("https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/SPM/ADM0/geoBoundaries-SPM-ADM0.geojson", "spm_adm0_full.geojson")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "yt-dlp"], check=True)
def ytdlp(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=600)
    if r.returncode:
        log.append("yt-dlp error: " + r.stderr[-300:]); return {}
    return json.loads(r.stdout)
found = {}
for q in ["Conseil territorial Saint-Pierre-et-Miquelon séance plénière", "Collectivité territoriale Saint-Pierre-et-Miquelon session conseil territorial", "SPM conseil territorial séance"]:
    for e in ytdlp(f"ytsearch20:{q}").get("entries") or []:
        found.setdefault(e.get("channel_url"), {"channel": e.get("channel"), "titles": []})["titles"].append(e.get("title"))
    time.sleep(2)
json.dump(found, open(f"{OUT}/yt_search.json", "w"), indent=1, ensure_ascii=False)
for url, v in found.items():
    if url and v["channel"] and any(k in v["channel"].lower() for k in ["collectivit", "territorial", "saint-pierre", "spm"]):
        vids = []
        for tab in ("/videos", "/streams"):
            vids += [{"title": x.get("title"), "id": x.get("id")} for x in (ytdlp(url + tab).get("entries") or [])]
            time.sleep(2)
        json.dump({"channel": v["channel"], "url": url, "videos": vids}, open(f"{OUT}/yt_channel_{len(os.listdir(OUT))}.json", "w"), indent=1, ensure_ascii=False)
open(f"{OUT}/log.txt", "w").write("\n".join(log))
