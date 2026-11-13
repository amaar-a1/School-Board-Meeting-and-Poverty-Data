# Temporary: SEP "principales cifras" form (planeacion.sep.gob.mx): can it be reached, and what are its form fields?
import json, os, subprocess, sys
OUT = "fetch/out/mx_sep1"; os.makedirs(OUT, exist_ok=True)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
log = open(f"{OUT}/log.txt", "w")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(user_agent="Mozilla/5.0 (school-board research project; github.com/amaar-a1)")
    reqs = []
    pg.on("request", lambda r: reqs.append(f"{r.method} {r.url} {(r.post_data or '')[:300]}") if r.resource_type in ("xhr", "fetch", "document") else None)
    for u in ["https://www.planeacion.sep.gob.mx/principalescifras/", "https://planeacion.sep.gob.mx/principalescifras/"]:
        try:
            r = pg.goto(u, wait_until="networkidle", timeout=90000); log.write(f"{u} -> {r.status if r else None} {pg.url}\n")
            pg.wait_for_timeout(3000)
            sels = pg.eval_on_selector_all("select", "ss => ss.map(s => ({id: s.id, name: s.name, opts: [...s.options].slice(0,40).map(o => o.value + '=' + o.text)}))")
            log.write("SELECTS " + json.dumps(sels, ensure_ascii=False)[:6000] + "\n")
            log.write("BUTTONS " + json.dumps(pg.eval_on_selector_all("button, input[type=submit], input[type=button], a.btn", "bs => bs.map(b => (b.id || '') + ':' + (b.innerText || b.value || '').trim().slice(0,40))"), ensure_ascii=False)[:2000] + "\n")
            break
        except Exception as e: log.write(f"{u} ERR {str(e)[:200]}\n")
    log.write("REQS\n" + "\n".join(reqs[:40]) + "\n")
    b.close()
log.close()
