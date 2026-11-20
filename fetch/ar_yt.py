"""Argentina: YouTube search results for each province's education council and its legislature's education committee.
Writes OUT/ar_yt.json: {province: {query: [{title, channel, channel_url, url, upload_date}]}} and the full video lists
of every channel whose name looks like an education council, ministry or legislature."""
import json, os, re, subprocess, sys, time
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
PROV = ["Buenos Aires", "Ciudad de Buenos Aires", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy",
        "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe",
        "Santiago del Estero", "Tierra del Fuego", "Tucumán"]
def yt(*a):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "-J", "--no-warnings", *a], capture_output=True, text=True, timeout=600)
    if r.returncode: raise RuntimeError(r.stderr.strip()[-300:])
    return json.loads(r.stdout)
res, chans = {}, {}
for p in PROV:
    leg = "Legislatura porteña" if p.startswith("Ciudad") else f"Legislatura {p}" if p not in ("Buenos Aires",) else "Cámara de Diputados Buenos Aires"
    qs = [f"Consejo General de Educación {p} sesión", f"Consejo Provincial de Educación {p} sesión", f"{p} consejo de educación reunión vocales",
          f"{leg} comisión de educación reunión"]
    res[p] = {}
    for q in qs:
        try:
            es = yt(f"ytsearch20:{q}").get("entries") or []
            res[p][q] = [{k: e.get(k) for k in ("title", "channel", "channel_url", "url", "upload_date", "duration")} for e in es]
            for e in es:
                c = e.get("channel") or ""
                if e.get("channel_url") and re.search(r"consejo|educaci|legislatura|diputados|senado|c[aá]mara|cge|cpe|dge|escuelas|ministerio", c, re.I):
                    chans[e["channel_url"]] = c
        except Exception as e:
            res[p][q] = [{"error": str(e)[:300]}]
            if "Sign in" in str(e): break
        time.sleep(2)
    json.dump(res, open(f"{OUT}/ar_yt.json", "w"), ensure_ascii=False)
lists = {}
for u, c in chans.items():
    vids = []
    for tab in ("/videos", "/streams"):
        try: vids += [{k: v.get(k) for k in ("title", "url", "upload_date", "duration")} for v in yt(u + tab).get("entries") or []]
        except Exception as e: vids.append({"error": str(e)[:200]})
        time.sleep(1)
    lists[u] = {"channel": c, "videos": vids}
    json.dump(lists, open(f"{OUT}/ar_yt_channels.json", "w"), ensure_ascii=False)
