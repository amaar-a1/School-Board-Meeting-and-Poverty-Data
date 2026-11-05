"""Build docs/data/germany.csv and docs/data/map/germany.json: Germany's 400 districts.

German schools are run jointly: each state (Land) employs the teachers and sets the curriculum, and
the districts (Landkreise) and district-free cities (kreisfreie Städte) are the school authorities
(Schulträger) for most secondary schools, with a school committee (Schulausschuss) of the council.
- Borders: Eurostat GISCO NUTS 2021 level 3 (= districts), 1:10m.
- Child poverty: Bertelsmann Stiftung, Wegweiser Kommune (CC0): share of children under 15 receiving
  basic income support (SGB II), 2023. Eisenach merged into the Wartburgkreis in 2021; the NUTS 2021
  border still shows it, with the Wartburgkreis figure.
- Children under 15 and density: Eurostat demo_r_pjanaggr3 and demo_r_d3dens (latest year).
- Meetings: recordings on the district's or city's own YouTube channel (data-prep/nordic_youtube.py,
  country DE; channels in inputs/germany/youtube/, wrong matches dropped in NOT_CHANNELS): sittings of
  its school committee (Schulausschuss, Bildungsausschuss) if any, otherwise of the council itself
  (Kreistag, Stadtrat, Bürgerschaft) as a stand-in, counted once per day.
- Locale (estimated): Eurostat's people per km²: urban 2,000+, suburban 500-2,000, mixed 100-500, rural under 100.
Usage: python3 data-prep/build_germany.py
"""
import csv, glob, io, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "germany")
DOCS = os.path.join(HERE, "..", "docs", "data")
LAND = {"DE1": "Baden-Württemberg", "DE2": "Bavaria", "DE3": "Berlin", "DE4": "Brandenburg", "DE5": "Bremen", "DE6": "Hamburg",
        "DE7": "Hesse", "DE8": "Mecklenburg-Vorpommern", "DE9": "Lower Saxony", "DEA": "North Rhine-Westphalia", "DEB": "Rhineland-Palatinate",
        "DEC": "Saarland", "DED": "Saxony", "DEE": "Saxony-Anhalt", "DEF": "Schleswig-Holstein", "DEG": "Thuringia"}
FIX = {"DE300": "Berlin", "DE600": "Hamburg", "DE233": "Weiden in der Oberpfalz", "DE277": "Dillingen an der Donau, LK",
       "DE236": "Neumarkt in der Oberpfalz, LK", "DE229": "Regen, LK"}


def eurostat(path, **fixed):
    d = json.load(open(os.path.join(IN, path)))
    ids, size = d["id"], d["size"]; cat = {k: list(d["dimension"][k]["category"]["index"]) for k in ids}
    out = {}
    for geo in cat["geo"]:
        for t in sorted(cat["time"], reverse=True):
            sel = {k: (fixed.get(k) or cat[k][0]) for k in ids}; sel.update(geo=geo, time=t); i = 0
            for k, s in zip(ids, size): i = i * s + cat[k].index(sel[k])
            v = d["value"].get(str(i))
            if v is not None:
                out[geo] = (v, t); break
    return out


SCHOOL = re.compile(r"(schul|bildungs)\w*ausschuss|ausschuss f[üu]r (schule|bildung)", re.I)
COUNCIL = re.compile(r"kreistag|stadtrat|stadtverordnet|gemeinderat|ratssitzung|b[üu]rgerschaft|abgeordnetenhaus|städteregionstag|regionsversammlung", re.I)
SITZ = re.compile(r"sitzung|\d{1,2}\.\s*\w+\s+20\d\d|\d{1,2}\.\d{1,2}\.\d{2,4}|live|übertragung", re.I)
NOT_T = re.compile(r"jugend|kinder|wahl|kandidat|interview|imagefilm|trailer|erklärt|bürgermeister(in)? im gespräch", re.I)
NOT_CHANNELS = set()   # channel names checked by hand and found wrong (filled after the search)


