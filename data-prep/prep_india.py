"""Turns the India downloads (made on GitHub's runner) into the small inputs build_latam.india() reads (data-prep/inputs/india/).

- ind_geo.geojson: the 735 districts of geoBoundaries gbOpen IND ADM2 (simplified), each placed in its state or union
  territory by where it lies in geoBoundaries IND ADM1.
- ind_data.json, per district (geoBoundaries shapeID):
  mpi: NITI Aayog, "National Multidimensional Poverty Index: A Progress Review 2023" (based on NFHS-5, 2019-21), the
    district headcount ratio (share of people who are multidimensionally poor), from each state's district table
    (NFHS-4 and NFHS-5 headcount ratio, intensity and MPI), or, where that table can't be read (Bihar and a few small
    states and union territories), from the state's district chart of the headcount ratio;
  pop, pop_year: English Wikipedia, "List of districts in India" (mostly Census 2011), matched by name within the state;
  meetings: the zila parishad's (district council's) YouTube channel, where one was found.
Districts created after NFHS-5 have no figure of their own. Names in the report and on the map differ (renamed districts,
spellings); ALIAS maps them.
Then, after build_latam.py, run data-prep/simplify_borders.sh (a lighter copy of the map file for zoomed-out views).
Usage: python3 data-prep/prep_india.py NITI_PDF WIKI_HTML GEODIR [MEETINGS_DIR (fetch/in_yt.py output)]
"""
import collections, difflib, html, json, os, re, sys, unicodedata
import pdfplumber
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "india")


def tables(pdf):
    out = []
    with pdfplumber.open(pdf) as P:
        state = ""
        for pno, pg in enumerate(P.pages):
            t = pg.extract_text() or ""
            m = re.search(r"([A-Z][A-Z &]+?)\s*MPI: PROGRESS REVIEW 2023|MPI: PROGRESS REVIEW 2023\s*\n?\s*([A-Z][A-Z &]+)\n", t)
            words = pg.extract_words()
            if sum(w["text"] == "Intensity" for w in words) < 2: continue
            num = [w for w in words if re.fullmatch(r"\d+\.\d+%", w["text"])]
            if len(num) < 12: continue
            hdr = max((w["top"] for w in words if w["text"] == "Intensity"), default=0)
            num = [w for w in num if w["top"] > hdr]
            cols = []
            for w in sorted(num, key=lambda w: (w["x0"] + w["x1"]) / 2):
                c = (w["x0"] + w["x1"]) / 2
                if cols and abs(cols[-1]["c"] - c) < 14: cols[-1]["w"].append(w)
                else: cols.append({"c": c, "w": [w]})
            cols = [c["w"] for c in cols if len(c["w"]) >= 3]
            if len(cols) < 4: continue
            h5 = sorted(cols[2], key=lambda w: w["top"])          # NFHS-5 headcount: the third % column (H4, A4, H5, A5)
            h4 = sorted(cols[0], key=lambda w: w["top"])          # NFHS-4 (2015-16) headcount, same rows
            left = min(w["x0"] for c in cols for w in c)
            nw = [w for w in words if w["x1"] < left - 2 and w["top"] > hdr + 3 and not re.fullmatch(r"[\d.%]+", w["text"])]
            lines = []
            for w in sorted(nw, key=lambda w: (round(w["top"]), w["x0"])):
                if lines and abs(lines[-1]["top"] - w["top"]) < 2.5: lines[-1]["t"] += " " + w["text"]; lines[-1]["b"] = max(lines[-1]["b"], w["bottom"])
                else: lines.append({"top": w["top"], "b": w["bottom"], "t": w["text"]})
            mid = lambda o: (o["top"] + o.get("b", o.get("bottom"))) / 2
            owner = {}
            for i, v in enumerate(h5):
                j = min(range(len(lines)), key=lambda j: abs(mid(lines[j]) - mid(v))) if lines else None
                if j is not None and abs(mid(lines[j]) - mid(v)) < 10: owner[j] = i
            names = {i: [] for i in range(len(h5))}
            for j, l in enumerate(lines):
                if j in owner: names[owner[j]].append((l["top"], l["t"])); continue
                near = [k for k in (j - 1, j + 1) if k in owner and abs(lines[k]["top"] - l["top"]) < 14]
                if near:   # a wrapped name's other line: to the closer neighbouring name
                    k = min(near, key=lambda k: abs(lines[k]["top"] - l["top"])); names[owner[k]].append((l["top"], l["t"]))
            names = {i: [t for _, t in sorted(v)] for i, v in names.items()}
            rows = [(" ".join(names[i]), float(v["text"][:-1])) for i, v in enumerate(h5)]
            out.append({"page": pno + 1, "state": (m.group(1) or m.group(2)).strip() if m else "", "rows": rows,
                        # the NFHS-4 figure on the same line (districts created since 2015-16 have none)
                        "h4": [next((float(u["text"][:-1]) for u in h4 if abs(mid(u) - mid(v)) < 4), None) for v in h5]})
    return out


