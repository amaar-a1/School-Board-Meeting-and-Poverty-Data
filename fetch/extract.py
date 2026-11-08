# Temporary: Belgium's income-tax statistics by municipality (Statbel) and Portugal's INE indicators (found via dados.gov.pt).
import html, io, json, os, re, time, traceback, urllib.parse, urllib.request, zipfile
OUT = "fetch/out/bp2"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t) as r:
        return r.read()
def step(name, f):
    t = time.time()
    try: log.write(f"== {name}\n{f()}\n({time.time()-t:.0f}s)\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1500:]}\n\n")
    log.flush()

def statbel():
    out = []
    for p in ["/en/open-data/fiscal-statistics-income", "/en/open-data/fiscal-statistics-income-0", "/en/open-data/fiscal-statistics-income-1",
              "/en/open-data/fiscal-statistics-income-municipality", "/nl/open-data/fiscale-statistiek-van-de-inkomens-0"]:
        try: t = get("https://statbel.fgov.be" + p, 120).decode("utf-8", "ignore")
        except Exception as e: out.append(f"{p} ERR {str(e)[:60]}"); continue
        ls = sorted({html.unescape(h) for h in re.findall(r'href="([^"]+\.(?:zip|xlsx|csv|txt))"', t, re.I)})
        out.append(f"{p}: {ls}")
        for h in ls:
            if re.search(r"MUNTY|munty|SECTOR|TAX", h) and not re.search(r"SECTOR", h):
                u = h if h.startswith("http") else "https://statbel.fgov.be" + h
                try:
                    b = get(u, 300); fn = u.split("/")[-1].split("?")[0][-90:]
                    open(f"{OUT}/be_{fn}", "wb").write(b); out.append(f"  downloaded {fn} {len(b)}")
                except Exception as e: out.append(f"  dl ERR {u} {str(e)[:60]}")
        time.sleep(1)
    return "\n".join(out)
step("Statbel fiscal statistics", statbel)

def portugal():
    out, found = [], []
    for q in ["rendimento social de inserção", "beneficiários do rendimento social", "rendimento bruto declarado", "sujeitos passivos rendimento",
              "alunos matriculados", "alunos ensino básico", "taxa de pobreza", "beneficiários de prestações", "abono de família", "poder de compra"]:
        for page in (1, 2):
            try:
                d = json.loads(get(f"https://dados.gov.pt/api/1/datasets/?page_size=50&page={page}&q=" + urllib.parse.quote(q), 120))
            except Exception as e: out.append(f"[{q}] ERR {str(e)[:80]}"); break
            for ds in d.get("data", []):
                url = next((r.get("url") for r in ds.get("resources", []) if "pindica.jsp" in (r.get("url") or "")), "")
                v = (re.search(r"varcd=(\d+)", url) or [None, ""])[1]
                found.append({"q": q, "title": ds.get("title"), "varcd": v, "org": (ds.get("organization") or {}).get("name")})
            time.sleep(0.7)
    json.dump(found, open(f"{OUT}/pt_datasets.json", "w"), ensure_ascii=False, indent=0)
    seen = set()
    for f in found:
        if f["title"] in seen: continue
        seen.add(f["title"])
        if re.search(r"inser|declarado|sujeitos|matricul|alunos|pobreza|abono|prest|poder de compra", f["title"] or "", re.I):
            out.append(f"{f['varcd']} | {f['title']} | {f['org']}")
    return "\n".join(out[:150])
step("Portugal: INE indicators on dados.gov.pt", portugal)
log.close()
