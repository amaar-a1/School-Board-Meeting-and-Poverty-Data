# Temporary: Poland's BDL data by municipality; Italy's pupils files; Japan's municipal statistics (SSDS) files.
import html, io, json, os, re, subprocess, time, traceback, urllib.parse, urllib.request, zipfile
OUT = "fetch/out/pij2"; os.makedirs(OUT, exist_ok=True)
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

# ---------- Poland
BDL = "https://bdl.stat.gov.pl/api/v1"
def bdl_get(u):
    for a in range(5):
        try: return json.loads(get(u, 120))
        except Exception as e:
            if "429" in str(e): time.sleep(30 * (a + 1)); continue
            if a == 4: raise
            time.sleep(5)
def poland():
    out = []
    # units at level 6 (gminy)
    units, page = [], 0
    while True:
        d = bdl_get(f"{BDL}/units?level=6&page-size=100&page={page}&format=json&lang=pl")
        units += [{k: u.get(k) for k in ("id", "name", "parentId", "kind")} for u in d["results"]]
        if not d.get("links", {}).get("next"): break
        page += 1; time.sleep(0.6)
    json.dump(units, open(f"{OUT}/pl_units.json", "w"), ensure_ascii=False)
    out.append(f"units {len(units)} sample {units[:2]}")
    # pupils: variables in subjects about primary schools at level 6
    found = []
    for q in ["szkoły podstawowe", "uczniowie szkół podstawowych dla dzieci", "uczniowie ogółem"]:
        d = bdl_get(f"{BDL}/variables/search?name={urllib.parse.quote(q)}&level=6&page-size=100&format=json&lang=pl")
        found += [{k: v.get(k) for k in ("id", "subjectId", "n1", "n2", "n3", "n4", "n5", "measureUnitName")} for v in d.get("results", [])]
        time.sleep(1)
    json.dump(found, open(f"{OUT}/pl_pupil_vars.json", "w"), ensure_ascii=False, indent=0)
    # data
    want = {"259889": "family_benefit_share", "259888": "family_benefit_children", "1548717": "social_assistance_per10k",
            "72305": "pop_total_check", "862": "pupils_primary_old"}
    # newest pupils variable: the first that mentions 'uczniowie' and 'podstaw' in a subject with data in 2023
    for v in found:
        s = " ".join(str(v.get(k) or "") for k in ("n1", "n2", "n3", "n4", "n5")).lower()
        if "uczniowie" in s and "podstaw" in s and "ogółem" in s and v["id"] not in want: want[str(v["id"])] = "pupils_cand_" + str(v["id"])
    data = {}
    for vid, name in list(want.items())[:12]:
        vals = {}
        for yr in ("2024", "2023", "2022"):
            page = 0
            got = 0
            while True:
                try: d = bdl_get(f"{BDL}/data/by-variable/{vid}?unit-level=6&year={yr}&page-size=100&page={page}&format=json&lang=pl")
                except Exception as e: out.append(f"{vid} {yr} ERR {str(e)[:100]}"); break
                for r in d.get("results", []):
                    for x in r.get("values", []):
                        if x.get("val") is not None: vals.setdefault(r["id"], {})[yr] = x["val"]; got += 1
                if not d.get("links", {}).get("next"): break
                page += 1; time.sleep(0.6)
            out.append(f"{vid} {name} {yr}: {got} values")
            if got: break
        data[vid] = {"name": name, "values": vals}
    json.dump(data, open(f"{OUT}/pl_data.json", "w"), ensure_ascii=False)
    return "\n".join(out)
step("Poland: BDL", poland)

