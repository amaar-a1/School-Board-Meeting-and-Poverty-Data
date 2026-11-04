"""Build docs/data/islands.csv and docs/data/map/islands.json: small island countries and territories.

Each island country or territory runs its schools through one government education ministry or
department, so each is a single "district". (Iceland's municipalities run its compulsory schools;
it's shown as one unit here.) The US territories and Saint-Pierre-et-Miquelon have their own views.
- Borders: Natural Earth 1:10m admin-0 (public domain), inputs/world/ne_10m_islands.geojson.
- Poverty, best available for each place, in this order:
  1. children under 18 below 60% of the median income (Eurostat EU-SILC ilc_li02): Malta, Cyprus, Iceland;
  2. people below the national poverty line (World Bank SI.POV.NAHC, else the CIA World Factbook);
  3. unemployment rate as a stand-in (World Bank SL.UEM.TOTL.ZS, ILO estimate, else the Factbook).
  The national poverty lines differ from country to country, so these aren't comparable.
- Enrollment: primary plus secondary pupils (World Bank SE.PRM.ENRL + SE.SEC.ENRL, UNESCO), latest year
  with both.
- Children: population x share aged 0-14 (World Bank, else the Factbook).
- Locale (estimated): people per km² of land (Factbook area): urban 2,000+, suburban 500-2,000, mixed
  100-500, rural under 100.
Usage: python3 data-prep/build_islands.py
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs")
DOCS = os.path.join(HERE, "..", "docs", "data")
REGION = {"Caribbean": "Caribbean", "Polynesia": "Pacific", "Melanesia": "Pacific", "Micronesia": "Pacific",
          "Australia and New Zealand": "Pacific", "Northern Europe": "Europe and the North Atlantic",
          "Southern Europe": "Europe and the North Atlantic", "Western Asia": "Asia and the Indian Ocean",
          "South-Eastern Asia": "Asia and the Indian Ocean", "Southern Asia": "Asia and the Indian Ocean",
          "Eastern Africa": "Africa and the South Atlantic", "Western Africa": "Africa and the South Atlantic",
          "Middle Africa": "Africa and the South Atlantic", "South America": "Africa and the South Atlantic",
          "Northern America": "Europe and the North Atlantic", "Seven seas (open ocean)": "Africa and the South Atlantic"}
NAMES = {"Antigua and Barb.": "Antigua and Barbuda", "St. Kitts and Nevis": "Saint Kitts and Nevis", "St. Vin. and Gren.": "Saint Vincent and the Grenadines",
         "Cayman Is.": "Cayman Islands", "British Virgin Is.": "British Virgin Islands", "Turks and Caicos Is.": "Turks and Caicos Islands",
         "Solomon Is.": "Solomon Islands", "Cook Is.": "Cook Islands", "Marshall Is.": "Marshall Islands", "Fr. Polynesia": "French Polynesia",
         "Wallis and Futuna Is.": "Wallis and Futuna", "Falkland Is.": "Falkland Islands", "Faeroe Is.": "Faroe Islands",
         "St-Barthélemy": "Saint-Barthélemy", "St-Martin": "Saint-Martin (French part)", "Sint Maarten": "Sint Maarten (Dutch part)",
         "Micronesia": "Federated States of Micronesia", "São Tomé and Principe": "São Tomé and Príncipe",
         "Saint Helena": "Saint Helena, Ascension and Tristan da Cunha"}
pct = lambda s: float(re.match(r"\s*([\d.]+)%", s).group(1)) if s and re.match(r"\s*([\d.]+)%", s) else None
year = lambda s: (re.search(r"\((\d{4})", s or "") or [None, ""])[1]
num = lambda s: float(re.match(r"\s*([\d,.]+)", s).group(1).replace(",", "")) if s and re.match(r"\s*[\d,.]*\d", s) else None


def txt(v):
    return v.get("text") if isinstance(v, dict) and "text" in v else v


def fb_latest(v):
    """Factbook values: plain text, or {"Unemployment rate 2024": {"text": ...}, ...}."""
    if v is None: return None, ""
    if isinstance(v, dict) and "text" not in v:
        ks = sorted((k for k in v if re.search(r"\d{4}$", k)), reverse=True)
        v = v[ks[0]] if ks else None
    t = txt(v)
    return (pct(t), year(t)) if t else (None, "")


def main():
    ne = {o["ISO_A3"]: o for o in json.load(open(os.path.join(IN, "world", "islands_ne.json"), encoding="utf-8"))}
    fb = json.load(open(os.path.join(IN, "islands", "factbook_extract.json"), encoding="utf-8"))
    # The 2026 Factbook dropped poverty and unemployment for many territories; the November 2023
    # edition (factbook.json commit 546573f) still has them, often from older surveys.
    old = json.load(open(os.path.join(IN, "islands", "factbook_2023_economy.json"), encoding="utf-8"))["data"]
    wb = json.load(open(os.path.join(IN, "islands", "worldbank.json")))
    W = {}
    for ind, rows in wb.items():
        for r in rows:
            W.setdefault(ind, {}).setdefault(r["countryiso3code"], {})[int(r["date"])] = r["value"]
    latest = lambda ind, iso: max(W.get(ind, {}).get(iso, {}).items(), default=(None, None))
    es = json.load(open(os.path.join(IN, "islands", "eurostat_ilc_li02.json")))
    ids, size = es["id"], es["size"]; cat = {k: list(es["dimension"][k]["category"]["index"]) for k in ids}
    def esv(geo, t):
        sel = dict(freq="A", statinfo="MED_EI", unit="PC", rskpovth="B_60", sex="T", age="Y_LT18", geo=geo, time=t); i = 0
        for k, s in zip(ids, size): i = i * s + cat[k].index(sel[k])
        return es["value"].get(str(i))
    ISO2 = {"MLT": "MT", "CYP": "CY", "ISL": "IS"}
    out = []
    for iso, n in sorted(ne.items(), key=lambda x: NAMES.get(x[1]["NAME"], x[1]["NAME"])):
        f = fb.get(n["ADM0_A3"]) or fb.get(iso) or {}
        econ = {**old.get(iso, {}), **f.get("Economy", {})}
        name = NAMES.get(n["NAME"], n["NAME"])
        rate = measure = ""
        if iso in ISO2:
            t = max((t for t in cat["time"] if esv(ISO2[iso], t) is not None), default=None)
            if t: rate, measure = esv(ISO2[iso], t), f"Children under 18 below 60% of the median income (Eurostat EU-SILC, {t})"
        if rate == "":
            y, v = latest("SI.POV.NAHC", iso)
            fv, fy = fb_latest(econ.get("Population below poverty line"))
            if v is not None and (not fy or int(fy) <= y):
                rate, measure = v, f"People below the national poverty line, all ages (World Bank, {y})"
            elif fv is not None:
                rate, measure = fv, f"People below the national poverty line, all ages (CIA World Factbook, {fy} estimate)"
        if rate == "":
            y, v = latest("SL.UEM.TOTL.ZS", iso)
            fv, fy = fb_latest(econ.get("Unemployment rate"))
            if fv is not None and (y is None or (fy and int(fy) >= y)):
                rate, measure = fv, f"Unemployment rate, a stand-in for poverty (CIA World Factbook, {fy} estimate)"
            elif v is not None:
                rate, measure = v, f"Unemployment rate, a stand-in for poverty (World Bank / ILO estimate, {y})"
        py, pop = latest("SP.POP.TOTL", iso)
        if pop is None:
            pop = num(txt((f.get("People and Society", {}).get("Population") or {}).get("total")) if isinstance(f.get("People and Society", {}).get("Population"), dict) else txt(f.get("People and Society", {}).get("Population")))
        _, share = latest("SP.POP.0014.TO.ZS", iso)
        if share is None:
            share = pct(txt((f.get("People and Society", {}).get("Age structure") or {}).get("0-14 years")))
        # Enrollment: latest year with both primary and secondary.
        pr, se = W.get("SE.PRM.ENRL", {}).get(iso, {}), W.get("SE.SEC.ENRL", {}).get(iso, {})
        both = sorted(set(pr) & set(se))
        enr, ey = (round(pr[both[-1]] + se[both[-1]]), str(both[-1])) if both else ("", "")
        area = f.get("Geography", {}).get("Area") or {}
        land = num(txt(area.get("land"))) or num(txt(area.get("total") or area.get("total ")))
        dens = pop / land if pop and land else None
        loc = "" if dens is None else "Urban" if dens >= 2000 else "Suburban" if dens >= 500 else "Mixed" if dens >= 100 else "Rural"
        sov = n["SOVEREIGNT"]
        status = "Independent country" if sov in (n["NAME"], n["NAME_LONG"]) or iso in ("FSM", "KNA", "VCT", "ATG", "STP", "BHS", "MHL", "SLB") else f"Territory of {'the United Kingdom' if sov == 'United Kingdom' else 'the Netherlands' if sov == 'Netherlands' else sov}"
        if iso in ("COK", "NIU"): status = "Self-governing, in free association with New Zealand"
        out.append({"District": name, "Region": REGION.get(n["SUBREGION"], n["SUBREGION"]), "Status": status,
                    "Available Board Meetings": 0,
                    "Poverty rate or stand-in": f"{rate:.2f}%" if rate != "" else "", "Poverty measure": measure,
                    "Population": round(pop) if pop else "", "Children Ages 0-14 (estimated)": round(pop * share / 100) if pop and share else "",
                    "Enrollment": enr, "Enrollment year": ey, "Locale": loc, "People per km² (estimated)": round(dens) if dens else "",
                    "District ID": f"ISLE-{iso}"})
    cols = list(out[0])
    with open(os.path.join(DOCS, "islands.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=cols); w.writeheader(); w.writerows(out)
    shapes = json.load(open(os.path.join(IN, "world", "ne_10m_islands.geojson"), encoding="utf-8"))
    iso_of = {o["ADM0_A3"]: o["ISO_A3"] for o in ne.values()}
    rnd = lambda c: [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 3), round(c[1], 3)]
    feats = [{"type": "Feature", "properties": {"id": f"ISLE-{iso_of[f['properties']['ADM0_A3']]}", "NAME": f["properties"]["NAME"]},
              "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}} for f in shapes["features"]]
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", "islands.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    for r in out:
        print(f"{r['District'][:28]:28} {r['Region'][:12]:12} {r['Poverty rate or stand-in']:>7} {r['Poverty measure'][:55]:55} enr {r['Enrollment']!s:>7} {r['Enrollment year']} {r['Locale']}")


if __name__ == "__main__":
    main()
