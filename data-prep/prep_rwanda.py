"""Turns the Rwanda downloads (made on GitHub's runner, fetch rounds 41-42) into the inputs build_latam.rwanda() reads
(data-prep/inputs/rwanda/).

- Poverty: National Institute of Statistics of Rwanda (NISR), Integrated Household Living Conditions Survey 7 (EICV7,
  2023/24), Main Indicators Report tables (EICV7_Tables_MainIndicatorReport.xlsx), Table A9.23: the headcount poverty
  rate by district, all ages, with its 95% confidence interval. Each district's province follows the table's order.
- Borders: geoBoundaries (gbOpen) RWA ADM2, simplified (30 districts).
- Population and children (for the enrollment estimate): WorldPop's 2025 age structures (R2025A, 1 km), summed over each
  border by the runner (rwa_ages_2025.json); the 2022 census district tables couldn't be downloaded.
Then, after build_latam.py, run data-prep/estimate_enrollment.py rwanda.csv.
Usage: python3 data-prep/prep_rwanda.py RAWDIR
"""
import json, os, sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "rwanda")
PROVINCES = ["City of Kigali", "Southern", "Western", "Northern", "Eastern"]


def rnd(c):
    return [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 5), round(c[1], 5)]


def main(raw):
    ws = openpyxl.load_workbook(os.path.join(raw, "main_0.xlsx"), read_only=True, data_only=True)["Table A9.23"]
    pov, part, prov = {}, None, None
    for r in ws.iter_rows(values_only=True):
        c = [x for x in r if x is not None]
        if not c: continue
        if c[0] in ("Province", "District", "Area of residence"): part = c[0]; continue
        if part == "Province" and c[0] in PROVINCES: continue
        if part == "District" and len(c) >= 5: pov[c[0]] = (round(c[1], 1), round(c[3], 1), round(c[4], 1))
    # Districts in the table's order: 3 in Kigali, 8 Southern, 7 Western, 5 Northern, 7 Eastern.
    order = list(pov)
    sizes = [3, 8, 7, 5, 7]
    pv = {}
    i = 0
    for p, n in zip(PROVINCES, sizes):
        for d in order[i:i + n]: pv[d] = p
        i += n
    ages = json.load(open(os.path.join(raw, "rwa_ages_2025.json"), encoding="utf-8"))["districts"]
    data, feats = {}, []
    for f in json.load(open(os.path.join(raw, "rwa_gb_ADM2.geojson"), encoding="utf-8"))["features"]:
        name = f["properties"]["shapeName"]
        a = ages.get(f["properties"]["shapeID"], {})
        did = "RWA-" + f["properties"]["shapeID"][-8:]
        data[did] = {"name": name, "province": pv[name], "pov": pov[name][0], "low": pov[name][1], "high": pov[name][2],
                     "pop": round(sum(a.values())) if a else None,
                     "ages": {g: round(a.get("f" + g, 0) + a.get("m" + g, 0)) for g in ("05", "10", "15")} if a else None}
        feats.append({"type": "Feature", "properties": {"id": did, "NAME": name}, "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])}})
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "rwa_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "rwa_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"))
    print(len(data), "districts; population", sum(x["pop"] or 0 for x in data.values()))


if __name__ == "__main__":
    main(*sys.argv[1:])
