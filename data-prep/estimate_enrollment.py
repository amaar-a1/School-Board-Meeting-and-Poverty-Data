"""Estimated enrollment for places with no pupil count: school-age children living there.

Run after any build that rewrites docs/data/*.csv (the daily US refresh runs it too). For every row whose
Enrollment is empty (or 0, where that means "none reported"), it writes an estimate into Enrollment and says so in a
column of its own, "Enrollment estimated" (shown in tooltips, so an estimate is never taken for a count). Rows it
estimated before are estimated again, so it can be re-run. Real counts are never touched.

The estimate is the number of children of the ages the country's enrollment figures cover, from the child counts the
site already has (each rule below says which), or for countries without them, the place's population times its
region's share of those ages (inputs/estimates/*.json, from Eurostat and the HDX population statistics).
Usage: python3 data-prep/estimate_enrollment.py [FILE ...]   (default: every file with a rule)
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, "..", "docs", "data")
EST = os.path.join(HERE, "inputs", "estimates")
FLAG = "Enrollment estimated"


def num(v):
    try: return float(str(v).replace(",", ""))
    except (TypeError, ValueError): return None


def share(name):
    p = os.path.join(EST, name)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def from_column(col, factor, text):
    def rule(r):
        v = num(r.get(col))
        return (round(v * factor), text) if v else None
    return rule


def from_region_share(name, key, text):
    """Population times the share of school-age children in the place's region (inputs/estimates/NAME)."""
    data = share(name)
    def rule(r):
        if not data: return None
        sh, pop = data["share"].get(key(r)), num(r.get("Population"))
        return (round(pop * sh), text.format(region=data.get("names", {}).get(key(r), key(r)))) if sh and pop else None
    return rule


RULES = {
    "national.csv": from_column("Children Ages 5-17", 1, "Estimate: children aged 5–17 living in the district (Census, SAIPE 2024); no enrollment reported to NCES"),
    "canada.csv": from_column("Children Ages 5-17 (2021 Census)", 1, "Estimate: children aged 5–17 living on the reserve (2021 Census); the band-operated school's enrollment isn't published"),
    "japan.csv": from_column("Children under 15", 9 / 15, "Estimate: children aged 6–14 living in the municipality (nine fifteenths of its children under 15)"),
    "iceland.csv": from_column("Children", 10 / 18, "Estimate: children aged 6–15 living in the municipality (ten eighteenths of its children under 18); it has no school of its own"),
    "germany.csv": from_column("Children", 12 / 18, "Estimate: children aged 6–17 living in the district (twelve eighteenths of its children under 18)"),
    "belgium.csv": from_column("Children under 18", 9 / 18, "Estimate: children aged 3–11 living in the municipality (nine eighteenths of its children under 18); it has no school of its own"),
    "islands.csv": from_column("Children Ages 0-14 (estimated)", 9 / 15, "Estimate: children aged 6–14 (nine fifteenths of the estimated children aged 0–14)"),
    "croatia.csv": from_region_share("hr_7_14.json", lambda r: r["District ID"][3:], "Estimate: children aged 7–14 (primary school ages): the place's 2024 population times {region}'s share of those ages (Eurostat, 2024)"),
    "italy.csv": from_region_share("it_6_13.json", lambda r: r["District ID"][3:], "Estimate: children aged 6–13 (primary and lower secondary ages): the comune's 2024 population times {region}'s share of those ages (Eurostat, 2024)"),
    "france.csv": from_region_share("fr_3_10.json", lambda r: r["District ID"][4:], "Estimate: children aged 3–10 (nursery and primary ages) living in the commune: its population times {region}'s share of those ages (Eurostat, 2024); it has no school of its own"),
    "philippines.csv": None,   # set below: by province, else region
    "spain.csv": None,   # set below: census residents in school-level studies plus children aged 3–14
}


def spain_rule():
    data = share("es_pupils.json")
    def rule(r):
        if not data: return None
        x = data["est"].get(r["District ID"][3:])
        return (x, data["text"]) if x else None
    return rule


RULES["spain.csv"] = spain_rule()


def ph_rule():
    import re, unicodedata
    data = share("ph_5_17.json")
    norm = lambda t: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower())
    def rule(r):
        if not data: return None
        pop = num(r.get("Population"))
        prov = r.get("Province", "")
        alias = {"Samar (Western)": "Samar", "Cotabato": "North Cotabato", "Davao de Oro": "Compostela Valley"}   # HDX's names
        for k, what in ((prov, "its province"), (alias.get(prov, ""), "its province"), (re.sub(r"\s*\(.*\)", "", prov), "its province"),
                        (r.get("Region", ""), "its region"), (re.sub(r"\s*\(.*\)", "", r.get("Region", "")), "its region")):
            if not k: continue
            sh = data["share"].get(norm(k))
            if sh and pop: return round(pop * sh), f"Estimate: children aged 5–17 (kindergarten to grade 12 ages): the place's 2021 population times {what}'s share of those ages (PSA projections for 2025, via HDX)"
        return None
    return rule


