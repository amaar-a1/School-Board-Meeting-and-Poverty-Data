# Temporary: Japan's newest welfare-rate table and municipal websites; Poland's pupils (slowly).
import html, json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/pij4"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)", "Accept": "*/*"}
log = open(f"{OUT}/log.txt", "w")
def get(u, t=300, hdr=None):
    with urllib.request.urlopen(urllib.request.Request(u, headers={**UA, **(hdr or {})}), timeout=t) as r:
        return r.read()
def step(name, f):
    t = time.time()
    try: log.write(f"== {name}\n{f()}\n({time.time()-t:.0f}s)\n\n")
    except Exception: log.write(f"== {name}\nERR {traceback.format_exc()[-1500:]}\n\n")
    log.flush()

ES = "https://www.e-stat.go.jp"
def japan_welfare():
    out, files = [], []
    # the survey's yearly groups (tstat), newest first
    t = get(f"{ES}/stat-search/files?page=1&toukei=00450312", 120).decode("utf-8", "ignore")
    tstats = sorted(set(re.findall(r"tstat=(\d+)", t)), reverse=True)
    out.append(f"tstat groups: {tstats[:15]}")
    for ts in tstats[:6]:
        for page in range(1, 8):
            u = f"{ES}/stat-search/files?page={page}&toukei=00450312&tstat={ts}&layout=dataset"
            try: t = get(u, 120).decode("utf-8", "ignore")
            except Exception as e: out.append(f"ERR {u} {str(e)[:60]}"); break
            got = 0
            for m in re.finditer(r'statInfId=(\d+)', t):
                ctx = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t[max(0, m.start() - 1500): m.start()])))[-300:]
                files.append({"id": m.group(1), "ctx": ctx, "tstat": ts}); got += 1
            # deeper groups (cycles / months) inside this year
            for l in sorted(set(re.findall(r'href="(/stat-search/files\?[^"]*tstat=' + ts + r'[^"]*tclass[^"]*)"', t)))[:10]:
                try:
                    t2 = get(ES + html.unescape(l) + "&layout=dataset", 120).decode("utf-8", "ignore")
                    for m in re.finditer(r'statInfId=(\d+)', t2):
                        ctx = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t2[max(0, m.start() - 1500): m.start()])))[-300:]
                        files.append({"id": m.group(1), "ctx": ctx, "tstat": ts})
                except Exception: pass
                time.sleep(0.7)
            if not got: break
            time.sleep(0.7)
    json.dump(files, open(f"{OUT}/jp_welfare_files.json", "w"), ensure_ascii=False, indent=0)
    hit = [f for f in files if "保護率" in f["ctx"] and "中核市" in f["ctx"]]
    out.append(f"files {len(files)}; rate tables {len(hit)}")
    def yr(f):
        m = re.search(r"調査年月\s+(\d{4})", f["ctx"]); return m.group(1) if m else ""
    hit.sort(key=yr, reverse=True)
    for f in hit[:6]:
        out.append(f"{f['id']} {yr(f)} {f['ctx'][-200:]}")
        try:
            b = get(f"{ES}/stat-search/file-download?statInfId={f['id']}&fileKind=0", 300)
            ext = "xlsx" if b[:2] == b"PK" else "xls" if b[:4] == b"\xd0\xcf\x11\xe0" else "csv"
            open(f"{OUT}/jp_w_{yr(f)}_{f['id']}.{ext}", "wb").write(b)
        except Exception as e: out.append(f"dl ERR {str(e)[:80]}")
        time.sleep(1)
    return "\n".join(out)
step("Japan: welfare rate tables", japan_welfare)

def japan_sites():
    q = """SELECT ?item ?code ?name ?site WHERE {
      ?item wdt:P429 ?code . OPTIONAL { ?item wdt:P856 ?site . }
      OPTIONAL { ?item rdfs:label ?name . FILTER(LANG(?name) = "ja") } }"""
    b = get("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q), 300, {"Accept": "application/sparql-results+json"})
    d = json.loads(b)["results"]["bindings"]
    rows = [{k: v["value"] for k, v in r.items()} for r in d]
    json.dump(rows, open(f"{OUT}/jp_wikidata_sites.json", "w"), ensure_ascii=False)
    return f"{len(rows)} rows; with website {sum(1 for r in rows if r.get('site'))}; sample {rows[:3]}"
step("Japan: municipal websites (Wikidata)", japan_sites)

BDL = "https://bdl.stat.gov.pl/api/v1"
def poland():
    out, pv = [], []
    for q in ["uczniowie"]:
        for page in range(4):
            for a in range(4):
                try:
                    d = json.loads(get(f"{BDL}/variables/search?name={urllib.parse.quote(q)}&level=6&page-size=100&page={page}&format=json&lang=pl", 120)); break
                except Exception as e:
                    out.append(f"search ERR {str(e)[:60]}"); time.sleep(90)
            else: break
            pv += [{k: v.get(k) for k in ("id", "subjectId", "n1", "n2", "n3", "n4", "n5", "measureUnitName")} for v in d.get("results", [])]
            if not d.get("links", {}).get("next"): break
            time.sleep(10)
    json.dump(pv, open(f"{OUT}/pl_pupil_vars.json", "w"), ensure_ascii=False, indent=0)
    cand = [v for v in pv if "podstaw" in " ".join(str(v.get(k) or "") for k in ("n1", "n2", "n3")).lower()]
    out.append(json.dumps(cand[:30], ensure_ascii=False)[:3000])
    data = {}
    for v in cand[:4]:
        vid = str(v["id"]); vals = {}
        for yr in ("2024", "2023"):
            page, got = 0, 0
            while True:
                try: d = json.loads(get(f"{BDL}/data/by-variable/{vid}?unit-level=6&year={yr}&page-size=100&page={page}&format=json&lang=pl", 120))
                except Exception as e:
                    out.append(f"{vid} ERR {str(e)[:60]}"); time.sleep(90); continue
                for r in d.get("results", []):
                    for x in r.get("values", []):
                        if x.get("val") is not None: vals[r["id"]] = x["val"]; got += 1
                if not d.get("links", {}).get("next"): break
                page += 1; time.sleep(4)
            out.append(f"{vid} {yr}: {got}")
            if got: break
        data[vid] = {"var": v, "values": vals}
        json.dump(data, open(f"{OUT}/pl_pupils.json", "w"), ensure_ascii=False)
    return "\n".join(out)
step("Poland: pupils", poland)
log.close()
