"""Turns the Slovenia downloads (made on GitHub's runner) into the small inputs build_latam.slovenia() reads
(data-prep/inputs/slovenia/).

- svn_geo.geojson: the 212 municipalities (občine), from geoBoundaries gbOpen SVN ADM2 (simplified), matched by name.
- svn_data.json, per municipality (SURS code):
  pop, area: SURS 2640010S (selected data on municipalities), population and area on 1 January 2026;
  pupils: SURS 2640010S, basic-school pupils (by the school's municipality) plus upper-secondary pupils (by residence), 2025;
  children: population minus those aged 18 or more, SURS 05C4006S, latest half-year;
  net income per person and registered unemployment, where downloaded (SURS 0883206S, 0700960S), for the poverty stand-in;
  meetings: the municipal council's YouTube channel (fetch/nyt.py, SI).
Usage: python3 data-prep/prep_slovenia.py RAWDIR [RAWDIR ...] GEODIR
"""
import glob, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "slovenia")
key = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower())


def find(dirs, name):
    fs = sorted(f for d in dirs for f in glob.glob(os.path.join(d, "**", name), recursive=True))
    return fs[-1] if fs else None


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]


def jstat(path):
    d = json.load(open(path, encoding="utf-8"))
    ids, size = d["id"], d["size"]
    cats = {k: list(d["dimension"][k]["category"]["index"]) for k in ids}
    labels = {k: d["dimension"][k]["category"]["label"] for k in ids}
    def val(**sel):
        i = 0
        for k, n in zip(ids, size):
            i = i * n + (cats[k].index(sel[k]) if k in sel else 0)
        return d["value"][i]
    return cats, labels, val


def main(*args):
    *dirs, geo = args
    os.makedirs(OUT, exist_ok=True)
    cats, labels, val = jstat(find(dirs, "si_2640010S.json"))
    M = {labels["MERITVE"][m]: m for m in cats["MERITVE"]}
    latest = lambda m, o: next((val(MERITVE=M[m], OBČINE=o, LETO=y) for y in reversed(cats["LETO"]) if val(MERITVE=M[m], OBČINE=o, LETO=y) is not None), None)
    c2, l2, v2 = jstat(find(dirs, "si_05C4006S.json"))
    half = next(h for h in reversed(c2["POLLETJE"]) if v2(SPOL=c2["SPOL"][0], OBČINE=c2["OBČINE"][0], POLLETJE=h, STAROST="12") is not None)
    data = {}
    for o in cats["OBČINE"]:
        name = labels["OBČINE"][o]
        if name == "SLOVENIA": continue
        pop = latest("Population - Total - 1 January", o)
        adults = v2(SPOL=c2["SPOL"][0], OBČINE=o, POLLETJE=half, STAROST="12")
        data[o] = {"name": name, "pop": pop, "area": latest("Surface area (sq. km) - 1 January", o),
                   "basic": latest("Number of pupils", o), "upper": latest("Number of upper secondary school pupils (by residence)", o),
                   "children": pop - adults if pop and adults is not None else None, "half": l2["POLLETJE"][half]}
    # Poverty stand-in: parental, family and social benefits as a share of residents' net income (SURS 0883206S). Slovenia
    # publishes no poverty rate below its 12 statistical regions; these benefits are largely means-tested (the child
    # benefit, financial social assistance, the income support supplement), so their weight in income tracks need.
    f = find(dirs, "si_0883206S.json")
    if f:
        c3, l3, v3 = jstat(f)
        yr = l3["LETO"][c3["LETO"][-1]]
        mid = {l3["MERITVE"][k]: k for k in c3["MERITVE"]}; inc = {l3["NETO DOHODEK"][k]: k for k in c3["NETO DOHODEK"]}
        for o, x in data.items():
            g_ = lambda m, i: v3(MERITVE=mid[m], OBČINE=o, LETO=c3["LETO"][-1], **{"NETO DOHODEK": inc[i]})
            tot, ben, med = g_("Average per capita, net (EUR)", "Net income - TOTAL"), g_("Average per capita, net (EUR)", "Parental, family and social benefits"), g_("Median net income of the population (EUR)", "Net income - TOTAL")
            if tot and ben is not None:
                x["stand_in"] = 100 * ben / tot; x["income_pc"] = tot; x["income_median"] = med; x["income_year"] = yr
                x["stand_in_note"] = (f"Stand-in: parental, family and social benefits as a share of residents' net income, {yr} ({ben:,.0f} of {tot:,.0f} EUR per person; "
                                      f"SURS 0883206S). These benefits are largely means-tested; Slovenia publishes no poverty rate by municipality")
    # geoBoundaries' names lost Slovenian letters ("Ajdovtcina" for Ajdovščina, "Ltore" for Štore): exact matches first,
    # then the closest remaining spelling (all 212 pairs checked by hand).
    import difflib
    g = json.load(open(os.path.join(geo, "geoBoundaries-SVN-ADM2_simplified.geojson"), encoding="utf-8"))["features"]
    gk = {}
    for ft in g:
        for part in re.split(r"\s*/\s*", ft["properties"]["shapeName"]): gk.setdefault(key(part), ft)
    pairs, used = {}, set()
    for o, x in data.items():
        if o.startswith("_"): continue
        ft = next((gk[key(p)] for p in [x["name"]] + x["name"].split("/") if key(p) in gk), None)
        if ft: pairs[o] = ft; used.add(id(ft))
    left = [o for o in data if not o.startswith("_") and o not in pairs]
    cand = sorted(((difflib.SequenceMatcher(None, key(data[o]["name"].replace("Slov.", "Slovenskih")), key(ft["properties"]["shapeName"])).ratio(), o, i)
                   for o in left for i, ft in enumerate(g) if id(ft) not in used), reverse=True)
    for r, o, i in cand:
        if o in pairs or id(g[i]) in used or r < 0.5: continue
        pairs[o] = g[i]; used.add(id(g[i]))
    feats = [{"type": "Feature", "properties": {"id": "SVN-" + o, "NAME": data[o]["name"]}, "geometry": {"type": ft["geometry"]["type"], "coordinates": rnd(ft["geometry"]["coordinates"])}} for o, ft in pairs.items()]
    miss = [data[o]["name"] for o in data if not o.startswith("_") and o not in pairs]
    json.dump(data, open(os.path.join(OUT, "svn_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "svn_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(len(data), "municipalities;", len(feats), "borders; missing", miss)
    print(sum((x["basic"] or 0) + (x["upper"] or 0) for k, x in data.items() if not k.startswith("_")), sum(x["children"] or 0 for k, x in data.items() if not k.startswith("_")))


if __name__ == "__main__":
    main(*sys.argv[1:])
