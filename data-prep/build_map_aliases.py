"""Build docs/data/map/aliases.json: map borders that have no row in docs/data/national.csv to the
district(s) whose figures they should show. Used by the map only; the data itself is unchanged.

Usage:
  python3 data-prep/build_map_aliases.py NCES_2023_FULL_JSON

  NCES_2023_FULL_JSON  all pages of https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2023/
                       (untrimmed: the supervisory_union_number and agency_type fields are needed)

Vermont: Census poverty figures are reported for supervisory unions, but the border files draw the
member town districts. Each member is linked to its union through NCES's supervisory_union_number.
Districts merged in 2024 (MERGED below) have no 2024 border yet, so their older pieces show the
merged district's figures. Grade-range pieces of districts (e.g. "Hamilton Unified School District
(9-12)") show their parent district, matched by name within the state. Districts the Census poverty
file leaves out (Defense Department base schools, districts with no schools of their own, a few tiny
districts) show their county's all-ages poverty rate (SAIPE 2024), like national.csv does for
districts with no school-age children.
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
    # High school pieces whose names don't match their parent district exactly.
    "0606018": (["0601415"], "High school (9-12) part of Washington Unified School District, Fresno County"),
    "4545079": (["4503390"], "Part of Richland School District 2 on Fort Jackson"),
    "4545013": (["4501110"], "Part of Beaufort County School District on Marine Corps Air Station Beaufort"),
    "2522222": (["2507990"], "Part of Mohawk Trail School District (Hawley and Charlemont)"),
    # Vermont union school districts NCES gives no supervisory union number, linked by name.
    "5099002": (["5099905"], "Vermont union school district; figures are for Southwest Vermont Supervisory Union"),
    "5099003": (["5099905"], "Vermont union school district; figures are for Southwest Vermont Supervisory Union"),
    "5099004": (["5099931"], "Vermont union school district; figures are for North Country Supervisory Union"),
    "5099001": (["5099946"], "Vermont union school district; figures are for Windham Central Supervisory Union"),
}


# Districts with a border but no row in the Census poverty file, and why.
NOT_IN_CENSUS = {   # border GEOID: (county FIPS, reason)
    "4500005": ("45079", "Defense Department school on Fort Jackson; the Census poverty file has no figures for base schools"),
    "4500006": ("45013", "Defense Department school on Marine Corps Air Station Beaufort; the Census poverty file has no figures for base schools"),
    "3018660": ("30095", "District with no schools of its own; the Census poverty file leaves it out"),
    "3802240": ("38029", "District with no schools of its own; the Census poverty file leaves it out"),
    "4013380": ("40085", "District with no schools of its own; the Census poverty file leaves it out"),
    "4029760": ("40067", "District with no schools of its own; the Census poverty file leaves it out"),
    "0200715": ("02290", "Small district the Census poverty file leaves out"),
    "4841130": ("48233", "Small district the Census poverty file leaves out"),
}


def piece_key(name):
    """Name without grade ranges, "in <town>" suffixes and generic words, to match pieces to parents."""
    s = name.lower()
    s = re.sub(r"\((?:pk|kg|\d)[^)]*\)", "", s)
    s = re.sub(r"\b(in|for) [a-z .'-]+$", "", s)
    s = re.sub(r"\b(school district|public schools|schools|school|district|unified|unit|independent|isd|the|of)\b", " ", s)
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", s).split())


def key(name):
    return re.sub(r"\b(supervisory|union|district|school|unified|sd|su)\b", "", name.lower()).replace("-", " ").split()


def main(nces_path, county_path="data-prep/inputs/est24all.txt"):
    rows = list(csv.DictReader(open("docs/data/national.csv", newline="", encoding="utf-8")))
    data = {r["District ID"]: r for r in rows}
    vt_rows = [r for r in rows if r["State"] == "VT"]
    names = {}
    for n in ("unsd", "elsd", "scsd"):
        t = json.load(open(f"docs/data/map/{n}.json"))
        names.update({g["properties"]["GEOID"]: g["properties"]["NAME"] for g in t["objects"][n]["geometries"]})
    geo = set(names)
    all_nces = {r["leaid"]: r for r in json.load(open(nces_path))}
    nces = {k: r for k, r in all_nces.items() if r["fips"] == 50}
    counties = {}
    for line in open(county_path, encoding="latin-1"):
        f = line.split()
        if len(f) > 6 and f[1] != "0":
            counties[f[0] + f[1].zfill(3)] = (f[5], line[193:239].strip())
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
    # Grade-range pieces of districts: same name as a district in the same state.
    by_state = {}
    for r in rows:
        by_state.setdefault(r["District ID"][:2], []).append(r)
    for g, name in sorted(names.items()):
        if g in data or g in out or g.startswith(("60", "66", "69", "72", "78")) or name == "School District Not Defined":
            continue
        match = [r for r in by_state.get(g[:2], []) if piece_key(r["District"]) == piece_key(name)]
        if len(match) == 1:
            out[g] = {"ids": [match[0]["District ID"]], "note": f"Part of {match[0]['District']}"}
    # Districts left out of the Census poverty file: their county's all-ages poverty rate.
    for g, (fips, why) in NOT_IN_CENSUS.items():
        n = all_nces.get(g, {})
        rate, county = counties[fips]
        enrollment = n.get("enrollment")
        out[g] = {"ids": [], "district": names[g], "rate": rate, "county": county,
                  "enrollment": enrollment if isinstance(enrollment, int) and enrollment >= 0 else None,
                  "note": f"{why}, so this is the all-ages poverty rate for {county} (Census SAIPE 2024)"}
    json.dump(out, open("docs/data/map/aliases.json", "w"), indent=0, sort_keys=True)
    print(len(out), "aliases")


if __name__ == "__main__":
    main(sys.argv[1])
