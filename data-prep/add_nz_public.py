"""Public-school share for New Zealand's regions.

Input: inputs/nz/schools_directory_2026_10.json, the Ministry of Education's schools directory (rolls at 1 October 2026).
Public = state schools. State-integrated schools (mostly Catholic, owned and run with a proprietor), charter schools
(run by a sponsor) and private schools are publicly funded or fee-paying but not run by the state, so they count as
private, the same rule as Ireland, Belgium, the Netherlands and Spain. Each region's state share of its schools' rolls
is applied to the site's Enrollment (July 2025); the combined regions add their parts up.
Adds or refreshes "Public school enrollment" in docs/data/new-zealand.csv. Usage: python3 data-prep/add_nz_public.py
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "docs", "data", "new-zealand.csv")
schools = json.load(open(os.path.join(HERE, "inputs", "nz", "schools_directory_2026_10.json"), encoding="utf-8"))["schools"]
tot, state = {}, {}
for s in schools:
    if s["status"] != "Open": continue
    tot[s["region"]] = tot.get(s["region"], 0) + s["roll"]
    if s["authority"] == "State": state[s["region"]] = state.get(s["region"], 0) + s["roll"]
rows = list(csv.DictReader(open(P, encoding="utf-8"))); cols = list(rows[0].keys())
if "Public school enrollment" not in cols: cols.insert(cols.index("Enrollment year") + 1, "Public school enrollment")
for r in rows:
    parts = [p.strip() for p in r["District"].split("/")]
    assert all(p in tot for p in parts), parts
    share = sum(state.get(p, 0) for p in parts) / sum(tot[p] for p in parts)
    r["Public school enrollment"] = round(int(r["Enrollment"]) * share) if r["Enrollment"] else ""
    print(f"{r['District']}: {100 * share:.1f}% state")
w = csv.DictWriter(open(P, "w", newline="", encoding="utf-8"), fieldnames=cols); w.writeheader(); w.writerows(rows)