def charts(pdf):
    out = []
    with pdfplumber.open(pdf) as P:
        for pno, pg in enumerate(P.pages):
            t = pg.extract_text() or ""
            m = re.search(r"^(.+?): Headcount Ratio\nPercentage of population who are multidimensionally poor in each district", t, re.M)
            if not m: continue
            state = re.sub(r"\s*MPI: PROGRESS REVIEW 2023.*", "", t.splitlines()[0]).strip() or m.group(1)
            words = pg.extract_words()
            pct = [w for w in words if re.fullmatch(r"\d+\.\d+%", w["text"])]
            left = min((w["x0"] for w in pct), default=999)
            names = [w for w in words if w["x1"] < left and not re.fullmatch(r"[\d.%]+", w["text"]) and w["top"] > 100 and w["text"] not in ("tcirtsiD",)]
            lines = []
            for w in sorted(names, key=lambda w: (round(w["top"]), w["x0"])):
                if lines and abs(lines[-1]["top"] - w["top"]) < 3: lines[-1]["t"] += " " + w["text"]
                else: lines.append({"top": w["top"], "t": w["text"]})
            rows = []
            for l in lines:
                near = sorted([w for w in pct if abs(w["top"] - l["top"]) < 4], key=lambda w: abs(w["top"] - l["top"]))
                if near: rows.append((l["t"], float(near[0]["text"][:-1])))
            out.append({"page": pno + 1, "state": m.group(1).strip(), "rows": rows, "n_pct": len(pct)})
    return out


fold=lambda s: re.sub(r"[^a-z]","",unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower())
sk=lambda s: fold(s).replace("and","")
dk=lambda s: re.sub(r"district$","",fold(s))
ALIAS={"gurugram":"gurgaon","belagavi":"belgaum","mysuru":"mysore","beed":"bid","dang":"thedangs","dantewada":"dakshinbastardantewada","spsrnellore":"sripottisriramulunellore",
       "ysrkadapa":"ysr","korea":"koriya","bengaluruurban":"bangalore","bengalururural":"bangalorerural","ballari":"bellary","vijayapura":"bijapur","kalaburagi":"gulbarga","ysrkadapa":"kadapaysr","ysr":"kadapaysr","kamrupmetro":"kamrupmetropolitan","raigad":"raigarh","sonepur":"subarnapur",
       "gangtok":"east","gyalshing":"west","mangan":"north","namchi":"south","howrah":"haora","northparganas":"northtwentyfourparganas","southparganas":"southtwentyfourparganas","kasganj":"kanshiramnagar",
       "warangalrural":"warangalr","warangalurban":"warangalu","westkarbianglong":"karbianglongwest","botad":"batod","agarmalwa":"agar","bhadradrikothagudem":"bhadradri",
       "jayashankarbhupalapally":"jayashankar","kumurambheemasifabad":"komarambheem","medchalmalkajgiri":"medchal","purbabardhaman":"barddhaman","pashchim":"pashchimchamparan","purbi":"purbachamparan"}
def load(geo5):
    st=json.load(open(f"{geo5}/geoBoundaries-IND-ADM1_simplified.geojson"))["features"]
    ds=json.load(open(f"{geo5}/geoBoundaries-IND-ADM2_simplified.geojson"))["features"]
    S=[(f["properties"]["shapeName"],shape(f["geometry"])) for f in st]
    out=[]
    for f in ds:
        p=shape(f["geometry"]).representative_point()
        s=next((n for n,g in S if g.contains(p)),"Lakshadweep")
        out.append((s,f))
    return out
def match(rows, geo):
    by=collections.defaultdict(list)
    for s,f in geo: by[dk(f["properties"]["shapeName"])].append((sk(s),f))
    res={}; miss=[]
    for r in rows:
        s,n=r[0],r[1]
        alts=[n]+re.findall(r"\(([^)]+)\)",n)+[re.sub(r"\s*\(.*?\)","",n)]
        keys=[ALIAS.get(dk(a),dk(a)) for a in alts if dk(a)]
        cand=[c for k in keys for c in by.get(k,[])]
        if len({id(c[1]) for c in cand})>1: cand=[c for c in cand if c[0]==sk(s)] or cand
        if len({id(c[1]) for c in cand})!=1:
            loc=[(k2,c) for k2,cs in by.items() for c in cs if c[0]==sk(s)]
            m=difflib.get_close_matches(keys[0] if keys else "", [k2 for k2,_ in loc], n=1, cutoff=0.8) if keys else []
            cand=[c for k2,c in loc if m and k2==m[0]]
        if len({id(c[1]) for c in cand})==1: res.setdefault(cand[0][1]["properties"]["shapeID"],[]).append(r)
        else: miss.append((s,n))
    return res,miss


