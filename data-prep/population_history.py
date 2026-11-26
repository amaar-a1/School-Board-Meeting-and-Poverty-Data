"""Population by year for countries whose builds have only one year, from official series downloaded on GitHub's
runner (fetch rounds 50-51), and the step that adds them to the site's data files as the "Population by year" column.

  python3 data-prep/population_history.py prep RAWDIR   writes data-prep/inputs/population_history.json
  python3 data-prep/population_history.py apply         adds or refreshes the column in docs/data/*.csv (safe to re-run;
                                                         run after the builds, which don't write it themselves)

Sources:
- Europe (France, Italy, Spain, Poland, Czechia, Croatia, Belgium, the Netherlands, Denmark, Norway, Sweden, Finland,
  Iceland): Eurostat GISCO Local Administrative Units, the population of every LAU on 1 January of each year 2016-2023
  (LAU_RG_01M_YYYY_4326.geojson, POP_YYYY), plus 2024 from the LAU file each build already uses. A municipality created
  by a merger has its former municipalities added up for the years before, from the official lists of mergers in
  inputs/border_changes.json (France, Italy, the Netherlands: prep_border_changes.py; see borders.py); elsewhere it
  has only the years since. Belgium's 2025 mergers are added up from their former municipalities.
  Brazil's five municipalities installed in 2013 are splits: their parents keep their own years, and each family
  is added up on the earlier borders too ("Population by year (earlier borders)").
- Germany (districts) and Switzerland (cantons): Eurostat demo_r_pjanaggr3, population on 1 January by NUTS 3 region.
- United Kingdom: ONS mid-year population estimates by local authority, 2011 on (Nomis NM_2002_1).
- Japan: population censuses 1980-2020 by municipality (e-Stat, SSDS 0000020201, A1101).
- Australia: ABS estimated resident population by local government area (2024 boundaries), 2001-2024
  (ABS_ANNUAL_ERP_LGA2024), matched by LGA code.
- Argentina: INDEC population projections by province, 1 July of each year (based on the 2010 census), to 2026.
- Colombia: DANE municipal population (back-)projections 2005-2017 and projections 2018-2042 (updated July 2025), both
  consistent with the 2018 census, to the current year.
- Mexico: CONAPO, "Reconstrucción y proyecciones de la población de los municipios de México 1990-2040" (2024):
  mid-year population, reconstructed for 1990-2020 and projected from 2021, to the current year (fetch round 55).
- Brazil: IBGE's population estimates by municipality for 1 July, 2001-2025 (SIDRA table 6579; none for the census
  years 2007, 2010 and 2022).
"""
import csv, glob, gzip, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import borders

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs")
DOCS = os.path.join(HERE, "..", "docs", "data")
OUTF = os.path.join(IN, "population_history.json")
COL = "Population by year"
# csv name -> (LAU country code, District ID -> GISCO_ID)
LAU = {"france": ("FR", lambda i: "FR_" + i.split("-", 1)[1]), "italy": ("IT", lambda i: "IT_" + i.split("-", 1)[1]),
       "spain": ("ES", lambda i: "ES_" + i.split("-", 1)[1]), "czechia": ("CZ", lambda i: "CZ_" + i.split("-", 1)[1]),
       "croatia": ("HR", lambda i: "HR_" + i.split("-", 1)[1]), "belgium": ("BE", lambda i: "BE_" + i.split("-", 1)[1]),
       "netherlands": ("NL", lambda i: "NL_" + i.split("-", 1)[1]), "denmark": ("DK", lambda i: "DK_" + i.split("-", 1)[1]),
       "norway": ("NO", lambda i: "NO_" + i.split("-", 1)[1]), "sweden": ("SE", lambda i: "SE_" + i.split("-", 1)[1]),
       "finland": ("FI", lambda i: "FI_" + i.split("-", 1)[1]), "iceland": ("IS", lambda i: "IS_" + i.split("-", 1)[1]),
       "poland": ("PL", None)}
CH = {"VD": "CH011", "VS": "CH012", "GE": "CH013", "BE": "CH021", "FR": "CH022", "SO": "CH023", "NE": "CH024", "JU": "CH025", "BS": "CH031",
      "BL": "CH032", "AG": "CH033", "ZH": "CH040", "GL": "CH051", "SH": "CH052", "AR": "CH053", "AI": "CH054", "SG": "CH055", "GR": "CH056",
      "TG": "CH057", "LU": "CH061", "UR": "CH062", "SZ": "CH063", "OW": "CH064", "NW": "CH065", "ZG": "CH066", "TI": "CH070"}


def ids(name):
    return [r["District ID"] for r in csv.DictReader(open(os.path.join(DOCS, f"{name}.csv"), encoding="utf-8"))]


