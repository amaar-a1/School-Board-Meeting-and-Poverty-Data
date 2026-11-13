# Temporary: SEP principales cifras (Formato 911), 2025-2026, escolarizada, educación básica: pupils by municipality for
# each state, all schools and public schools. One query at a time, with pauses.
import json, os, subprocess, sys, time
OUT = "fetch/out/mx_sep3"; os.makedirs(OUT, exist_ok=True)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--user", "--break-system-packages", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True)
    os.execv(sys.executable, [sys.executable] + sys.argv)
log = open(f"{OUT}/log.txt", "w")
URL = "https://www.planeacion.sep.gob.mx/principalescifras/"
def opts(pg, sel): return pg.eval_on_selector(sel, "s => [...s.options].map(o => [o.value, o.text.trim()])")
def choose(pg, sel, value):
    pg.select_option(sel, value); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(800)
res = {}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(user_agent="Mozilla/5.0 (school-board research project; github.com/amaar-a1)")
    pg.goto(URL, wait_until="networkidle", timeout=90000)
    choose(pg, "#DDLciclos", "29"); choose(pg, "#DDLEscolarizadas", "1")
    tipos = opts(pg, "#DDLNivel"); log.write(f"tipo options {tipos}\n")
    basica = next(v for v, t in tipos if "BÁSICA" in t.upper() or "BASICA" in t.upper())
    states = [v for v, t in opts(pg, "#DDLEntidad") if v != "0"]
    for control in ("0", "1"):
        for st in states:
            for attempt in range(2):
                try:
                    pg.goto(URL, wait_until="networkidle", timeout=90000)
                    choose(pg, "#DDLciclos", "29"); choose(pg, "#DDLEscolarizadas", "1"); choose(pg, "#DDLNivel", basica)
                    choose(pg, "#DDLControl", control); choose(pg, "#DDLEntidad", st)
                    pg.click("#Button1"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1500)
                    tables = pg.eval_on_selector_all("table", "ts => ts.map(t => [...t.rows].map(r => [...r.cells].map(c => c.innerText.trim())))")
                    t = None
                    for tb in tables:
                        for i, row in enumerate(tb):
                            if row and row[0].strip().upper() == "MUNICIPIO": t = tb[i:]; break
                        if t: break
                    if not t: raise RuntimeError(f"no municipio table; {len(tables)} tables; first {str(tables[:1])[:300]}")
                    res[f"{control}|{st}"] = t; log.write(f"ok control {control} state {st}: {len(t)-2} municipalities\n"); break
                except Exception as e:
                    log.write(f"ERR control {control} state {st} try {attempt}: {str(e)[:200]}\n"); time.sleep(5)
            time.sleep(2)
            json.dump({"cycle": "2025-2026", "modalidad": "Escolarizada", "tipo": basica, "tables": res}, open(f"{OUT}/sep_basica_by_municipio.json", "w"), ensure_ascii=False)
    b.close()
log.close()

# v3
