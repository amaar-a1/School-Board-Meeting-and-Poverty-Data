# Temporary: open the data.gov.ph DepEd dataset page in a headless browser; record API calls and download links.
import json, os, subprocess, sys
OUT = "fetch/out/ph_deped4"; os.makedirs(OUT, exist_ok=True)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
log = open(f"{OUT}/log.txt", "w")
page_url = "https://data.gov.ph/index/public/dataset/Historical%20Enrollment%20Data/l6xdlzdg-ixdr-yuve-tw7k-0cgug0ceul10"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(user_agent="Mozilla/5.0 (school-board research project; github.com/amaar-a1)")
    seen = []
    def on_resp(r):
        ct = r.headers.get("content-type", "")
        if "json" in ct or r.request.resource_type in ("xhr", "fetch"):
            try: body = r.text()[:3000]
            except Exception: body = ""
            seen.append({"url": r.url, "status": r.status, "ct": ct, "body": body})
    pg.on("response", on_resp)
    pg.goto(page_url, wait_until="networkidle", timeout=120000); pg.wait_for_timeout(5000)
    log.write("TEXT " + pg.inner_text("body")[:4000] + "\n")
    links = pg.eval_on_selector_all("a", "as => as.map(a => [a.innerText.trim().slice(0,80), a.href])")
    log.write("LINKS " + json.dumps([l for l in links if l[1] and "data.gov.ph" not in l[1] or any(k in (l[0] + l[1]).lower() for k in ("download", "csv", "xls", "resource", "file"))], ensure_ascii=False)[:4000] + "\n")
    btns = pg.locator("text=DOWNLOAD").all()
    log.write(f"buttons {len(btns)}\n")
    for i, bt in enumerate(btns[:3]):
        try:
            with pg.expect_download(timeout=120000) as d: bt.click()
            dl = d.value; fn = f"{OUT}/{i}_{dl.suggested_filename}"; dl.save_as(fn); log.write(f"saved {fn} {os.path.getsize(fn)}\n")
        except Exception as e: log.write(f"dl {i} ERR {str(e)[:200]}\n")
        pg.wait_for_timeout(1500)
    for s in seen: log.write(f"XHR {s['status']} {s['url']}\n  {s['body'][:1500]}\n")
    b.close()
log.close()

# v4
