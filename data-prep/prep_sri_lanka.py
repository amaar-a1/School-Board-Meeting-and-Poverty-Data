"""Turns the Sri Lanka downloads (made on GitHub's runner, fetch rounds 38 and 42) into the inputs build_latam.sri_lanka()
reads (data-prep/inputs/sri_lanka/).

- Poverty: Department of Census and Statistics (DCS), Poverty Indicators 2019 (from the Household Income and Expenditure
  Survey 2019), Table 04: the poverty headcount index by district, on the updated official poverty line (based on
  2012/13, NCPI), all ages; the figure on the old line (based on 2002) is kept for the note.
- Population: DCS, Census of Population and Housing 2024, preliminary report: population by district, 2024.
- Borders: geoBoundaries (gbOpen) LKA ADM2 (25 districts) and ADM1 (9 provinces, for each district's province).
- Children (for the enrollment estimate): WorldPop's 2025 age structures (R2025A, 1 km), summed over each border
  (lka_ages_2025.json); the Ministry of Education's school census couldn't be reached.
Then, after build_latam.py, run data-prep/estimate_enrollment.py sri_lanka.csv.
Usage: python3 data-prep/prep_sri_lanka.py RAWDIR   (RAWDIR holds pi19.txt and pp.txt, pdftotext -layout of the two PDFs)
"""
import json, os, re, sys
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "sri_lanka")
DISTRICTS = ["Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya", "Galle", "Matara", "Hambantota", "Jaffna", "Mannar", "Vavuniya",
             "Mullaitivu", "Kilinochchi", "Batticaloa", "Ampara", "Trincomalee", "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla",
             "Monaragala", "Ratnapura", "Kegalle"]
key = lambda s: re.sub(r"[^a-z]", "", re.sub(r"\s*District$", "", s).lower()).replace("vavunia", "vavuniya").replace("vavunya", "vavuniya").replace("moneragala", "monaragala")
num = lambda s: float(s.replace(",", ""))


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 5), round(c[1], 5)]


def main(raw):
    t = open(os.path.join(raw, "pi19.txt"), encoding="utf-8").read()
    t = t[t.index("Table 04"):t.index("Table 05")]
    pov = {}
    for line in t.splitlines():
        m = re.match(r"\s*([A-Za-z][A-Za-z ]+?)\s{2,}([\d.]+)\s+([\d,]+)\s+([\d.]+)\s+([\d.]+)\s+([\d,]+)\s+([\d.]+)\s*$", line)
        if m and key(m.group(1)) in {key(d) for d in DISTRICTS}: pov[key(m.group(1))] = (num(m.group(5)), num(m.group(2)), int(num(m.group(6))))
    pop = {}
    for line in open(os.path.join(raw, "pp.txt"), encoding="utf-8"):
        m = re.match(r"([A-Za-z][A-Za-z ]+?)\s{2,}([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+[\d.]+\s+[\d.]+\s+([\d,]+)\s", line)
        if m and key(m.group(1)) in {key(d) for d in DISTRICTS} and key(m.group(1)) not in pop: pop[key(m.group(1))] = int(num(m.group(5)))
    prov = [(f["properties"]["shapeName"], shape(f["geometry"]).buffer(0)) for f in json.load(open(os.path.join(raw, "lka_gb_ADM1.geojson"), encoding="utf-8"))["features"]]
    ages = json.load(open(os.path.join(raw, "lka_ages_2025.json"), encoding="utf-8"))["districts"]
    data, feats = {}, []
    for f in json.load(open(os.path.join(raw, "lka_gb_ADM2.geojson"), encoding="utf-8"))["features"]:
        k = key(f["properties"]["shapeName"])
        name = next(d for d in DISTRICTS if key(d) == k)
        g = shape(f["geometry"]).buffer(0); pt = g.representative_point()
        pv = next((n for n, pg in prov if pg.contains(pt)), None) or min(prov, key=lambda p: p[1].distance(pt))[0]
        a = ages.get(f["properties"]["shapeID"], {})
        did = "LKA-" + f["properties"]["shapeID"][-8:]
        data[did] = {"name": name, "province": pv.replace(" Province", ""), "pov": pov[k][0], "pov_old": pov[k][1], "poor": pov[k][2], "pop": pop.get(k),
                     "ages": {g_: round(a.get("f" + g_, 0) + a.get("m" + g_, 0)) for g_ in ("05", "10", "15")} if a else None}
        feats.append({"type": "Feature", "properties": {"id": did, "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "lka_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "lka_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"))
    print(len(data), "districts; poverty", len(pov), "; population", sum(x["pop"] or 0 for x in data.values()), [x["name"] for x in data.values() if not x["pop"]])


if __name__ == "__main__":
    main(*sys.argv[1:])
