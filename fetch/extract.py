# Temporary: DGEEC "Regiões em Números 2023/2024 - Educação" (a JavaScript site), via Node Playwright; then download
# the files it links to.
import json, os, re, subprocess, time, traceback, urllib.request
OUT = "fetch/out/pt_dgeec4"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
def sh(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True); log.write(f"$ {c}\n{r.stdout[-800:]}\n{r.stderr[-800:]}\n"); log.flush(); return r
try:
    sh("cd fetch/pt && npm init -y >/dev/null && npm install playwright@1.48.2 >/dev/null 2>&1 && npx playwright install --with-deps chromium >/dev/null 2>&1; echo installed")
    sh(f"cd fetch/pt && node dgeec.js ../../{OUT}")
    d = json.load(open(f"{OUT}/browse.json")) if os.path.exists(f"{OUT}/browse.json") else {}
    log.write(f"url {d.get('url')} title {d.get('title')}\n")
    files = [l for l in d.get("links", []) if "ficheiros" in (l[0] or "")]
    log.write("file links: " + json.dumps(files[:40], ensure_ascii=False) + "\n")
    log.write("api calls: " + json.dumps(d.get("calls", [])[:40]) + "\n")
    for href, txt in files[:20]:
        try:
            with urllib.request.urlopen(urllib.request.Request(href, headers={"User-Agent": "Mozilla/5.0 (school-board research project)"}), timeout=300) as r:
                f = r.read(); cd = r.headers.get("Content-Disposition", "")
            name = (re.search(r'filename="?([^";]+)', cd) or [None, href.split("/")[-1]])[1]
            open(f"{OUT}/{re.sub(r'[^A-Za-z0-9_.-]', '_', name)[-90:]}", "wb").write(f); log.write(f"  downloaded {name} {len(f)} ({txt})\n")
        except Exception as e: log.write(f"  ERR {href} {str(e)[:80]}\n")
        time.sleep(1)
except Exception: log.write(traceback.format_exc()[-1200:])
log.close()