def lau_2024():
    """GISCO_ID -> 2024 population, from the LAU files the builds use."""
    out = {}
    for f in glob.glob(os.path.join(IN, "*", "lau_*.geojson")):
        for ft in json.load(open(f, encoding="utf-8"))["features"]:
            p = ft["properties"]
            if p.get("GISCO_ID") and p.get("POP_2024"): out[p["GISCO_ID"]] = int(p["POP_2024"])
    return out


def prep(raw):
    res = {}
    lau = {}
    for f in sorted(glob.glob(os.path.join(raw, "lau_pop_20??.json"))):
        y = re.search(r"(20\d\d)", os.path.basename(f)).group(1)
        for c, d in json.load(open(f)).items():
            for g, v in d.items(): lau.setdefault(g, {})[y] = int(v)
    for g, v in lau_2024().items(): lau.setdefault(g, {})["2024"] = v
    merge = json.load(open(os.path.join(IN, "belgium", "be_mergers_2025.json")))
    old_of = {}
    for o, n in merge.items(): old_of.setdefault(n, []).append(o)
    bc = json.load(open(os.path.join(IN, "border_changes.json"), encoding="utf-8"))
    mtexts = {}
    for name, (cc, conv) in LAU.items():
        out = {}
        # Mergers (borders.py): a merged municipality's years before the merger are its former ones added up.
        sub = {g: s for g, s in lau.items() if g.startswith(cc + "_")}
        if bc.get(name, {}).get("mergers"):
            drop_years(name, sub)   # a year in thousands or carried forward isn't added up
        tx = borders.merge_back(sub, bc.get(name, {}).get("mergers", []))
        lau.update(sub)
        if cc == "PL":   # Statistics Poland's 12-digit unit ID, less its last digit, is the end of the GISCO_ID
            tail = {g[5:]: g for g in lau if g.startswith("PL_")}
            conv = lambda i: tail.get(i.split("-", 1)[1][:-1])
        for i in ids(name):
            g = conv(i)
            s = dict(lau.get(g, {})) if g else {}
            if cc == "BE" and old_of.get(i.split("-", 1)[1]):   # merged in 2025: its former municipalities added up
                parts = ["BE_" + o for o in old_of[i.split("-", 1)[1]]] + ([g] if g in lau else [])
                years = set.intersection(*[set(lau.get(x, {})) for x in parts])
                s = {y: sum(lau[x][y] for x in parts) for y in years}
            s = {y: v for y, v in s.items() if v > 0}
            if len(s) > 1: out[i] = s
            if g in tx: mtexts.setdefault(name, {})[i] = tx[g]
        res[name] = out
    # Germany and Switzerland: NUTS 3
    d = json.load(open(os.path.join(raw, "es_pop_nuts3_all.json")))
    gi, ti = d["dimension"]["geo"]["category"]["index"], d["dimension"]["time"]["category"]["index"]
    val = lambda g, t: d["value"].get(str(gi[g] * len(ti) + ti[t]))
    nuts = {g: {t: int(val(g, t)) for t in ti if val(g, t) is not None} for g in gi}
    res["germany"] = {i: nuts[i.split("-", 1)[1]] for i in ids("germany") if len(nuts.get(i.split("-", 1)[1], {})) > 1}
    res["switzerland"] = {i: nuts[CH[i.split("-", 1)[1]]] for i in ids("switzerland") if CH.get(i.split("-", 1)[1]) in nuts}
    # UK: the local authority files (two boundary sets; the later one wins)
    uk = {}
    for f in sorted(glob.glob(os.path.join(raw, "uk_nomis_TYPE*.csv"))):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if r["OBS_VALUE"]: uk.setdefault(r["GEOGRAPHY_CODE"], {})[r["DATE_NAME"]] = int(float(r["OBS_VALUE"]))
    res["uk"] = {i: uk[i.split("-", 1)[1]] for i in ids("uk") if len(uk.get(i.split("-", 1)[1], {})) > 1}
    # Japan: census years
    jp = {}
    for x in json.load(open(os.path.join(raw, "jp_ssds_A1101.json"))):
        if x["v"] not in (None, "", "-", "…") and re.fullmatch(r"\d+", str(x["v"])): jp.setdefault(x["area"], {})[x["time"][:4]] = int(x["v"])
    res["japan"] = {i: jp[i.split("-", 1)[1]] for i in ids("japan") if len(jp.get(i.split("-", 1)[1], {})) > 1}
    # Australia: ERP by LGA, persons, all ages
    au = {}
    for r in csv.DictReader(gzip.open(os.path.join(raw, "au_ABS_ANNUAL_ERP_LGA2024.csv.gz"), "rt", encoding="utf-8-sig")):
        if r["REGION_TYPE"] == "LGA2024" and r["SEX_ABS"] == "3" and r["AGE"] == "TOT" and r["OBS_VALUE"]:
            au.setdefault(r["LGA_2024"], {})[r["TIME_PERIOD"]] = int(float(r["OBS_VALUE"]))
    res["australia"] = {i: au[i.split("-", 1)[1]] for i in ids("australia") if len(au.get(i.split("-", 1)[1], {})) > 1}
    # Argentina: province projections (sheets "06-BUENOS AIRES" ...), to the current year
    import datetime, xlrd
    b = xlrd.open_workbook(os.path.join(raw, "ar_proy_prov.xls"))
    ar = {}
    for sh in b.sheets():
        m = re.match(r"(\d\d)-", sh.name)
        if not m or m.group(1) == "01": continue
        for i in range(sh.nrows):
            r = sh.row_values(i)
            if isinstance(r[0], float) and 2010 <= r[0] <= datetime.date.today().year and isinstance(r[1], float):
                ar.setdefault(m.group(1), {})[str(int(r[0]))] = int(r[1])
    res["argentina"] = {i: ar[i.split("-", 1)[1]] for i in ids("argentina") if i.split("-", 1)[1] in ar}
    # Colombia: municipal (back-)projections 2005-2017 and projections 2018-2042 (two areas per municipality, added up)
    import datetime, openpyxl
    co = {}
    for f in glob.glob(os.path.join(raw, "co_*Mun-*.xlsx")):
        if "sexo" in f.lower(): continue
        for ws in openpyxl.load_workbook(f, read_only=True).worksheets:
            h = None
            for r in ws.iter_rows(values_only=True):
                if h is None:
                    if r and "MPIO" in r and "AÑO" in r: h = {str(c): k for k, c in enumerate(r) if c}
                    continue
                if not r or not isinstance(r[h["AÑO"]], (int, float)): continue
                area = str(r[h["ÁREA GEOGRÁFICA"]]).strip(); y = int(r[h["AÑO"]])
                v = r[h.get("Población", h.get("TOTAL"))]
                if area == "Total" or not isinstance(v, (int, float)) or not 2005 <= y <= datetime.date.today().year: continue
                m = str(r[h["MPIO"]]).zfill(5)
                co.setdefault(m, {}).setdefault(str(y), 0); co[m][str(y)] += int(v)
    res["colombia"] = {i: co[i.split("-", 1)[1]] for i in ids("colombia") if len(co.get(i.split("-", 1)[1], {})) > 1}
    # Brazil: IBGE's estimates for 1 July (SIDRA table 6579; none in the census years 2007, 2010 and 2022)
    br = json.load(open(os.path.join(raw, "br_pop_estimates.json")))
    res["brazil"] = {i: {y: int(v) for y, v in br[i.split("-", 1)[1]].items() if str(v).isdigit()} for i in ids("brazil") if i.split("-", 1)[1] in br}
    # Mexico: CONAPO's reconstruction 1990-2020 and projections 2021-2040, mid-year, men and women added up, to the current year
    mz = glob.glob(os.path.join(raw, "mx_00_Republica_mexicana.zip*"))
    if mz:
        import io, zipfile
        b = gzip.open(mz[0]).read() if mz[0].endswith(".gz") else open(mz[0], "rb").read()
        z = zipfile.ZipFile(io.BytesIO(b))
        ws = openpyxl.load_workbook(io.BytesIO(z.read(next(n for n in z.namelist() if "2_Gran_Gedad" in n))), read_only=True).worksheets[0]
        ws.reset_dimensions()
        mx = {}
        for r in ws.iter_rows(min_row=2, values_only=True):
            if r and isinstance(r[5], int) and r[5] <= datetime.date.today().year and isinstance(r[10], (int, float)):
                c = str(r[0]).zfill(5); mx.setdefault(c, {}); mx[c][str(r[5])] = mx[c].get(str(r[5]), 0) + int(r[10])
        res["mexico"] = {i: mx[i.split("-", 1)[1]] for i in ids("mexico") if len(mx.get(i.split("-", 1)[1], {})) > 1}
    # Border changes (borders.py): a split's parents keep their own years (their drop isn't a break to cut at), and
    # each family is added up on the borders before the split.
    for name in list(res):
        splits = [tuple(e) for e in bc.get(name, {}).get("splits", [])]
        keep = {}
        for p, c, F in splits: keep.setdefault(p, set()).add(F)
        res[name] = clean(name, res[name], keep)
        if splits:
            names = {r["District ID"]: r["District"] for r in csv.DictReader(open(os.path.join(DOCS, f"{name}.csv"), encoding="utf-8"))}
            eb = borders.earlier_borders(res[name], splits, lambda k: names.get(k, k))
            res.setdefault("_borders", {})[name] = {k: {"early": fs, "together": t, "changes": tx} for k, (fs, t, tx) in eb.items() if len(fs) > 1}
        for k, tx in mtexts.get(name, {}).items():
            if k in res[name]: res.setdefault("_borders", {}).setdefault(name, {}).setdefault(k, {"changes": []})["changes"] += tx
    json.dump(res, open(OUTF, "w"), separators=(",", ":"), sort_keys=True)
    for k, v in res.items():
        if not k.startswith("_"): print(f"{k}: {len(v)} of {len(ids(k))} places")


