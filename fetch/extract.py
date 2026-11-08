# Temporary: Poland's BDL data by municipality (retry); Japan's welfare survey tables (被保護者調査).
import html, io, json, os, re, time, traceback, urllib.parse, urllib.request
OUT = "fetch/out/pij3"; os.makedirs(OUT, exist_ok=True)
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

BDL = "https://bdl.stat.gov.pl/api/v1"
def bdl_get(u):
    last = None
    for a in range(6):
        try:
            d = json.loads(get(u, 120))
            if isinstance(d, dict) and "results" in d: return d
            last = f"no results: {str(d)[:200]}"
        except Exception as e:
            last = str(e)[:200]
        time.sleep(20 * (a + 1))
    raise RuntimeError(last)
def poland():
    out = []
    pv = []
    for q in ["uczniowie", "szkoły podstawowe"]:
        for page in range(3):
            try:
                d = bdl_get(f"{BDL}/variables/search?name={urllib.parse.quote(q)}&level=6&page-size=100&page={page}&format=json&lang=pl")
            except Exception as e: out.append(f"search {q} ERR {e}"); break
            pv += [{k: v.get(k) for k in ("id", "subjectId", "n1", "n2", "n3", "n4", "n5", "measureUnitName")} for v in d["results"]]
            if not d.get("links", {}).get("next"): break
            time.sleep(1.5)
    json.dump(pv, open(f"{OUT}/pl_pupil_vars.json", "w"), ensure_ascii=False, indent=0)
    want = {"259889": "family_benefit_share", "259888": "family_benefit_children", "1548717": "social_assistance_per10k"}
    for v in pv:
        s = " / ".join(str(v.get(k) or "") for k in ("n1", "n2", "n3", "n4", "n5")).lower()
        if "uczniowie" in s and "podstaw" in s and ("ogółem" in s or s.endswith("uczniowie")) and "specjal" not in s.split("/")[0]:
            want.setdefault(str(v["id"]), "pupils: " + s[:120])
    out.append("variables: " + json.dumps(want, ensure_ascii=False)[:2000])
    data = {}
    for vid, name in list(want.items())[:14]:
        vals, names = {}, {}
        for yr in ("2024", "2023", "2022", "2021"):
            page, got = 0, 0
            while True:
                try: d = bdl_get(f"{BDL}/data/by-variable/{vid}?unit-level=6&year={yr}&page-size=100&page={page}&format=json&lang=pl")
                except Exception as e: out.append(f"{vid} {yr} ERR {str(e)[:100]}"); break
                for r in d["results"]:
                    names[r["id"]] = r.get("name")
                    for x in r.get("values", []):
                        if x.get("val") is not None: vals.setdefault(r["id"], {})[yr] = x["val"]; got += 1
                if not d.get("links", {}).get("next"): break
                page += 1; time.sleep(1.2)
            out.append(f"{vid} {yr}: {got} values")
            if got >= 2000: break
        data[vid] = {"name": name, "values": vals, "unit_names": names}
        json.dump(data, open(f"{OUT}/pl_data.json", "w"), ensure_ascii=False)
    return "\n".join(out)
step("Poland: BDL", poland)

ES = "https://www.e-stat.go.jp"
def japan():
    out, files, seen = [], [], set()
    queue = [f"{ES}/stat-search/files?page=1&toukei=00450312&layout=dataset", f"{ES}/stat-search/files?page=2&toukei=00450312&layout=dataset",
             f"{ES}/stat-search/files?page=1&toukei=00450312"]
    n = 0
    while queue and n < 60:
        u = queue.pop(0)
        if u in seen: continue
        seen.add(u); n += 1
        try: t = get(u, 120).decode("utf-8", "ignore")
        except Exception as e: out.append(f"ERR {u} {str(e)[:80]}"); continue
        for m in re.finditer(r'statInfId=(\d+)', t):
            seg = t[max(0, m.start() - 1500): m.start()]
            files.append({"id": m.group(1), "ctx": html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", seg)))[-300:], "page": u})
        for l in re.findall(r'href="(/stat-search/files\?[^"]+)"', t):
            l = html.unescape(l)
            if "toukei=00450312" in l and "tstat=" in l and l not in seen:
                queue.append(ES + l + ("&layout=dataset" if "layout" not in l else ""))
        time.sleep(1)
    json.dump(files, open(f"{OUT}/jp_welfare_files.json", "w"), ensure_ascii=False, indent=0)
    out.append(f"pages {n}, files {len(files)}")
    hit = [f for f in files if re.search(r"保護率|被保護実人員", f["ctx"]) and re.search(r"指定都市|中核市|都道府県", f["ctx"])]
    out.append(json.dumps(hit[:30], ensure_ascii=False)[:5000])
    for f in hit[:8]:
        try:
            b = get(f"{ES}/stat-search/file-download?statInfId={f['id']}&fileKind=0", 300)
            ext = "xlsx" if b[:2] == b"PK" else "xls" if b[:4] == b"\xd0\xcf\x11\xe0" else "csv" if b[:1] != b"<" else "html"
            open(f"{OUT}/jp_w_{f['id']}.{ext}", "wb").write(b)
        except Exception as e: out.append(f"dl {f['id']} ERR {str(e)[:80]}")
        time.sleep(1)
    return "\n".join(out)
step("Japan: welfare survey", japan)
log.close()
