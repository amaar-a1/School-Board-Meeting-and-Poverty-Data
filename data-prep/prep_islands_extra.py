"""Borders and YouTube titles for the islands added in November 2026, for build_islands.py.

Borders: Eurostat GISCO countries 2024 at 1:1 million (CNTR_RG_01M_2024_4326, downloaded on GitHub's runner),
for Christmas Island (CX), the Cocos (Keeling) Islands (CC), Gibraltar (GI), Pitcairn (PN), Tokelau (TK) and
Svalbard (SJ, without Jan Mayen, south of 75°N). The Caribbean Netherlands (BQ) is split into Bonaire, Sint
Eustatius and Saba by longitude. The Chatham Islands come from inputs/nz/nz_regions.geojson (NZ-CIT).
Writes inputs/islands/extra_borders.geojson, and inputs/islands/youtube/islands_titles_more.json from the runner's
YouTube listing (yt.json): every video and live-stream title of the councils' channels used.
Usage: python3 data-prep/prep_islands_extra.py GISCO.geojson YT.json
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs")
CODES = {"CX": "CXR", "CC": "CCK", "GI": "GIB", "PN": "PCN", "TK": "TKL", "SJ": "SJM"}
NAMES = {"CXR": "Christmas Island", "CCK": "Cocos (Keeling) Islands", "GIB": "Gibraltar", "PCN": "Pitcairn Islands", "TKL": "Tokelau",
         "SJM": "Svalbard", "BON": "Bonaire", "STA": "Sint Eustatius", "SAB": "Saba", "CHT": "Chatham Islands"}
CHANNELS = ["UCxqEdMrLfjuM_PiOW0nfFTg", "UCMHMQ2Ugkm8qLSudfNV-nzg", "UCHPtYhBXgaCWac8QqxQVZlg", "UCAag5hACX3kH2zFmB3YvA7w",
            "UCo-EbrFXLtZOo_XB50hUEbg", "UCBskr7IINEHAYUmtMxOoTyg"]


def polys(g):
    return g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]


def first_point(p):
    return p[0][0]


def main(gisco, yt):
    feats = []
    for f in json.load(open(gisco, encoding="utf-8"))["features"]:
        c = f["properties"]["CNTR_ID"]
        if c in CODES:
            ps = polys(f["geometry"])
            if c == "SJ": ps = [p for p in ps if first_point(p)[1] > 75]
            feats.append((CODES[c], ps))
        elif c == "BQ":
            parts = {"BON": [], "STA": [], "SAB": []}
            for p in polys(f["geometry"]):
                x = first_point(p)[0]
                parts["BON" if x < -65 else "SAB" if x < -63.1 else "STA"].append(p)
            feats += list(parts.items())
    for f in json.load(open(os.path.join(IN, "nz", "nz_regions.geojson"), encoding="utf-8"))["features"]:
        if f["properties"].get("iso_3166_2") == "NZ-CIT": feats.append(("CHT", polys(f["geometry"])))
    out = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"ISO": k, "NAME": NAMES[k]},
           "geometry": {"type": "MultiPolygon", "coordinates": ps}} for k, ps in feats]}
    json.dump(out, open(os.path.join(IN, "islands", "extra_borders.geojson"), "w", encoding="utf-8"), separators=(",", ":"))
    print(sorted(k for k, _ in feats))
    y = json.load(open(yt, encoding="utf-8")); titles = {}
    for place in y.values():
        for cid, c in place["channels"].items():
            if cid in CHANNELS:
                titles[f"https://www.youtube.com/channel/{cid}"] = [t for t in (c.get("titles") or []) + (c.get("streams") or []) if t]
    json.dump(titles, open(os.path.join(IN, "islands", "youtube", "islands_titles_more.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print({k: len(v) for k, v in titles.items()})


if __name__ == "__main__":
    main(*sys.argv[1:3])