def clean(name, by, keep=None):
    """Drops what isn't a population series of the same place:
    - a year a country's file gives in thousands (GISCO's Finnish and most Italian figures for 2022-2023: the
      typical place is a thousandth of the year before), or that repeats the year before for most places (GISCO
      carries a figure forward where the country sent none);
    - a place's years before its last break, a change of more than a quarter from one year to the next (two years
      apart at most), which in these files is a boundary change: a merger, a split, or a code reused;
    - a place whose latest figure is more than a quarter off the site's own population (a different place behind the
      same code).
    keep: place -> years of known splits, where a break is the place losing land and its earlier years stay."""
    drop_years(name, by)
    site = {r["District ID"]: r for r in csv.DictReader(open(os.path.join(DOCS, f"{name}.csv"), encoding="utf-8"))}
    out = {}
    for i, s in by.items():
        ys = sorted(s)
        start = 0
        for k in range(1, len(ys)):
            if int(ys[k]) - int(ys[k - 1]) <= 2 and min(s[ys[k]], s[ys[k - 1]]) > 200 and abs(s[ys[k]] / s[ys[k - 1]] - 1) > 0.25 \
                    and ys[k] not in (keep or {}).get(i, ()): start = k
        s = {y: s[y] for y in ys[start:]}
        try: p = float(site.get(i, {}).get("Population") or 0)
        except ValueError: p = 0
        if p > 1000 and abs(s[max(s)] / p - 1) > 0.25: continue
        if len(s) > 1: out[i] = s
    return out


