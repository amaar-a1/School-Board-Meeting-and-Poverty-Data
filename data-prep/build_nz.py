"""Build docs/data/new-zealand.csv and docs/data/map/new-zealand.json.

New Zealand's schools each have their own elected board (about 2,500), so there's no district-level
board. Stats NZ publishes child poverty for 12 regional council areas (some combined), so the
site shows those areas, with 0 meetings.
- Child low income: Stats NZ, Child poverty statistics, year ended June 2025, Table 4.02: children in
  households below 60% of the median equivalised disposable income before housing costs (BHC).
- Enrollment: students in primary and secondary schools at July 2025 (Ministry of Education roll returns,
  via Figure.NZ), added up the way Stats NZ combines regions (inputs/nz/school_rolls_july2025.csv).
- Meetings: New Zealand's councils have no part in schooling, so (as for Australia's councils) the meetings of each
  area's regional or unitary council stand in: recordings on the council's YouTube channel
  (inputs/nz/council_videos.json, listed with yt-dlp), counting titles that name a committee, meeting, hui or
  community board, or a council or hearings with a date; parts and agenda items of one meeting count once.
- Borders: Natural Earth 1:10m admin-1 regions, merged the way Stats NZ combines them.
- Locale (estimated): children / 0.22 (their approximate share of the population) over each area.
Usage: python3 data-prep/build_nz.py
"""
import csv, json, os, re, sys
import openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo_area import area_km2
from meeting_dates import parse, summary

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


STRONG = re.compile(r"\b(committee|sub-?committee|meeting|hui|komiti|community board)\b", re.I)
WEAK = re.compile(r"\b(council|hearings|hearing\s*[-–(]|forum|river authority)\b", re.I)
NOT = re.compile(r"\b(award|winner|webinar|explainer|how (do|to)|promo|trailer|highlights?|interview|launch|students present|"
                 r"clip of the week|stv|rainfall)\b", re.I)


def council_meetings():
    """{area id: (count, titles, councils)}: distinct dated council meetings on each area's councils' channels."""
    import datetime
    today = datetime.date.today(); now = (today.year, today.month, today.day)
    p = os.path.join(IN, "council_videos.json")
    if not os.path.exists(p): return {}
    out = {}
    for area, cs in json.load(open(p, encoding="utf-8"))["areas"].items():
        seen, titles = set(), []
        for c in cs:
            for title, up, _ in c["titles"]:
                dt = parse(title)
                if not ((STRONG.search(title) or (WEAK.search(title) and dt)) and not NOT.search(title)): continue
                dt = dt or ((int(up[:4]), int(up[4:6]), int(up[6:8])) if up else None)
                if not dt or (dt[0], dt[1] or 1, dt[2] or 1) > now: continue
                k = re.sub(r"\s*[-–|:]?\s*(items?\s*[\d.,\s&and-]+|part\s*\d+|recording\s*#?\s*\d+|(morning|afternoon|evening)\s+session|day\s*\d+)\b.*$", "", re.sub(r"\d", "", title), flags=re.I)
                k = (dt, re.sub(r"[^a-z]", "", k.lower())[:60])
                if k in seen: continue
                seen.add(k); titles.append(title if parse(title) else f"{title} ({dt[0]}-{dt[1]:02d}-{dt[2]:02d})")
        out[area] = (len(seen), titles, [c["council"] for c in cs])
    return out


def main():
    ws = openpyxl.load_workbook(os.path.join(IN, "nz_cp2025.xlsx"), read_only=True)["Table4.02"]
    vals, reg, hist = {}, None, {}
    for row in ws.iter_rows(values_only=True):
        v = [c for c in row if c is not None]
        if len(v) == 1 and isinstance(v[0], str):
            reg = v[0][:-7] if v[0].endswith(" region") else None   # "All regions" and notes end a block
        elif reg and v and str(v[0]) == "2025":
            vals.setdefault(reg, (v[1], v[5]))   # rate (%), number of children (000s)
        if reg and v and re.fullmatch(r"20\d\d", str(v[0])) and isinstance(v[1], (int, float)):
            hist.setdefault(reg, {}).setdefault(str(v[0]), v[1])
    roll = {r["Regional Council Area"]: int(r["Number of Students"]) for r in csv.DictReader(open(os.path.join(IN, "school_rolls_july2025.csv"), encoding="utf-8"))}
    geo = json.load(open(os.path.join(IN, "nz_regions.geojson"), encoding="utf-8"))
    by = {f["properties"]["iso_3166_2"]: f["geometry"] for f in geo["features"]}
    meet = council_meetings()
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
                     "Available Board Meetings": meet.get(f"NZ-{CODE[name]}", (0,))[0],
                     "Meetings type": "Council meetings (stand-in: councils have no part in schooling)" if f"NZ-{CODE[name]}" in meet else "",
                     "Meetings source": "; ".join(meet[f"NZ-{CODE[name]}"][2]) + " (YouTube)" if f"NZ-{CODE[name]}" in meet else "",
                     "Latest meeting": summary(meet.get(f"NZ-{CODE[name]}", (0, []))[1])[0], "Meetings by year": summary(meet.get(f"NZ-{CODE[name]}", (0, []))[1])[1],
                     "Children": kids, "Children in Low Income": round(n * 1000),
                     "Percentage of Children in Low Income": f"{rate:.2f}%",
                     "Enrollment": sum(roll[p.strip()] for p in name.split("/")), "Enrollment year": "July 2025",
                     "Poverty by year": "; ".join(f"{y}:{x}" for y, x in sorted(hist.get(name, {}).items())), "People per km² (estimated)": round(dens),
                     "District ID": f"NZ-{CODE[name]}"})
        rnd = lambda c: [rnd(x) for x in c] if isinstance(c[0], list) else [round(c[0], 3), round(c[1], 3)]
        feats.append({"type": "Feature", "properties": {"id": f"NZ-{CODE[name]}", "NAME": name}, "geometry": {"type": "MultiPolygon", "coordinates": rnd(polys)}})
    with open(os.path.join(DOCS, "new-zealand.csv"), "w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(DOCS, "map", "new-zealand.json"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    for r in rows: print(r)


if __name__ == "__main__":
    main()
    import add_regions   # the Region column for the site's region menu
    for k in ("new-zealand",):
        add_regions.add(k)
