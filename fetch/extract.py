# Temporary: where Belgium's integration-income dashboard (stat.mi-is.be) gets its data by municipality; and
# Portugal's pupils by municipality (INE indicators found through dados.gov.pt).
import html, json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/bp5"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=200, hdr=None):
    err = None
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}), timeout=t) as r:
                return r.read()
        except Exception as e:
            err = e; time.sleep(30 * (a + 1))
    raise err
def step(name, f):
    try: log.write(f"== {name}\n{f()}\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1500:]}\n\n")
    log.flush()

B = "https://stat.mi-is.be"
def mi():
    out = []
    for p in ["/nl/dashboard/gpmis_leefloon_ratio?menu=map", "/fr/dashboard/ris_cities?menu=map", "/nl/dashboard/ris_entities?menu=drilldown"]:
        t = get(B + p).decode("utf-8", "ignore")
        open(f"{OUT}/mi_{re.sub(r'[^a-z_]', '_', p)[:40]}.html", "w").write(t)
        js = sorted(set(re.findall(r'src="([^"]+\.js[^"]*)"', t)))
        urls = sorted(set(re.findall(r'["\'](/[^"\']*(?:api|json|data|csv|xlsx|export|download)[^"\']*)["\']', t)))
        out.append(f"{p}: {len(t)} bytes; js {js[:15]}; urls {urls[:30]}")
        for j in js[:12]:
            u = j if j.startswith("http") else B + j
            try:
                s = get(u).decode("utf-8", "ignore")
                hits = sorted(set(re.findall(r'["\'`]((?:https?://[^"\'`]*)?/[^"\'`\s]*(?:api|json|csv|data|export|download)[^"\'`\s]*)["\'`]', s)))
                if hits: out.append(f"   {j}: {hits[:20]}")
            except Exception as e: out.append(f"   {j}: ERR {str(e)[:60]}")
        time.sleep(1)
    for guess in ["/api/dashboard/gpmis_leefloon_ratio", "/nl/api/dashboard/gpmis_leefloon_ratio", "/api/data/gpmis_leefloon_ratio", "/nl/dashboard/gpmis_leefloon_ratio/data",
                  "/nl/dashboard/gpmis_leefloon_ratio?menu=map&format=json", "/nl/export/gpmis_leefloon_ratio", "/nl/dashboard/gpmis_leefloon_ratio/export?format=csv"]:
        try:
            b = get(B + guess, 60); out.append(f"guess {guess}: {len(b)} {b[:160]!r}")
            open(f"{OUT}/mi_guess_{re.sub(r'[^a-z_]', '_', guess)[:40]}", "wb").write(b)
        except Exception as e: out.append(f"guess {guess}: ERR {str(e)[:60]}")
    return "\n".join(out)
step("Belgium: integration income dashboard", mi)

def pt_pupils():
    out = []
    for q in ["Alunos matriculados (N.º) por Localização geográfica", "Alunos matriculados no ensino básico", "Taxa bruta de escolarização", "Alunos matriculados"]:
        try: d = json.loads(get("https://dados.gov.pt/api/1/datasets/?page_size=50&q=" + urllib.parse.quote(q)))
        except Exception as e: out.append(f"[{q}] ERR {str(e)[:60]}"); continue
        for ds in d.get("data", []):
            u = next((r.get("url") for r in ds.get("resources", []) if "pindica.jsp" in (r.get("url") or "")), "")
            v = (re.search(r"varcd=(\d+)", u) or [None, ""])[1]
            if v and re.search(r"matricul|alunos", ds.get("title") or "", re.I): out.append(f"{v} | {ds.get('title')}")
        time.sleep(1)
    return "\n".join(sorted(set(out)))
log.close()
