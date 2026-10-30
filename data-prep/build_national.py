"""Build docs/data/national.csv: every US school district in the Census SAIPE file,
with child poverty (SAIPE 2024), NCES 2023 enrollment and locale, and the number of
available board meetings listed on CivicSearch (0 when CivicSearch doesn't list it).

Usage:
  python3 data-prep/build_national.py SAIPE_CSV NCES_JSON CIVIC_JSON OUT_CSV REPORT_CSV

  SAIPE_CSV  https://www2.census.gov/programs-surveys/saipe/datasets/2024/2024-school-districts/ussd24.csv
  NCES_JSON  all pages of https://educationdata.urban.org/api/v1/school-districts/ccd/directory/2023/
             (nces_fallback.json next to it, if present, fills enrollment and locale missing in 2023
             from the latest of the 2018-2022 directories that has them)
  CIVIC_JSON https://schools.civicsearch.org/api/get_place_list

CivicSearch places are matched to districts by federal ID when CivicSearch names a
district "District NNNNNNN", otherwise by name within the same state, with distance
between CivicSearch's map point and the NCES district office breaking ties.
REPORT_CSV lists every CivicSearch place and what it was matched to, for checking.
"""
import csv
import json
import math
import os
import re
import sys

LOCALE = {1: "Urban", 2: "Suburban", 3: "Town", 4: "Rural"}

# Words that differ between CivicSearch, Census and NCES names for the same district.
GENERIC = {
    "school", "schools", "district", "districts", "public", "isd", "cisd", "usd", "sd", "csd", "ufsd",
    "independent", "consolidated", "unified", "community", "free", "central", "the", "of",
    "board", "education", "local", "exempted", "village", "area", "regional", "unit", "unsd", "elsd", "scsd", "msd", "municipal", "system", "corporation",
    "and", "no", "number", "dist", "co", "cty", "cusd", "ccsd", "chsd", "esd", "hsd", "rsd", "vsd", "isd's",
}
ALIASES = {"saint": "st", "mount": "mt", "fort": "ft", "u": "universal", "va": "virginia"}

# CivicSearch places checked by hand. Aransas County ISD is Rockport-Fulton ISD
# (Aransas County); the project's sources note this for its 16 meetings.
MANUAL = {"aransas-county-isd-texas": "4808550"}

# Districts where the Census counts no children ages 5-17 have no school-age poverty rate, so
# they show the all-ages poverty rate of their county (SAIPE 2024, est24all.txt in the inputs
# folder). Counties are from the NCES directory, or the district's name where NCES has none.
ZERO_CHILDREN_COUNTY = {
    "2306030": "23003",   # Glenwood Plantation, ME: Aroostook County
    "2382013": "23015",   # Louds Island Unorganized Territory, ME: Lincoln County
    "2382004": "23023",   # Sagadahoc Unorganized Territory, ME: Sagadahoc County
    "3904896": "39123",   # North Bass Local School District, OH: Ottawa County
    "4104290": "41025",   # Double O School District 28, OR: Harney County
}


# Districts NCES has no 2023 record for, or records under other districts. `from` lists the NCES
# district(s) whose county and locale they take; with "sum", their enrollment is the 2023 total of
# those districts. Merged districts: news and state reports are on the site's Sources tab.
RELATED = {
    "0999501": (["0903515", "0902220"], "sum", "Formed in 2024 from Regional School District 6 and Litchfield; enrollment and locale are theirs for 2023"),
    "1799501": (["1737120", "1737140"], "sum", "Formed in 2024 from St. Anne districts 256 and 302; enrollment and locale are theirs for 2023"),
    "3499501": (["3401020", "3407200", "3407050"], "sum", "Became a PreK-12 district in 2024, merging Atlantic Highlands and Highlands; enrollment and locale are the three districts' for 2023"),
    "4599501": (["4503914", "4501080"], "sum", "Formed from Barnwell 45 and Barnwell County Consolidated (Barnwell 48); enrollment and locale are theirs for 2023"),
    "3333009": (["5000024"], "sum", "Interstate district (New Hampshire and Vermont); NCES lists it under Vermont"),
    "3172700": (["3100122"], "", "Part of South Central Nebraska Unified 5, which NCES reports as a whole (733 students in 2023, with Sandy Creek)"),
    "3176390": (["3100122"], "", "Part of South Central Nebraska Unified 5, which NCES reports as a whole (733 students in 2023, with Lawrence-Nelson)"),
    "5101230": (["5101260"], "", "Served by Fairfax County Public Schools, where NCES counts its students"),
    "5101190": (["5101740"], "", "Served by Greensville County Public Schools, where NCES counts its students"),
    "5100036": (["5104020"], "", "Served by Williamsburg-James City County Public Schools; NCES counts its students under Williamsburg City"),
}
# County (or independent city) where the related district's would be wrong.
COUNTY = {"3172700": "Nuckolls County", "5101230": "Fairfax city", "5101190": "Emporia city", "5100036": "James City County"}
# Notes for districts whose NCES enrollment counts students from elsewhere.
SERVES_OTHERS = {
    "5104020": "Enrollment includes James City County students (Williamsburg-James City County Public Schools)",
    "5101260": "Enrollment includes Fairfax City students",
    "5101740": "Enrollment includes Emporia City students",
}


