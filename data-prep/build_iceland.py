"""Build docs/data/iceland.csv and docs/data/map/iceland.json: Iceland's municipalities.

Iceland's municipalities (sveitarfélög) run its compulsory schools (grunnskólar, ages 6-15). Their
education committees (fræðsluráð, skólanefnd) meet in private, but many councils (bæjarstjórn,
sveitarstjórn, borgarstjórn), where school matters come up, stream their meetings.
- Borders: Eurostat GISCO LAU 2023 (its names are wrong for eight municipalities, e.g. 1000 Kópavogsbær is
  labelled "Λευκωσία", so names come from Statistics Iceland's municipality codes), merged to the 2026 municipalities (Skagabyggð into Húnabyggð and
  Tálknafjarðarhreppur into Vesturbyggð, 2024).
- Children 6-15 and population: Statistics Iceland MAN02005, 1 January 2026.
- Poverty: no local child rate is published, so every municipality shows Iceland's national rate of
  children under 18 below 60% of the median income (Eurostat ilc_li02, latest year). Statistics
  Iceland's split by residence (LIF01140) isn't used: its "total" row is higher than both parts.
- Meetings: council meetings on the municipality's own YouTube channel (data-prep/nordic_youtube.py,
  country IS), counted once per meeting (parts and continuations together).
- Enrollment: pupils by school, autumn 2025 (Statistics Iceland SKO02102), added up by the municipality each
  school is in (SCHOOLS below, checked by hand; the table lists schools in municipality-number order). Schools whose
  figure isn't published ("."), closed schools and the online school Ásgarður (whose municipality isn't given) are left out.
- Locale (estimated): population over area: urban 2,000+ per km², suburban 500-2,000, mixed 100-500, rural under 100.
Usage: python3 data-prep/build_iceland.py
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2
from meeting_dates import summary as date_summary

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "iceland")
DOCS = os.path.join(HERE, "..", "docs", "data")
MERGED = {"5611": "5613", "4607": "4604"}   # Skagabyggð into Húnabyggð; Vesturbyggð and Tálknafjarðarhreppur merged (2024) under code 4604
NOT_COUNCIL = {"Kvikmyndafjelag Borgarfjarðar"}   # a film society the search matched for Borgarbyggð
PER_ITEM = {"Bæjarstjórn Akureyrar"}   # Akureyri posts each agenda item as its own clip
NOT_MEETING = re.compile(r"kynningarfund|kosning|íbúafund|aætlun um fundi|áætlun um fundi", re.I)
COUNCIL = re.compile(r"b[æa]jarstj[óo]rn|borgarstj[óo]rn|sveitarstj[óo]rn|hreppsnefnd", re.I)


SCHOOLS = {   # municipality code: compulsory schools in it, as named in SKO02102
    "0000": "Austurbæjarskóli|Álftamýrarskóli|Árbæjarskóli|Ártúnsskóli|Barnaskóli Hjallastefnunnar Reykjavík|Borgaskóli|Breiðagerðisskóli|Breiðholtsskóli|"
            "Brúarskóli|Dalskóli|Engjaskóli|Fellaskóli (Reykjavík)|Foldaskóli|Fossvogsskóli|Grandaskóli|Hagaskóli|Hamraskóli|Háteigsskóli|Hlíðaskóli|"
            "Hólabrekkuskóli|Húsaskóli|Hvassaleitisskóli|Ingunnarskóli|Klettaskóli|Klébergsskóli|Landakotsskóli|Langholtsskóli|Laugalækjarskóli|"
            "Laugarnesskóli|Melaskóli|Norðlingaskóli|Réttarholtsskóli|Rimaskóli|Selásskóli|Seljaskóli|Skóli Ísaks Jónssonar|Suðurhlíðarskóli|"
            "Sæmundarskóli|Tjarnarskóli|Vesturbæjarskóli|Víkurskóli (Reykjavík)|Vogaskóli|Waldorfskólinn Sólstafir|Ölduselsskóli",
    "1000": "Arnarskóli|Álfhólsskóli|Barnaskóli Kársness|Hörðuvallaskóli|Kársnesskóli|Kópavogsskóli|Kóraskóli|Lindaskóli|Salaskóli|Smáraskóli|"
            "Snælandsskóli|Vatnsendaskóli|Waldorfskólinn Lækjarbotnum",
    "1100": "Mýrarhúsaskóli|Valhúsaskóli",
    "1300": "Alþjóðaskólinn á Íslandi|Álftanesskóli|Barnaskóli Hjallastefnunnar Garðabæ|Flataskóli|Garðaskóli|Hofsstaðaskóli|Sjálandsskóli|Urriðaholtsskóli",
    "1400": "Áslandsskóli|Barnaskóli Hjallastefnunnar Hafnarfirði|Engidalsskóli|Hraunvallaskóli|Hvaleyrarskóli|Lækjarskóli|NÚ|Setbergsskóli|"
            "Skarðshlíðarskóli|Víðistaðaskóli|Öldutúnsskóli",
    "1604": "Helgafellsskóli|Krikaskóli|Kvíslarskóli|Lágafellsskóli|Varmárskóli",
    "2000": "Akurskóli|Háaleitisskóli (Reykjanesbæ)|Heiðarskóli (Reykjanesbæ)|Holtaskóli|Myllubakkaskóli|Njarðvíkurskóli|Stapaskóli",
    "2506": "Stóru-Vogaskóli", "2510": "Gerðaskóli|Sandgerðisskóli", "3000": "Brekkubæjarskóli|Grundaskóli",
    "3511": "Heiðarskóli (Hvalfjarðarsveit)", "3609": "Grunnskóli Borgarfjarðar|Grunnskólinn í Borgarnesi", "3709": "Grunnskóli Grundarfjarðar",
    "3714": "Grunnskóli Snæfellsbæjar", "3716": "Grunnskólinn í Stykkishólmi", "3811": "Auðarskóli", "4100": "Grunnskóli Bolungarvíkur",
    "4200": "Grunnskóli Önundarfjarðar|Grunnskólinn á Ísafirði|Grunnskólinn á Suðureyri|Grunnskólinn Þingeyri", "4502": "Reykhólaskóli",
    "4604": "Bíldudalsskóli|Patreksskóli|Tálknafjarðarskóli", "4803": "Súðavíkurskóli", "4902": "Grunnskóli Drangsness",
    "4911": "Grunnskólinn á Hólmavík", "5508": "Grunnskóli Húnaþings vestra", "5609": "Höfðaskóli", "5613": "Húnaskóli",
    "5716": "Árskóli|Grunnskólinn austan Vatna|Varmahlíðarskóli",
    "6000": "Brekkuskóli|Giljaskóli|Glerárskóli|Hlíðarskóli|Hríseyjarskóli|Lundarskóli|Naustaskóli|Oddeyrarskóli|Síðuskóli",
    "6100": "Borgarhólsskóli|Öxarfjarðarskóli", "6250": "Grunnskóli Fjallabyggðar", "6400": "Árskógarskóli|Dalvíkurskóli",
    "6513": "Hrafnagilsskóli", "6515": "Þelamerkurskóli", "6601": "Valsárskóli", "6602": "Grenivíkurskóli",
    "6613": "Reykjahlíðarskóli|Stórutjarnaskóli|Þingeyjarskóli", "6710": "Grunnskólinn á Þórshöfn",
    "7300": "Breiðdals- og Stöðvarfjarðarskóli|Eskifjarðarskóli|Grunnskóli Fáskrúðsfjarðar|Grunnskóli Reyðarfjarðar|Nesskóli",
    "7400": "Brúarásskóli|Djúpavogsskóli|Egilsstaðaskóli|Fellaskóli (Fellabæ)|Seyðisfjarðarskóli", "7502": "Vopnafjarðarskóli",
    "8000": "Grunnskóli Vestmannaeyja", "8200": "Barnaskólinn á Eyrarbakka og Stokkseyri|Stekkjaskóli|Sunnulækjarskóli|Vallaskóli",
    "8401": "Grunnskóli Hornafjarðar|Grunnskólinn í Hofgarði", "8508": "Víkurskóli (Vík í Mýrdal)", "8509": "Kirkjubæjarskóli",
    "8613": "Hvolsskóli", "8614": "Grunnskólinn Hellu|Laugalandsskóli í Holtum", "8710": "Flúðaskóli", "8716": "Grunnskólinn í Hveragerði",
    "8717": "Grunnskólinn í Þorlákshöfn", "8719": "Kerhólsskóli", "8720": "Þjórsárskóli", "8721": "Bláskógaskóli Laugarvatni|Reykholtsskóli",
    "8722": "Flóaskóli",
}


def pupils():
    rows = list(csv.reader(open(os.path.join(IN, "is_SKO02102_pupils_by_school_2025.csv"), encoding="utf-8-sig")))
    n = {r[0]: int(r[1]) for r in rows[1:] if r[1].strip().isdigit()}
    out, seen = {}, set()
    for code, names in SCHOOLS.items():
        for s in names.split("|"):
            assert s in n, s
            out[code] = out.get(code, 0) + n[s]; seen.add(s)
    left = sorted(set(n) - seen - {"Alls", "Ásgarður"})
    assert not left, left
    return out, rows[0][1].split()[0]


def meeting_key(t):
    """One key per meeting: its number ("402. fundur", "nr. 865") or date, else the title without part markers."""
    m = re.search(r"(?:nr\.?\s*|^)(\d{2,4})\.?\s*fund", t, re.I) or re.search(r"fundur\s+nr\.?\s*(\d+)", t, re.I) or re.search(r"\bnr\.?\s*(\d+)", t, re.I)
    if m: return "n" + m.group(1)
    m = re.search(r"(\d{1,2})[. ]+(\w+|\d{1,2})[. ]+(\d{4})", t)
    if m: return "d" + "-".join(m.groups()).lower()
    return re.sub(r"\(?\d/\d\)?|\bhluti\b|\bframhald\b|-|–", "", t, flags=re.I).strip().lower()


def main():
    geo = json.load(open(os.path.join(IN, "lau_IS.geojson"), encoding="utf-8"))
    pop = json.load(open(os.path.join(IN, "is_pop.json"), encoding="utf-8"))
    ids, size = pop["id"], pop["size"]; cat = {k: list(pop["dimension"][k]["category"]["index"]) for k in ids}
    lab = pop["dimension"]["Sveitarfélag"]["category"]["label"]; alab = pop["dimension"]["Aldur"]["category"]["label"]
    def pv(m, a):
        sel = {k: cat[k][0] for k in ids}; sel.update({"Sveitarfélag": m, "Aldur": a}); i = 0
        for k, n in zip(ids, size): i = i * n + cat[k].index(sel[k])
        return pop["value"][i] or 0
    year = cat["Ár"][0]
    people = {m: (pv(m, "-1"), sum(pv(m, a) for a in cat["Aldur"] if a != "-1")) for m in cat["Sveitarfélag"] if lab[m] != "Alls"}
    es = json.load(open(os.path.join(IN, "es_is_child.json")))
    eids, esz = es["id"], es["size"]; ecat = {k: list(es["dimension"][k]["category"]["index"]) for k in eids}
    def ev(t):
        sel = dict(freq="A", statinfo="MED_EI", unit="PC", rskpovth="B_60", sex="T", age="Y_LT18", geo="IS", time=t); i = 0
        for k, n in zip(eids, esz): i = i * n + ecat[k].index(sel[k])
        return es["value"].get(str(i))
    ty = max(t for t in ecat["time"] if ev(t) is not None); rate = ev(ty)
    yt = {}
    for f in ("IS_youtube.csv", "IS_youtube_rerun.csv"):   # the rerun (correct names, more queries) wins where it found a channel
        p = os.path.join(IN, "youtube", f)
        if os.path.exists(p):
            for r in csv.DictReader(open(p, encoding="utf-8")):
                if r["Channel"] or r["District ID"] not in yt: yt[r["District ID"]] = r
    titles = {}
    for f in ("titles.json", "titles_rerun.json"):
        p = os.path.join(IN, "youtube", f)
        if os.path.exists(p): titles.update(json.load(open(p, encoding="utf-8")))
    from shared_titles import shared_titles
    titles.update(shared_titles())
    shapes, ids_of = {}, {}
    for f in geo["features"]:
        lid = MERGED.get(f["properties"]["LAU_ID"], f["properties"]["LAU_ID"])
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        shapes.setdefault(lid, []).extend(polys)
    rows, feats = [], []
    enr, enr_year = pupils()
    for lid, polys in sorted(shapes.items(), key=lambda x: lab[x[0]]):
        name = lab[lid]; gm = {"type": "MultiPolygon", "coordinates": polys}
        tot, kids = people.get(lid, (0, 0))
        dens = tot / area_km2(gm) if tot else 0
        r = yt.get(f"IS-{lid}") or {}
        url = "" if r.get("Channel") in NOT_COUNCIL else r.get("Channel URL", "")
        vids = titles.get(url, [])
        council = [t for t in vids if COUNCIL.search(t) and re.search(r"fund", t, re.I) and not NOT_MEETING.search(t)]
        n = len({meeting_key(t) for t in council})
        if r.get("Channel") in PER_ITEM:   # one clip per agenda item, numbered from 1 in each meeting
            n = sum(1 for t in vids if re.match(r"\s*1\s{2,}\S", t))
        rows.append({"District": name, "Locale": "Urban" if dens >= 2000 else "Suburban" if dens >= 500 else "Mixed" if dens >= 100 else "Rural",
                     "Available Board Meetings": n, "Meetings source": url,
                     **dict(zip(("Latest meeting", "Meetings by year"), date_summary(council) if n else ("", ""))),
                     "Population": tot, "Children": kids, "Enrollment": enr.get(lid, ""), "Enrollment year": f"Autumn {enr_year}" if lid in enr else "", "Percentage of Children in Low Income": f"{rate:.2f}%",
                     "Poverty note": f"Iceland's national rate, {ty} (Eurostat); no local child rate is published",
                     "People per km² (estimated)": round(dens), "District ID": f"IS-{lid}"})
        rnd = lambda c: [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]
        feats.append({"type": "Feature", "properties": {"id": f"IS-{lid}", "NAME": name}, "geometry": {"type": "MultiPolygon", "coordinates": rnd(polys)}})
    miss = [r["District"] for r in rows if not r["Population"]]
    assert not miss, miss
    with open(os.path.join(DOCS, "iceland.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", "iceland.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(len(rows), "municipalities; children", sum(r["Children"] for r in rows), f"({year}); meetings for", sum(1 for r in rows if r["Available Board Meetings"]))
    for r in rows:
        if r["Available Board Meetings"]: print("  ", r["District"], r["Available Board Meetings"])


if __name__ == "__main__":
    main()
