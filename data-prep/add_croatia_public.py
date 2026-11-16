"""Public-school share for Croatia's cities and municipalities.

Input: inputs/croatia/hr_primary_schools_2025.json, the education ministry's list of every primary school with its
founder (osnivač), from data.gov.hr (May 2025). Public schools are founded by a town, municipality, county or ministry;
the 27 others are founded by an association, a church body, a company or a person. The list counts schools, not
pupils, so only places with no privately founded primary school get a figure: 100% public. The 12 places with one
(Zagreb, Split, Rijeka, Osijek, Zadar, Šibenik, Varaždin, Požega, Virovitica, Novska, Samobor, Dugopolje) stay blank.

Croatia's pupil counts are estimates (children aged 7-14), so run this after estimate_enrollment.py.
Adds or refreshes "Public school enrollment" in docs/data/croatia.csv. Usage: python3 data-prep/add_croatia_public.py
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "docs", "data", "croatia.csv")
PLACE = {"Sesvete": "Zagreb"}   # a district of the City of Zagreb

schools = json.load(open(os.path.join(HERE, "inputs", "croatia", "hr_primary_schools_2025.json"), encoding="utf-8"))["schools"]
rows = list(csv.DictReader(open(P, encoding="utf-8"))); cols = list(rows[0].keys())
names = {}
for r in rows: names.setdefault(r["District"], []).append(r)
private = set()
for s in schools:
    if s["public"]: continue
    place = PLACE.get(s["place"], s["place"])
    assert len(names.get(place, [])) == 1, ("private school not placed", s["name"], place)
    private.add(place)
if "Public school enrollment" not in cols: cols.insert(cols.index("Enrollment year") + 1, "Public school enrollment")
for r in rows:
    r["Public school enrollment"] = r["Enrollment"] if r["Enrollment"] and r["District"] not in private else ""
w = csv.DictWriter(open(P, "w", newline="", encoding="utf-8"), fieldnames=cols); w.writeheader(); w.writerows(rows)
print(len(private), "places with a private primary school:", sorted(private))
print(sum(1 for r in rows if r["Public school enrollment"]), "of", len(rows), "at 100% public")