def county_poverty(path):
    """All-ages poverty rate and name for each county in the SAIPE state and county file."""
    out = {}
    for line in open(path, encoding="latin-1"):
        f = line.split()
        if len(f) > 6 and f[1] != "0":
            out[f[0] + f[1].zfill(3)] = (f[5], line[193:239].strip())
    return out


def tokens(name):
    s = name.lower().replace("&", " and ").replace("’", "'")
    s = re.sub(r",\s*[a-z ]+$", "", s)            # drop ", State"
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    words = [ALIASES.get(w, w) for w in s.split()]
    core = [w for w in words if w not in GENERIC]
    return core or words


def core_key(name):
    return " ".join(tokens(name))


def distance_km(a, b):
    if None in (a[0], a[1], b[0], b[1]):
        return 1e9
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def main(saipe_path, nces_path, civic_path, out_path, report_path):
    nces = {r["leaid"]: r for r in json.load(open(nces_path))}
    # Districts with no 2023 enrollment or locale use the latest earlier NCES year that has one.
    fallback_path = os.path.join(os.path.dirname(nces_path), "nces_fallback.json")
    fallback = json.load(open(fallback_path)) if os.path.exists(fallback_path) else {}
    # NCES reports New York City's students in its 32 geographic districts, not the city-wide district.
    nyc = [r for r in nces.values() if (r.get("lea_name") or "").upper().startswith("NEW YORK CITY GEOGRAPHIC DISTRICT")]
    if nyc and "3620580" in nces:
        nces["3620580"] = {**nces["3620580"], "enrollment": sum(r["enrollment"] or 0 for r in nyc)}
    # Vermont: Census reports supervisory unions; NCES counts students in their member districts.
    vt = [r for r in nces.values() if r.get("leaid", "").startswith("50") and r.get("supervisory_union_number")]
    vt_unions = {r["supervisory_union_number"]: r for r in vt if r.get("agency_type") == 3}
    vt_members = {}
    for r in vt:
        if r.get("agency_type") != 3 and isinstance(r.get("enrollment"), int) and r["enrollment"] > 0:
            vt_members.setdefault(r["supervisory_union_number"], []).append(r["enrollment"])
    vt_key = lambda name: re.sub(r"\b(supervisory|union|district|school|unified|sd|su)\b", "", name.lower()).replace("-", " ").split()
    saipe = list(csv.DictReader(open(saipe_path, encoding="latin-1")))
    county_path = os.path.join(os.path.dirname(saipe_path), "est24all.txt")
    counties = county_poverty(county_path) if os.path.exists(county_path) else {}
    districts = []
    for r in saipe:
        if r["STABREV"] in TERRITORIES:
            continue    # territories are kept separate, in docs/data/territories.csv
        leaid = r["state"] + r["distid"]
        n = nces.get(leaid, {})
        kids, poor = int(r["rpop5_17v_24"]), int(r["saepov5_17rv_24"])
        enrollment = n.get("enrollment")
        locale = n.get("urban_centric_locale")
        fb = fallback.get(leaid, {})
        if not (isinstance(enrollment, int) and enrollment >= 0):
            enrollment = fb.get("enrollment")
        if not (isinstance(locale, int) and locale > 0):
            locale = fb.get("urban_centric_locale")
        county_name = n.get("county_name") or ""
        notes = []
        related = RELATED.get(leaid)
        if related:
            ids, how, why = related
            rel = [nces[i] for i in ids if i in nces]
            if rel:
                county_name = county_name or rel[0].get("county_name") or ""
                if not (isinstance(locale, int) and locale > 0):
                    locale = rel[0].get("urban_centric_locale")
                if how == "sum" and not (isinstance(enrollment, int) and enrollment >= 0):
                    enrollment = sum(r.get("enrollment") or 0 for r in rel)
            notes.append(why)
        if r["STABREV"] == "VT" and not (isinstance(enrollment, int) and enrollment >= 0):
            union = nces.get(leaid) if (nces.get(leaid) or {}).get("agency_type") == 3 else next(
                (u for u in vt_unions.values() if vt_key(u["lea_name"]) == vt_key(r["name"])), None)
            if union and vt_members.get(union["supervisory_union_number"]):
                enrollment = sum(vt_members[union["supervisory_union_number"]])
                county_name = county_name or union.get("county_name") or ""
                if not (isinstance(locale, int) and locale > 0):
                    locale = union.get("urban_centric_locale")
                notes.append("Enrollment is the total of the union's member districts (NCES 2023)")
        county_name = COUNTY.get(leaid, county_name)
        if r["name"].endswith("Unorganized Territory") and not county_name:
            county_name = {"Louds Island": "Lincoln County"}.get(r["name"][:-22], r["name"][:-22] + " County")
        if leaid == "3620580":
            notes.append("Enrollment is the total of NCES's 32 New York City geographic districts")
        if leaid in SERVES_OTHERS:
            notes.append(SERVES_OTHERS[leaid])
        elif isinstance(enrollment, int) and kids and enrollment > 3 * kids + 200:
            notes.append(f"Enrollment ({enrollment:,}) is far above the {kids:,} school-age children living here, "
                         "likely because the district runs an online or statewide program that enrolls students from elsewhere")
        pct, note = (f"{100 * poor / kids:.8f}%" if kids else ""), ""
        if not kids:
            county = counties.get(ZERO_CHILDREN_COUNTY.get(leaid, ""))
            if county:
                pct = f"{county[0]}%"
                note = (f"No children ages 5-17 live here (Census), so this is the all-ages poverty rate "
                        f"for {county[1]} (Census SAIPE 2024)")
            else:
                note = "No children ages 5-17 live here (Census), so there is no school-age poverty rate"
        note = ". ".join([x for x in [note] + notes if x])
        districts.append({
            "leaid": leaid, "name": r["name"], "state": r["STABREV"], "county": county_name,
            "kids": kids, "poor": poor, "pct": pct, "note": note,
            "enrollment": enrollment if isinstance(enrollment, int) and enrollment >= 0 else "",
            "locale": LOCALE.get(locale // 10, "") if isinstance(locale, int) and locale > 0 else "",
            "nces_name": n.get("lea_name", ""), "lat": n.get("latitude"), "lon": n.get("longitude"),
            "meetings": 0,
        })
    by_id = {d["leaid"]: d for d in districts}
    states = {}
    for d in districts:
        states.setdefault(d["state"], []).append(d)

    places = json.load(open(civic_path))
    report = []
    for p in places:
        state = p["state_name"]
        if state == "West":
            state = "West Virginia"     # CivicSearch cuts this state name short
        abbr = STATE_ABBR.get(state)
        m = re.match(r"District (\d{7})", p["name"])
        match, how = None, ""
        if p.get("query_id") in MANUAL:
            match, how = by_id[MANUAL[p["query_id"]]], "checked by hand"
        elif m and m.group(1) in by_id:
            match, how = by_id[m.group(1)], "federal ID"
        elif abbr in states:
            key = core_key(p["name"])
            cands = [d for d in states[abbr] if key in (core_key(d["name"]), core_key(d["nces_name"] or d["name"]))]
            how = "name"
            if not cands:
                # every CivicSearch word must appear in the district name
                pk = set(tokens(p["name"]))
                cands = [d for d in states[abbr] if pk <= set(tokens(d["name"])) | set(tokens(d["nces_name"] or ""))]
                how = "partial name"
            if cands:
                here = (p.get("latitude"), p.get("longitude"))
                cands.sort(key=lambda d: distance_km(here, (d["lat"], d["lon"])))
                match = cands[0]
                if len(cands) > 1:
                    how += f" (closest of {len(cands)})"
        if match:
            km = distance_km((p.get("latitude"), p.get("longitude")), (match["lat"], match["lon"]))
            match["meetings"] += p["num_meetings"] or 0
            report.append([p["name"], state, p["num_meetings"], match["leaid"], match["name"], how, f"{km:.0f}" if km < 1e8 else ""])
        else:
            report.append([p["name"], state, p["num_meetings"], "", "", "not matched", ""])

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["District", "State", "County", "Available Board Meetings", "Children Ages 5-17", "Children Ages 5-17 in Poverty",
                    "Percentage of Children Ages 5-17 in Poverty", "Locale", "Enrollment", "District ID", "Notes"])
        for d in districts:
            w.writerow([d["name"], d["state"], d["county"], d["meetings"], d["kids"], d["poor"], d["pct"], d["locale"], d["enrollment"], d["leaid"], d["note"]])
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["CivicSearch name", "State", "Meetings", "Matched LEAID", "Matched district (Census name)", "How", "Distance km"])
        w.writerows(sorted(report, key=lambda r: (r[5] != "not matched", r[1], r[0])))
    matched = sum(1 for r in report if r[3])
    print(f"{len(districts)} districts; {matched} of {len(places)} CivicSearch places matched")


TERRITORIES = {"PR", "GU", "VI", "AS", "MP"}

STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}

if __name__ == "__main__":
    main(*sys.argv[1:6])
