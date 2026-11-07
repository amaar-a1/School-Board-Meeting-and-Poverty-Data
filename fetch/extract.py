# Temporary: Ecuador's school register (MINEDUC, Registro Administrativo Histórico 2009-2024, start of year):
# pupils by canton for the latest school year.
import csv, io, json, os, re, time, traceback, urllib.request
OUT = "fetch/out/ec_amie"; os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (school-board research project; github.com/amaar-a1)"}
log = open(f"{OUT}/log.txt", "w")
u = "https://www.datosabiertos.gob.ec/dataset/5d1838d2-4efb-44a3-8c36-eebb5a8f798a/resource/59db7bb5-eb6b-4a7a-a06a-d1f93ac7506a/download/registro-administrativo-historico_2009-2024-inicio.csv"
try:
    for a in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=1500) as r: b = r.read(); break
        except Exception as e:
            log.write(f"try {a}: {e}\n"); time.sleep(20)
    log.write(f"{len(b)} bytes\n")
    for enc in ("utf-8-sig", "latin-1"):
        try: t = b.decode(enc); break
        except Exception: pass
    first = t[:3000]; delim = max([";", ",", "|", "\t"], key=first.count)
    rd = csv.reader(io.StringIO(t), delimiter=delim); head = next(rd)
    log.write(f"delimiter {delim!r}; header {head}\n")
    rows = []
    for i, row in enumerate(rd):
        if i < 3: log.write(f"row {row}\n")
        rows.append(row)
    H = [h.strip().lower() for h in head]
    def col(*pats):
        for p in pats:
            for i, h in enumerate(H):
                if re.search(p, h): return i
        return None
    yr = col(r"^a[ñn]o_?lectivo|periodo|a[ñn]o"); cc = col(r"cod.*cant|cant.*cod|^dpa_?cant"); cn = col(r"^cant[oó]n|nombre.*cant")
    sx = [i for i, h in enumerate(H) if re.search(r"^total_?(estudiantes|alumnos)|^estudiantes_?total|^total$", h)]
    tot = sx[0] if sx else None
    sost = col(r"sostenimiento")
    log.write(f"year col {yr} {H[yr] if yr is not None else ''}; canton code {cc} {H[cc] if cc is not None else ''}; canton name {cn}; total {tot} {H[tot] if tot is not None else ''}; sostenimiento {sost}\n")
    years = sorted({r[yr] for r in rows if yr is not None and len(r) > yr})
    log.write(f"years {years}\n")
    last = years[-1] if years else None
    agg = {}
    for r in rows:
        if len(r) <= max(x for x in (yr, cc, tot) if x is not None) or r[yr] != last: continue
        k = r[cc] if cc is not None else r[cn]
        try: n = float(r[tot].replace(",", "."))
        except Exception: continue
        a = agg.setdefault(k, {"name": r[cn] if cn is not None else "", "total": 0, "fiscal": 0, "schools": 0})
        a["total"] += n; a["schools"] += 1
        if sost is not None and re.search(r"fiscal", r[sost], re.I) and not re.search(r"fiscomisional", r[sost], re.I): a["fiscal"] += n
    json.dump({"year": last, "by_canton": agg}, open(f"{OUT}/ec_pupils_by_canton.json", "w"), ensure_ascii=False)
    log.write(f"cantons {len(agg)}; sample {list(agg.items())[:3]}\n")
except Exception:
    log.write(traceback.format_exc()[-1500:])
log.close()