# ---------- Italy: pupils by school (state schools) and school directory
def italy():
    out = []
    page = get("https://dati.istruzione.it/opendata/opendata/catalogo/elements1/?area=Studenti", 120).decode("utf-8", "ignore")
    links = sorted(set(re.findall(r'([A-Z]{6,}\d{12,})\.csv', page)))
    out.append("Studenti links: " + ", ".join(l for l in links if "ALU" in l)[:3000])
    page2 = get("https://dati.istruzione.it/opendata/opendata/catalogo/elements1/?area=Scuole", 120).decode("utf-8", "ignore")
    links2 = sorted(set(re.findall(r'([A-Z]{6,}\d{12,})\.csv', page2)))
    out.append("Scuole links (STA/PAR latest): " + ", ".join(l for l in links2 if l.startswith(("SCUANAGRAFESTAT", "SCUANAGRAFEPAR")))[-800:])
    cands = [l for l in links if l.startswith(("ALUCORSOINDCLASTA", "ALUCORSOETASTA", "ALUSECGRADOSTA", "ALUCORSOINDCLAPAR"))]
    for kind in ("ALUCORSOINDCLASTA", "ALUCORSOETASTA", "ALUCORSOINDCLAPAR"):
        best = sorted(l for l in cands if l.startswith(kind))[-1:] if cands else []
        for l in best:
            try: b = get(f"https://dati.istruzione.it/opendata/opendata/catalogo/elements1/{l}.csv", 600); open(f"{OUT}/it_{l}.csv", "wb").write(b); out.append(f"{l}: {len(b)}")
            except Exception as e: out.append(f"{l}: ERR {str(e)[:100]}")
    par = sorted(l for l in links2 if l.startswith("SCUANAGRAFEPAR"))[-1:]
    for l in par:
        try: b = get(f"https://dati.istruzione.it/opendata/opendata/catalogo/elements1/{l}.csv", 600); open(f"{OUT}/it_{l}.csv", "wb").write(b); out.append(f"{l}: {len(b)}")
        except Exception as e: out.append(f"{l}: ERR {str(e)[:100]}")
    return "\n".join(out)
step("Italy: pupils", italy)

# ---------- Japan: crawl e-Stat SSDS file pages for the municipal tables
ES = "https://www.e-stat.go.jp"
def japan():
    out, seen, files = [], set(), []
    front = get(f"{ES}/stat-search/files?page=1&toukei=00200502&layout=dataset", 120).decode("utf-8", "ignore")
    open(f"{OUT}/jp_front.html", "w").write(front)
    queue = [f"{ES}/stat-search/files?page=1&toukei=00200502&layout=dataset"]
    n = 0
    while queue and n < 120:
        u = queue.pop(0)
        if u in seen: continue
        seen.add(u); n += 1
        try: t = get(u, 120).decode("utf-8", "ignore")
        except Exception as e: out.append(f"ERR {u} {str(e)[:80]}"); continue
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", t))
        for m in re.finditer(r'statInfId=(\d+)', t):
            seg = t[max(0, m.start() - 1500): m.start()]
            title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", seg))[-260:]
            files.append({"id": m.group(1), "ctx": html.unescape(title), "page": u})
        if "市区町村" in t or n < 4:
            for l in re.findall(r'href="(/stat-search/files\?[^"]+)"', t):
                l = html.unescape(l)
                if "toukei=00200502" in l and ("tstat=" in l or "tclass" in l or "cycle" in l) and "layout" not in l:
                    queue.append(ES + l + "&layout=dataset" if "page=" in l else ES + l)
        time.sleep(1)
    json.dump(files, open(f"{OUT}/jp_files.json", "w"), ensure_ascii=False, indent=0)
    out.append(f"pages {n}, files {len(files)}")
    want = [f for f in files if "市区町村" in f["ctx"]]
    out.append("municipal-looking: " + json.dumps(want[:40], ensure_ascii=False)[:4000])
    got = 0
    for f in want[:30]:
        try:
            b = get(f"{ES}/stat-search/file-download?statInfId={f['id']}&fileKind=0", 300)
            ext = "xlsx" if b[:2] == b"PK" else "xls" if b[:4] == b"\xd0\xcf\x11\xe0" else "csv" if b[:1] != b"<" else "html"
            open(f"{OUT}/jp_{f['id']}.{ext}", "wb").write(b); got += 1
        except Exception as e: out.append(f"dl {f['id']} ERR {str(e)[:80]}")
        time.sleep(1)
    out.append(f"downloaded {got}")
    return "\n".join(out)
step("Japan: SSDS crawl", japan)
log.close()