def drop_years(name, by):
    """A year a country's file gives in thousands, or carries forward from the year before, comes out (see clean)."""
    import statistics
    years = sorted({y for s in by.values() for y in s})
    kept = years[:1]
    for b in years[1:]:   # each year against the last one kept
        a = kept[-1]
        r = [s[b] / s[a] for s in by.values() if s.get(a, 0) > 0 and b in s]
        same = sum(1 for x in r if x == 1) / len(r) if r else 0
        if r and (not 0.01 < statistics.median(r) < 100 or same > 0.3):
            for s in by.values(): s.pop(b, None)
            print(f"  {name}: {b} dropped (" + (f"{same:.0%} of places unchanged from {a}: the earlier figure carried forward" if same > 0.3 else f"median ratio {statistics.median(r):.4f} to {a}") + ")")
        else: kept.append(b)


def apply():
    res = json.load(open(OUTF))
    bord = res.pop("_borders", {})
    for name, by in res.items():
        p = os.path.join(DOCS, f"{name}.csv")
        text = open(p, encoding="utf-8", newline="").read()
        rows = list(csv.DictReader(text.splitlines()))
        f = list(rows[0].keys())
        if COL in f and name not in res: continue
        if COL not in f: f.insert(f.index("Population") + 1 if "Population" in f else len(f), COL)
        b = bord.get(name, {})
        EB = COL + " (earlier borders)"
        hasE = any(x.get("early") for x in b.values())
        for c in (((EB, "Earlier borders") if hasE else ()) + ((borders.COL,) if b else ())):
            if c not in f: f.insert(f.index(COL) + 1 if c == EB else len(f) - (1 if f[-1] == "District ID" else 0), c)
        for r in rows:
            s = by.get(r["District ID"])
            r[COL] = "; ".join(f"{y}: {v}" for y, v in sorted(s.items())) if s else ""
            x = b.get(r["District ID"])
            if hasE: r[EB] = "; ".join(f"{y}: {v}" for y, v in sorted(x["early"].items())) if x and x.get("early") else ""
            if x:
                if x.get("together"): r["Earlier borders"] = r.get("Earlier borders") or x["together"]
                r[borders.COL] = borders.add_texts(r.get(borders.COL) if name in borders.BUILD_WRITES else "", x["changes"])
            elif b and name not in borders.BUILD_WRITES: r[borders.COL] = ""
        nl = "\r\n" if "\r\n" in text[:5000] else "\n"
        with open(p, "w", encoding="utf-8", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=f, lineterminator=nl); w.writeheader(); w.writerows(rows)
        print(f"{name}: {sum(1 for r in rows if r[COL])} of {len(rows)}")


if __name__ == "__main__":
    prep(sys.argv[2]) if sys.argv[1] == "prep" else apply()