# Channels the search found that aren't the district's zila parishad (checked by hand): a DJ, a news channel, a
# personal channel, a town council, a village panchayat, a block (janpad) panchayat and another district's council.
NOT_ZP = {"Banka", "Kozhikode", "Chhindwara", "Dindori", "Supaul", "Betul", "Kamrup"}

# Map names -> Wikipedia's (renamed or respelled districts)
POP_ALIAS = {"punch": "poonch", "dohad": "dahod", "kachchh": "kutch", "pashchimisinghbhum": "westsinghbhum", "purbisinghbhum": "eastsinghbhum",
             "pashchimchamparan": "westchamparan", "purbachamparan": "eastchamparan", "mewat": "nuh", "uttarbastarkanker": "kanker", "garhwal": "pauri",
             "kochbihar": "coochbehar", "hugli": "hooghly", "muktsar": "srimuktsarsahib", "baleshwar": "balasore", "kheri": "lakhimpurkheri",
             "mahamayanagar": "hathras", "jyotibaphulenagar": "amroha", "allahabad": "prayagraj", "ramanagara": "bengalurusouth",
             "bangalore": "bangaloreurban",   # the map's "Bangalore" is Bengaluru Urban, not Bangalore Rural
             "thenilgiris": "nilgiris", "faizabad": "ayodhya", "warangalu": "hanamkonda"}   # not Theni, Firozabad, Warangal (Rural)
# 2011 census populations for the area the map draws, where the Wikipedia list gives a different area's: Andhra Pradesh's 13
# districts before the 2022 reorganisation (the list has the new, smaller districts' 2021 estimates; these add up to the
# state's 49,386,799), Chennai before its 2018 enlargement and Kancheepuram before Chengalpattu was split off in 2019 (the
# map has the older borders), and Phek and Peren (the list repeats Phek's figure for Peren). Census of India 2011, Primary
# Census Abstract.
POP_FIX = {"Srikakulam": 2703114, "Vizianagaram": 2344474, "Visakhapatnam": 4290589, "East Godavari": 5154296, "West Godavari": 3936966,
           "Krishna": 4517398, "Guntur": 4887813, "Prakasam": 3397448, "Sri Potti Sriramulu Nellore": 2963557, "Kadapa(YSR)": 2882469,
           "Kurnool": 4053463, "Anantapur": 4081148, "Chittoor": 4174064, "Chennai": 4646732, "Kancheepuram": 3998252,
           "Phek": 163418, "Peren": 95219}


def population(path):
    """{(state key, district key): (population, year)} from the Wikipedia tables (one per state)."""
    cl = lambda c: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>|\[\w+\]", "", c))).strip()
    s = open(path, encoding="utf-8").read()
    out = {}
    heads = [(m.start(), cl(m.group(1))) for m in re.finditer(r"<h[23][^>]*>(.*?)</h[23]>", s, re.S)]
    for m in re.finditer(r"<table.*?</table>", s, re.S):
        rows = [[cl(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)] for r in re.findall(r"<tr.*?</tr>", m.group(0), re.S)]
        if not rows or not any(h.startswith("Population") for h in rows[0]) or "District" not in " ".join(rows[0]): continue
        state = [h for p, h in heads if p < m.start()]
        state = re.sub(r"\s*\(.*?\)|\[edit\]|Districts? of ", "", state[-1]).strip() if state else ""
        ip = next(i for i, h in enumerate(rows[0]) if h.startswith("Population")); idist = next(i for i, h in enumerate(rows[0]) if h.startswith("District"))
        year = re.search(r"(\d{4})", rows[0][ip]); year = year.group(1) if year else ""
        for r in rows[1:]:
            if len(r) <= ip or not re.match(r"[\d,]+$", r[ip]): continue
            out[(sk(state), dk(r[idist]))] = (int(r[ip].replace(",", "")), year)
    return out


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 3), round(c[1], 3)]


