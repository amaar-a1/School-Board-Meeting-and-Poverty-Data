# Temporary: DGEEC "Regiões em Números 2023/2024 - Educação" (a JavaScript site): open it in a headless browser, record
# its API calls and file links, and download the spreadsheets.
import json, os, re, subprocess, sys, time, traceback, urllib.request
OUT = "fetch/out/pt_dgeec3"; os.makedirs(OUT, exist_ok=True)
log = open(f"{OUT}/log.txt", "w")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True, capture_output=True)
from playwright.sync_api import sync_playwright
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
try:
    calls = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.on("response", lambda r: calls.append((r.url, r.status, r.headers.get("content-type", ""))))
        pg.goto("https://www.dgeec.medu.pt/l/Z9on6", wait_until="networkidle", timeout=120000); time.sleep(5)
        log.write(f"url {pg.url}\ntitle {pg.title()}\n")
        text = pg.inner_text("body"); open(f"{OUT}/page.txt", "w").write(text)
        links = pg.eval_on_selector_all("a", "els => els.map(e => [e.href, e.innerText.trim().slice(0, 100)])")
        log.write("links: " + json.dumps([l for l in links if l[0] and ("ficheiro" in l[0] or "xls" in l[0].lower() or "Regi" in l[1] or "munic" in l[1].lower())][:60], ensure_ascii=False) + "\n")
        log.write("api calls: " + json.dumps([c for c in calls if "/api/" in c[0]][:60]) + "\n")
        b.close()
    for href, txt in [l for l in links if "api/ficheiros" in (l[0] or "")][:15]:
        try:
            with urllib.request.urlopen(urllib.request.Request(href, headers=UA), timeout=300) as r:
                f = r.read(); cd = r.headers.get("Content-Disposition", "")
            name = (re.search(r'filename="?([^";]+)', cd) or [None, href.split("/")[-1]])[1]
            open(f"{OUT}/{re.sub(r'[^A-Za-z0-9_.-]', '_', name)[-90:]}", "wb").write(f)
            log.write(f"  downloaded {name} {len(f)} ({txt})\n")
        except Exception as e: log.write(f"  ERR {href} {str(e)[:80]}\n")
except Exception: log.write(traceback.format_exc()[-1200:])
log.close()
