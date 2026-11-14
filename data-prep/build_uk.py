"""Build docs/data/uk.csv and docs/data/map/uk.json: one row per UK education authority.

England: the 153 upper-tier councils (counties, unitary authorities, metropolitan and London
boroughs). Scotland: 32 councils. Wales: 22 councils. Northern Ireland: one Education Authority.
- Child poverty: DWP, Children in Low Income Families (relative low income before housing
  costs, children under 16), financial year ending 2025. England's 21 two-tier counties add up
  their districts (ONS lookup); Northern Ireland adds up its 11 districts.
- Public-school share (England only): state-funded pupils against independent schools' pupils in the same local
  authority (Get Information about Schools, full extract, November 2026).
- Enrollment: England, Get Information about Schools (open state-funded schools); Scotland,
  pupil census 2025 (Table 5.2); Wales, schools' census January 2025 (Table 5); Northern
  Ireland, school census October 2025 (primary 164,713 + post-primary 156,766 + special 7,729).
- Borders: ONS Counties and Unitary Authorities (December 2024), UK, BUC.
Inputs are in data-prep/inputs/uk/. Usage: python3 data-prep/build_uk.py
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "uk")
OUT_CSV = os.path.join(HERE, "..", "docs", "data", "uk.csv")
OUT_MAP = os.path.join(HERE, "..", "docs", "data", "map", "uk.json")
NI_PUPILS = 164713 + 156766 + 7729
NATION = {"E": "England", "S": "Scotland", "W": "Wales", "N": "Northern Ireland"}
num = lambda v: float(str(v).replace(",", "")) if str(v).strip() not in ("", "nan", "[x]", "[c]", "[z]") else None
norm = lambda s: re.sub(r"[^a-z]", "", re.sub(r"^the ", "", s.lower()).replace("&", "and").replace(", city of", "").replace("city of ", "").replace("county of ", ""))


def main():
    rows = list(csv.reader(open(os.path.join(IN, "dwp_cilif_bhc_relative_la_fye2022_2025.csv"), encoding="utf-8")))
    head = next(i for i, r in enumerate(rows) if r and r[1] == "Area Code")
    cols = [c.replace("\n", " ") for c in rows[head]]
    ni_, pi_ = cols.index("Number of children  FYE 2025"), next(i for i, c in enumerate(cols) if c.startswith("Percentage of children  FYE 2025"))
    pov = {}   # code -> (children in low income, all children)
    for r in rows[head + 1:]:
        if len(r) > pi_ and r[1] and num(r[ni_]) and num(r[pi_]):
            n, p = num(r[ni_]), num(r[pi_])
            pov[r[1]] = (n, n / p)
    lookup = {r["LAD24CD"]: r["CTYUA24CD"] for r in csv.DictReader(open(os.path.join(IN, "ons_lad24_ctyua24_lookup.csv")))}
    # Every year in the table (FYE 2022-2025), added up the same way, for "Poverty by year".
    hist = {}
    for fy in ("2022", "2023", "2024", "2025"):
        nc, pc = cols.index(f"Number of children  FYE {fy}"), next(i for i, c in enumerate(cols) if c.startswith(f"Percentage of children  FYE {fy}"))
        yr = {}
        for r in rows[head + 1:]:
            if len(r) > pc and r[1] and num(r[nc]) and num(r[pc]):
                n, k = num(r[nc]), num(r[nc]) / num(r[pc])
                for key in {r[1], lookup.get(r[1]) if r[1].startswith("E07") else None, "N-EA" if r[1].startswith("N09") else None} - {None}:
                    a = yr.setdefault(key, [0, 0]); a[0] += n; a[1] += k
        for key, (n, k) in yr.items():
            hist.setdefault(key, {})[fy] = round(100 * n / k, 2)
    agg = {}
    for code, (n, k) in pov.items():
        if code.startswith("E07"):
            cty = lookup.get(code)
            if cty:
                a = agg.setdefault(cty, [0, 0]); a[0] += n; a[1] += k
        if code.startswith("N09"):
            a = agg.setdefault("N-EA", [0, 0]); a[0] += n; a[1] += k
    pov.update({k: tuple(v) for k, v in agg.items()})
    geo = json.load(open(os.path.join(IN, "ons_ctyua_dec2024_buc.geojson")))
    eng = {norm(r["LA (name)"]): float(r["NumberOfPupils"]) for r in csv.DictReader(open(os.path.join(IN, "england_gias_pupils_by_la_20261104.csv")))}
    # England's independent schools' pupils by local authority (Get Information about Schools, full extract), for the
    # share of pupils in public (state-funded) schools; Scotland, Wales and Northern Ireland have no figure here.
    gp = os.path.join(IN, "england_gias_pupils_by_la_group_20261113.json")
    indep = {norm(k): v.get("Independent schools", 0) for k, v in json.load(open(gp))["by_la"].items()} if os.path.exists(gp) else {}
    sco = {norm(r["Local Authority"]): float(r["Pupils 2025"]) for r in csv.DictReader(open(os.path.join(IN, "scotland_pupil_census_2025_table5_2.csv")))}
    wr = list(csv.reader(open(os.path.join(IN, "wales_census_2025_table5.csv"), encoding="utf-8")))
    wh = next(i for i, r in enumerate(wr) if r and r[0] == "Local authority")
    wal = {norm(r[0]): num(r[wr[wh].index("All pupils - total")]) for r in wr[wh + 1:] if r and r[0] and num(r[wr[wh].index("All pupils - total")])}
    out, feats, seen = [], [], set()
    for f in geo["features"]:
        p = f["properties"]
        code, name = p["CTYUA24CD"], p["CTYUA24NM"]
        nat = NATION[code[0]]
        rid = "N-EA" if code.startswith("N09") else code
        feats.append({"type": "Feature", "properties": {"id": "UK-" + rid, "NAME": name}, "geometry": f["geometry"]})
        if rid in seen:
            continue
        seen.add(rid)
        if rid == "N-EA":
            name, enr, ey = "Education Authority (Northern Ireland)", NI_PUPILS, "October 2025"
        elif nat == "England":
            enr, ey = eng.get(norm(name)), "January 2026 (register)"
        elif nat == "Scotland":
            enr, ey = sco.get(norm(name)) or sco.get(norm(name.replace("and", "&"))), "September 2025"
        else:
            enr, ey = wal.get(norm(name)), "January 2025"
        n, k = pov.get(rid, (None, None))
        out.append({"District": name, "Nation": nat, "Available Board Meetings": 0, "Meetings source": "",
                    "Children Under 16": round(k) if k else "", "Children Under 16 in Low Income": round(n) if n else "",
                    "Percentage of Children Under 16 in Low Income": f"{100 * n / k:.2f}%" if k else "",
                    "Poverty by year": "; ".join(f"{y}:{v}" for y, v in sorted(hist.get(rid, {}).items())),
                    "Enrollment": round(enr) if enr else "", "Enrollment year": ey if enr else "",
                    "Public school enrollment": round(enr) if enr and nat == "England" and norm(name) in indep else "",
                    "Private school enrollment (within its borders)": round(indep[norm(name)]) if enr and nat == "England" and norm(name) in indep else "",
                    "District ID": "UK-" + rid})
    # Meetings: council committee meetings on YouTube (data-prep/uk_youtube.py), with hand-checked fixes
    yt = {r["District ID"]: r for r in csv.DictReader(open(os.path.join(IN, "uk_youtube.csv"), encoding="utf-8"))} if os.path.exists(os.path.join(IN, "uk_youtube.csv")) else {}
    bad = {r["District"] for r in csv.DictReader(open(os.path.join(IN, "uk_channels.csv"), encoding="utf-8"))} if os.path.exists(os.path.join(IN, "uk_channels.csv")) else set()
    from shared_titles import shared_titles
    from meeting_dates import summary as date_summary
    import uk_youtube as ukt
    fresh = shared_titles()
    for r in out:
        y = yt.get(r["District ID"], {})
        url = y.get("Channel URL", "")
        n, kept = (int(y.get("Meetings") or 0), []) if r["District"] not in bad else (0, [])
        if n and url in fresh:   # recount from the monthly refresh, with uk_youtube.py's rules
            vids = fresh[url]
            kept = [v for v in vids if re.search(r"board", v, re.I) and ukt.MEET.search(v)] if "Education Authority" in r["District"] \
                else [v for v in vids if ukt.EDU.search(v) and ukt.MEET.search(v)]
            n = len({re.sub(r"\b(part|pt)\s*\d+\b|\(\d\)", "", v, flags=re.I).strip().lower() for v in kept})
        r["Available Board Meetings"] = n
        r["Meetings source"] = url if n else ""
        r["Latest meeting"], r["Meetings by year"] = date_summary(kept) if n else ("", "")
    # Other meetings: the council's education and children's committee meetings listed in its ModernGov committee
    # system (public web service GetCommittees / GetMeetings), 2010 to the collection date. These are listed meetings,
    # not recordings, so they go in their own column. Committees that aren't councillors' meetings about children's
    # services and schools (schools forums, SACREs, appeals, admissions, partnerships, single-member decision days) are
    # left out, and so are two councils matched to another body's site (Hull to Kingston upon Thames's, the City of
    # London to the Greater London Authority's).
    mg_path = os.path.join(IN, "uk_moderngov_committees.json")
    mg = json.load(open(mg_path, encoding="utf-8")) if os.path.exists(mg_path) else {}
    import datetime
    YES = re.compile(r"children|education|schools?\b|young people|learning|families", re.I)
    KIND = re.compile(r"committee|scrutiny|panel|board|cabinet|sub-?group|executive|commission|^education$", re.I)
    NO = re.compile(r"forum|sacre|religious|appeal|admission|placement|partnership|trust|working group|training|joint consultative|advisory|"
                    r"corporate parent|in care council|adoption|fostering|building schools|employment|skills board|safeguarding (children )?(partnership|board)|"
                    r"health and wellbeing|music|governor|transport|cabinet member|portfolio|decision day|executive member|lead member|deputy mayor|"
                    r"licensing|planning|standards|pension|youth offending|staff|employ|appointment|personnel|joint negotiating|disabilit", re.I)
    WRONG_SITE = {"UK-E06000010", "UK-E09000001"}
    collected = datetime.date(2026, 11, 6)
    for r in out:
        v = mg.get(r["District ID"]) or {}
        if not v.get("host") or r["District ID"] in WRONG_SITE: continue
        dates = set()
        for c in v["committees"]:
            if not (YES.search(c["title"]) and KIND.search(c["title"])) or NO.search(c["title"]): continue
            for m in c.get("meetings") or []:
                try:
                    dd, mm, yy = map(int, m.split()[0].split("/")); x = datetime.date(yy, mm, dd)
                except ValueError:
                    continue
                if x <= collected: dates.add(x)
        if dates:
            r["Other Board Meetings"] = len(dates)
            r["Other meetings source"] = f"education and children's committee meetings listed on the council's committee site ({v['host']}), 2010 to November 2026"
            if not r.get("Latest meeting"):
                r["Latest meeting"] = max(dates).isoformat()
                r["Meetings by year"] = "; ".join(f"{y}:{n}" for y, n in sorted(__import__("collections").Counter(x.year for x in dates).items()))
    out.sort(key=lambda r: (r["Nation"], r["District"]))
    # Estimated locale from population density: people = children / 0.185 (their share of the
    # population), over land area. Urban 2,000+ per km², suburban 500-2,000, mixed 100-500, rural under 100.
    area = {}
    for f in feats:
        area[f["properties"]["id"]] = area.get(f["properties"]["id"], 0) + area_km2(f["geometry"])
    for r in out:
        k = float(r["Children Under 16"] or 0)
        d = k / 0.185 / area[r["District ID"]] if area.get(r["District ID"]) else 0
        r["Locale"] = "Urban" if d >= 2000 else "Suburban" if d >= 500 else "Mixed" if d >= 100 else "Rural"
        r["People per km² (estimated)"] = round(d)
    path = OUT_CSV if "OUT_CSV" in globals() else os.path.join(HERE, "..", "docs", "data", "ireland.csv")
    data = out
    with open(path, "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(dict.fromkeys(k for r in data for k in r)), restval=""); w.writeheader(); w.writerows(data)
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]
    for f in feats:
        f["geometry"]["coordinates"] = rnd(f["geometry"]["coordinates"])
    json.dump({"type": "FeatureCollection", "features": feats}, open(OUT_MAP, "w"), separators=(",", ":"))
    miss = [r["District"] for r in out if not r["Percentage of Children Under 16 in Low Income"]]
    me = [r["District"] for r in out if not r["Enrollment"]]
    print(len(out), "authorities; no poverty:", miss, "; no enrollment:", me)


if __name__ == "__main__":
    main()
