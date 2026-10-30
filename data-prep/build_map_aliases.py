"""Build docs/data/map/aliases.json: map borders that have no row in docs/data/national.csv to the
district(s) whose figures they should show. Used by the map only; the data itself is unchanged.

Usage:
  python3 data-prep/build_map_aliases.py NCES_2023_FULL_JSON

  NCES_2023_FULL_JSON  all pages of https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2023/
                       (untrimmed: the supervisory_union_number and agency_type fields are needed)

Vermont: Census poverty figures are reported for supervisory unions, but the border files draw the
member town districts. Each member is linked to its union through NCES's supervisory_union_number.
Districts merged in 2024 (MERGED below) have no 2024 border yet, so their older pieces show the
merged district's figures.
"""
import csv
import json
import re
import sys

MERGED = {
    # border GEOID: (data District ID(s), note)
    "0903515": (["0999501"], "Merged with Litchfield into Regional School District 20 in 2024"),
    "0902220": (["0999501"], "Merged with Region 6 into Regional School District 20 in 2024"),
    "3401020": (["3499501"], "Merged into the PreK-12 Henry Hudson Regional School District in 2024"),
    "3407200": (["3499501"], "Merged into the PreK-12 Henry Hudson Regional School District in 2024"),
    "3407050": (["3499501"], "Merged into the PreK-12 Henry Hudson Regional School District in 2024"),
    "1737120": (["1799501"], "Merged into St. Anne Unit District 24 in 2024"),
    "1737140": (["1799501"], "Merged into St. Anne Unit District 24 in 2024"),
    "4503914": (["4599501"], "Part of Barnwell County School District"),
    "4501080": (["4599501"], "Part of Barnwell County School District"),
    "3100122": (["3172700", "3176390"], "Covers Lawrence-Nelson Public Schools and Sandy Creek Schools; figures are the two combined"),
    # Vermont union school districts NCES gives no supervisory union number, linked by name.
    "5099002": (["5099905"], "Vermont union school district; figures are for Southwest Vermont Supervisory Union"),
    "5099003": (["5099905"], "Vermont union school district; figures are for Southwest Vermont Supervisory Union"),
    "5099004": (["5099931"], "Vermont union school district; figures are for North Country Supervisory Union"),
    "5099001": (["5099946"], "Vermont union school district; figures are for Windham Central Supervisory Union"),
}


def key(name):
    return re.sub(r"\b(supervisory|union|district|school|unified|sd|su)\b", "", name.lower()).replace("-", " ").split()


def main(nces_path):
    rows = list(csv.DictReader(open("docs/data/national.csv", newline="", encoding="utf-8")))
    data = {r["District ID"]: r for r in rows}
    vt_rows = [r for r in rows if r["State"] == "VT"]
    geo = set()
    for n in ("unsd", "elsd", "scsd"):
        t = json.load(open(f"docs/data/map/{n}.json"))
        geo |= {g["properties"]["GEOID"] for g in t["objects"][n]["geometries"]}
    nces = {r["leaid"]: r for r in json.load(open(nces_path)) if r["fips"] == 50}
    unions = {r["supervisory_union_number"]: r for r in nces.values() if r["agency_type"] == 3}

    out = {g: {"ids": ids, "note": note} for g, (ids, note) in MERGED.items()}
    for g in sorted(x for x in geo if x.startswith("50") and x not in data):
        member = nces.get(g)
        union = member and unions.get(member["supervisory_union_number"])
        if not union:
            continue
        target = union["leaid"] if union["leaid"] in data else None
        if not target:
            match = [r["District ID"] for r in vt_rows if key(r["District"]) == key(union["lea_name"])]
            target = match[0] if len(match) == 1 else None
        if target:
            out[g] = {"ids": [target], "note": f"Vermont town district; figures are for {data[target]['District']}"}
    json.dump(out, open("docs/data/map/aliases.json", "w"), indent=0, sort_keys=True)
    print(len(out), "aliases")


if __name__ == "__main__":
    main(sys.argv[1])