def main(pdf, wiki, geo5, meetdir=None):
    tab = [t for t in tables(pdf) if t["state"] != "INDIA"]
    rows, have = [], set()
    for t in tab:
        st = t["state"] or "ANDAMAN & NICOBAR ISLANDS"; have.add(sk(st)); rows += [(st, n, h) for n, h in t["rows"] if n]
    for c in charts(pdf):
        if sk(c["state"]) not in have: rows += [(c["state"], n, h) for n, h in c["rows"] if n != "Champaran"]   # the wrapped name's 2015-16 line
    geo = load(geo5)
    res, miss = match(rows, geo)
    pop = population(wiki)
    meet = {}
    if meetdir:
        import glob
        for f in glob.glob(os.path.join(meetdir, "in_meet_*.json")): meet.update(json.load(open(f, encoding="utf-8")))
    # Borders follow de facto control: districts in Jammu and Kashmir and Ladakh are clipped to the area India administers
    # (Natural Earth's India plus the Siachen Glacier), leaving Pakistan-administered Kashmir and China-administered Aksai Chin
    # to those countries on the world map. Elsewhere geoBoundaries' finer borders are kept.
    from shapely.geometry import mapping
    from shapely.ops import unary_union
    ne = [f for f in json.load(open(os.path.join(HERE, "inputs", "world", "ne_50m_admin_0_countries.geojson"), encoding="utf-8"))["features"] if f["properties"]["ADM0_A3"] in ("IND", "KAS")]
    held = unary_union([shape(f["geometry"]).buffer(0) for f in ne])
    data, feats, nopop = {}, [], []
    for st, f in geo:
        sid = f["properties"]["shapeID"]; name = f["properties"]["shapeName"]
        if name == "DATA NOT AVAILABLE": continue   # Aksai Chin: administered by China
        if sk(st) in ("jammukashmir", "ladakh"):
            g = shape(f["geometry"]).buffer(0).intersection(held)
            if g.is_empty: continue
            f = {**f, "geometry": mapping(g.buffer(0))}
        x = {"name": name, "state": unicodedata.normalize("NFKD", st).encode("ascii", "ignore").decode()}
        if sid in res:
            v = [r[2] for r in res[sid]]; x["mpi"] = round(sum(v) / len(v), 2)   # Warangal Rural and Urban share one border: their mean
            if len(v) > 1: x["mpi_note"] = " and ".join(r[1] for r in res[sid])
        rev = {v: k for k, v in ALIAS.items()}
        rev.update(POP_ALIAS)
        alts = [name] + re.findall(r"\(([^)]+)\)", name) + [re.sub(r"\s*\(.*?\)", "", name)]
        keys = [k for a in alts for k in (dk(a), ALIAS.get(dk(a), ""), rev.get(dk(a), "")) if k]
        cands = [k[1] for k in pop if k[0] == sk(st)]
        p = next((pop[(sk(st), k)] for k in keys if (sk(st), k) in pop), None)
        if not p:
            c = [w for k in keys for w in cands if len(k) >= 4 and (w.startswith(k) or k.startswith(w))] or [w for k in keys for w in difflib.get_close_matches(k, cands, n=1, cutoff=0.75)]
            p = pop.get((sk(st), c[0])) if c else None
        if p: x["pop"], x["pop_year"] = p
        if name.strip() in POP_FIX: x["pop"], x["pop_year"] = POP_FIX[name.strip()], "2011"
        else: nopop.append((st, name))
        m = meet.get("IND-" + sid[-8:]) or {}
        if m.get("url") and name not in NOT_ZP: x["meetings"] = {"channel": m["channel"], "url": m["url"], "videos": m["videos"]}
        data[sid] = x
        feats.append({"type": "Feature", "properties": {"id": "IND-" + sid[-8:], "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "ind_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "ind_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(len(data), "districts;", sum("mpi" in x for x in data.values()), "with MPI;", sum("pop" in x for x in data.values()), "with population; report rows unmatched:", miss)
    print("no population:", nopop[:40], len(nopop))


def history(pdf, geo5):
    """Adds each district's NFHS-4 (2015-16) headcount ratio from the same district tables to ind_data.json, as
    mpi_years {"2016": NFHS-4, "2020": NFHS-5} (the surveys' middle years), for change over time. Districts read from the
    state charts (Bihar and a few small states and territories) have the 2019-21 figure only.
    Usage: python3 data-prep/prep_india.py --history NITI_PDF GEODIR"""
    rows = []
    for t in tables(pdf):
        if t["state"] == "INDIA" or not t["h4"]: continue
        st = t["state"] or "ANDAMAN & NICOBAR ISLANDS"
        rows += [(st, n, h4) for (n, _), h4 in zip(t["rows"], t["h4"]) if n and h4 is not None]
    res, miss = match(rows, load(geo5))
    p = os.path.join(OUT, "ind_data.json"); data = json.load(open(p, encoding="utf-8"))
    n = 0
    for sid, x in data.items():
        if sid in res and x.get("mpi") is not None:
            v = [r[2] for r in res[sid]]
            x["mpi_years"] = {"2016": round(sum(v) / len(v), 2), "2020": x["mpi"]}; n += 1
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(n, "districts with both surveys; unmatched", len(miss))


if __name__ == "__main__" and sys.argv[1] == "--history":
    history(*sys.argv[2:])
elif __name__ == "__main__":
    main(*sys.argv[1:])