def meetings(k):
    """(count, channel URL, counted titles, kind) for NUTS id k."""
    import json as _j
    from meeting_dates import parse
    from shared_titles import shared_titles
    yd = os.path.join(IN, "youtube")
    rows = {r["District ID"]: r for r in csv.DictReader(open(os.path.join(yd, "DE_youtube.csv"), encoding="utf-8"))} if os.path.exists(os.path.join(yd, "DE_youtube.csv")) else {}
    titles = _j.load(open(os.path.join(yd, "titles.json"), encoding="utf-8")) if os.path.exists(os.path.join(yd, "titles.json")) else {}
    titles.update(shared_titles())
    r = rows.get(f"DE-{k}") or {}
    url = r.get("Channel URL", "")
    if not url or r.get("Channel") in NOT_CHANNELS or url not in titles:
        return 0, "", [], ""
    vids = [t for t in titles[url] if SITZ.search(t) and not NOT_T.search(t)]
    for rx, kind in ((SCHOOL, "School committee"), (COUNCIL, "Council (stand-in)")):
        keep = [t for t in vids if rx.search(t)]
        keys = {parse(t) or re.sub(r"\b(teil|part)\s*\d+\b|\(\d\)|\d/\d", "", t, flags=re.I).strip().lower() for t in keep}
        if keys: return len(keys), url, keep, kind
    return 0, "", [], ""


def meeting_cols(k):
    from meeting_dates import summary
    n, url, keep, kind = meetings(k)
    latest, years = summary(keep) if n else ("", "")
    return {"Available Board Meetings": n, "Meetings type": kind, "Meetings source": url, "Latest meeting": latest, "Meetings by year": years}


def main():
    search = json.load(open(os.path.join(IN, "de_ww_search.json"), encoding="utf-8"))
    urls = json.load(open(os.path.join(IN, "de_ww_urls.json")))
    name_of = {}   # Wegweiser display name -> NUTS id
    for k, v in search.items():
        hit = [h for h in v["hits"] if h["friendlyUrl"] == urls.get(k)]
        if hit and k not in FIX: name_of[hit[0]["name"]] = k
    for k, n in FIX.items(): name_of[n] = k
    rate, hist = {}, {}
    for f in sorted(glob.glob(os.path.join(IN, "de_ww_*.csv"))):
        text = open(f, encoding="latin-1").read()
        for row in csv.reader(io.StringIO(text), delimiter=";"):
            if len(row) >= 4 and row[0] in name_of and re.match(r"[\d,]+$", row[3].strip()):
                rate[name_of[row[0]]] = float(row[3].replace(",", "."))
                hist[name_of[row[0]]] = {y: float(x.replace(",", ".")) for y, x in zip(("2021", "2022", "2023"), row[1:4]) if re.match(r"[\d,]+$", x.strip())}
    if "DEG0P" in rate: rate.setdefault("DEG0N", rate["DEG0P"]); hist.setdefault("DEG0N", hist.get("DEG0P", {}))
    kids = eurostat("es_de_pop.json", age="Y_LT15", sex="T", unit="NR")
    dens = eurostat("es_de_dens.json")
    geo = json.load(open(os.path.join(IN, "nuts3_2021_de.geojson"), encoding="utf-8"))
    rows, feats = [], []
    for f in geo["features"]:
        p = f["properties"]; k = p["NUTS_ID"]
        name = re.sub(r",\s*Kreisfreie Stadt$", " (city)", p["NAME_LATN"]).replace(", Landkreis", " (district)")
        c = kids.get(k, (None, ""))[0]; r = rate.get(k); d = dens.get(k, (None, ""))[0]
        rows.append({"District": name, "State": LAND[k[:3]],
                     "Type": "District-free city" if "Kreisfreie Stadt" in p["NAME_LATN"] or k in ("DE300", "DE600", "DE501", "DE502") else "District",
                     "Locale": "" if d is None else "Urban" if d >= 2000 else "Suburban" if d >= 500 else "Mixed" if d >= 100 else "Rural",
                     **meeting_cols(k), "Children": round(c) if c else "",
                     "Children in Low Income": round(c * r / 100) if c and r is not None else "",
                     "Percentage of Children in Low Income": f"{r:.2f}%" if r is not None else "",
                     "Poverty by year": "; ".join(f"{y}:{v}" for y, v in sorted(hist.get(k, {}).items())),
                     "People per km² (estimated)": round(d) if d else "",
                     "Map note": "Merged into the Wartburgkreis in July 2021; shown with the Wartburgkreis figure" if k == "DEG0N" else "",
                     "District ID": f"DE-{k}"})
        rnd = lambda c: [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 3), round(c[1], 3)]
        feats.append({"type": "Feature", "properties": {"id": f"DE-{k}", "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    rows.sort(key=lambda r: r["District"])
    with open(os.path.join(DOCS, "germany.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", "germany.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(len(rows), "districts; child poverty for", sum(1 for r in rows if r["Percentage of Children in Low Income"]), "; children for", sum(1 for r in rows if r["Children"]))
    print("missing:", [r["District"] for r in rows if not r["Percentage of Children in Low Income"]])


if __name__ == "__main__":
    main()