RULES["philippines.csv"] = ph_rule()


def ee_rule():
    """Estonia: children aged 7-18 living in the municipality (Statistics Estonia RV0240, 1 January 2026)."""
    p = os.path.join(HERE, "inputs", "estonia", "ee_data.json")
    data = json.load(open(p, encoding="utf-8"))["data"] if os.path.exists(p) else {}
    def rule(r):
        x = data.get(str(int(r["District ID"][3:])), {})
        return (x["age7_18"], "Estimate: children aged 7–18 (basic and upper-secondary school ages) living in the municipality, 1 January 2026 "
                              "(Statistics Estonia RV0240); pupil counts by municipality aren't in Estonia's open data") if x.get("age7_18") else None
    return rule


RULES["estonia.csv"] = ee_rule()


def in_rule():
    """India: children aged 6-17 (classes 1-12) living in the district, from WorldPop's 2025 age structures (R2025A,
    1 km, constrained) summed over the district's border by the GitHub runner (fetch rounds 24-26, saved as
    inputs/india/in_ages_2025.json). WorldPop gives five-year groups, so 6-17 is four fifths of 5-9, all of 10-14
    and three fifths of 15-19. UDISE+, India's school census, doesn't answer from outside India."""
    p = os.path.join(HERE, "inputs", "india", "in_ages_2025.json")
    data = json.load(open(p, encoding="utf-8"))["districts"] if os.path.exists(p) else {}
    def rule(r):
        x = data.get(r["District ID"])
        if not x: return None
        v = sum(0.8 * x.get(s + "05", 0) + x.get(s + "10", 0) + 0.6 * x.get(s + "15", 0) for s in "fm")
        return (round(v), "Estimate: children aged 6–17 (classes 1–12) living in the district in 2025, from WorldPop's gridded "
                          "age structures (R2025A); UDISE+, India's school census, couldn't be reached") if v >= 1 else None
    return rule


RULES["india.csv"] = in_rule()


def ages_rule(folder, data_file, frac, ages_text, where):
    """Children of school age from a country's five-year age groups ({"05": n, "10": n, "15": n}) in its data file:
    frac gives the share of each group counted (e.g. 6-17 is four fifths of 5-9, all of 10-14, three fifths of 15-19)."""
    p = os.path.join(HERE, "inputs", folder, data_file)
    data = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    def rule(r):
        a = (data.get(r["District ID"]) or {}).get("ages")
        if not a: return None
        v = sum(frac[g] * a.get(g, 0) for g in frac)
        return (round(v), f"Estimate: children aged {ages_text} living in the {where} in 2025, from WorldPop's gridded age structures (R2025A); "
                          "no pupil count by place could be reached") if v >= 1 else None
    return rule


# Indonesia: school ages 7-18 (SD, SMP, SMA); Paraguay: 6-17 (basic and secondary education).
RULES["indonesia.csv"] = ages_rule("indonesia", "idn_data.json", {"05": 0.6, "10": 1, "15": 0.8}, "7–18", "regency or city")
RULES["paraguay.csv"] = ages_rule("paraguay", "pry_data.json", {"05": 0.8, "10": 1, "15": 0.6}, "6–17", "district")


def my_rule():
    """Malaysia: districts whose education office covers more or less than the district get children aged 7-17 from
    DOSM's 2025 population by age (three fifths of 5-9, all of 10-14, three fifths of 15-19)."""
    p = os.path.join(HERE, "inputs", "malaysia", "my_data.json")
    data = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    def rule(r):
        k = (data.get(r["District ID"]) or {}).get("kids7_17")
        return (k, "Estimate: children aged 7–17 living in the district, 2025 (DOSM population by age); its education office's count covers "
                   "a different area (an office shared with another district, split in two, or older than the district)") if k else None
    return rule


RULES["malaysia.csv"] = my_rule()


def run(fn):
    p = os.path.join(DOCS, fn)
    rule = RULES.get(fn)
    if not rule or not os.path.exists(p): return
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    cols = list(rows[0])
    if FLAG not in cols: cols.append(FLAG)
    n = 0
    for r in rows:
        if r.get(FLAG):   # an earlier estimate: recompute
            r["Enrollment"], r[FLAG] = "", ""
        v = num(r.get("Enrollment"))
        if v:   # a real count
            continue
        got = rule(r)
        if got and got[0] > 0:
            r["Enrollment"], r[FLAG] = got[0], got[1]; n += 1
    if not any(r.get(FLAG) for r in rows): cols.remove(FLAG)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    print(fn, n, "estimated;", sum(1 for r in rows if not num(r.get("Enrollment"))), "still without")


if __name__ == "__main__":
    for fn in sys.argv[1:] or RULES: run(fn)
