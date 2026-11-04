"""Build docs/data/new-zealand.csv and docs/data/map/new-zealand.json.

New Zealand's schools each have their own elected board (about 2,500), so there's no district-level
board. Stats NZ publishes child poverty for 12 regional council areas (some combined), so the
site shows those areas, with 0 meetings.
- Child low income: Stats NZ, Child poverty statistics, year ended June 2025, Table 4.02: children in
  households below 60% of the median equivalised disposable income before housing costs (BHC).
- Borders: Natural Earth 1:10m admin-1 regions, merged the way Stats NZ combines them.
- Locale (estimated): children / 0.22 (their approximate share of the population) over each area.
Usage: python3 data-prep/build_nz.py
"""
import csv, json, os, sys
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "nz")
DOCS = os.path.join(HERE, "..", "docs", "data")
AREAS = {  # Stats NZ area -> Natural Earth ISO 3166-2 codes
    "Northland": ["NZ-NTL"], "Auckland": ["NZ-AUK"], "Waikato": ["NZ-WKO"], "Bay of Plenty": ["NZ-BOP"],
    "Gisborne / Hawke's Bay": ["NZ-GIS", "NZ-HKB"], "Taranaki": ["NZ-TKI"], "Manawatū-Whanganui": ["NZ-MWT"],
    "Wellington": ["NZ-WGN"], "Tasman / Nelson / Marlborough / West Coast": ["NZ-TAS", "NZ-NSN", "NZ-MBH", "NZ-WTC"],
    "Canterbury": ["NZ-CAN"], "Otago": ["NZ-OTA"], "Southland": ["NZ-STL"]}
CODE = {"Northland": "NTL", "Auckland": "AUK", "Waikato": "WKO", "Bay of Plenty": "BOP", "Gisborne / Hawke's Bay": "GIS-HKB",
        "Taranaki": "TKI", "Manawatū-Whanganui": "MWT", "Wellington": "WGN", "Tasman / Nelson / Marlborough / West Coast": "TNMW",
        "Canterbury": "CAN", "Otago": "OTA", "Southland": "STL"}


def main():
    ws = openpyxl.load_workbook(os.path.join(IN, "nz_cp2025.xlsx"), read_only=True)["Table4.02"]
    vals, reg = {}, None
    for row in ws.iter_rows(values_only=True):
        v = [c for c in row if c is not None]
        if len(v) == 1 and isinstance(v[0], str):
            reg = v[0][:-7] if v[0].endswith(" region") else None   # "All regions" and notes end a block
        elif reg and v and str(v[0]) == "2025":
            vals.setdefault(reg, (v[1], v[5]))   # rate (%), number of children (000s)
    geo = json.load(open(os.path.join(IN, "nz_regions.geojson"), encoding="utf-8"))
    by = {f["properties"]["iso_3166_2"]: f["geometry"] for f in geo["features"]}
    rows, feats = [], []
    for name, codes in AREAS.items():
        polys = []
        for c in codes:
            g = by[c]; polys += g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        gm = {"type": "MultiPolygon", "coordinates": polys}
        rate, n = vals[name]
        kids = round(n * 1000 / rate * 100)
        dens = kids / 0.22 / area_km2(gm)
        rows.append({"District": name, "Locale": "Urban" if dens >= 2000 else "Suburban" if dens >= 500 else "Mixed" if dens >= 100 else "Rural",
                     "Available Board Meetings": 0, "Children": kids, "Children in Low Income": round(n * 1000),
                     "Percentage of Children in Low Income": f"{rate:.2f}%", "People per km² (estimated)": round(dens),
                     "District ID": f"NZ-{CODE[name]}"})
        rnd = lambda c: [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 3), round(c[1], 3)]
        feats.append({"type": "Feature", "properties": {"id": f"NZ-{CODE[name]}", "NAME": name}, "geometry": {"type": "MultiPolygon", "coordinates": rnd(polys)}})
    with open(os.path.join(DOCS, "new-zealand.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", "new-zealand.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    for r in rows: print(r)


if __name__ == "__main__":
    main()
