"""Public-school share for British Columbia's school districts.

BC has one board per school district (plus the province-wide francophone board), and every school number starts with
its district's number, independent schools included. So each district gets:
- "Public school enrollment": the board's own pupils (its Enrollment);
- "Private school enrollment (within its borders)": pupils at independent schools in the district, 2025/26
  (inputs/canada/bc_independent_pupils_2025_26.json, from BC's Student Headcount by Grade; independent online
  schools, which teach across the province, are left out).
Francophone board (CSF) pupils living in the district are counted by neither, so the share is a little low or high.
Other provinces have overlapping public, Catholic and francophone boards, so they get no figure.
Usage: python3 data-prep/add_canada_public.py (run after the Canada build and estimate_enrollment.py)
"""
import csv, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "docs", "data", "canada.csv")
PUB, PRIV = "Public school enrollment", "Private school enrollment (within its borders)"
ind = json.load(open(os.path.join(HERE, "inputs", "canada", "bc_independent_pupils_2025_26.json")))["independent_by_district"]
rows = list(csv.DictReader(open(P, encoding="utf-8"))); cols = list(rows[0].keys())
for c in (PRIV, PUB):
    if c not in cols: cols.insert(cols.index("Enrollment year") + 1, c)
n = 0
for r in rows:
    m = re.match(r"CA-BC-SD(\d+)$", r["District ID"])
    ok = m and r["Enrollment"] and not r.get("Enrollment estimated")
    r[PUB] = r["Enrollment"] if ok else ""
    r[PRIV] = ind.get(m.group(1), 0) if ok else ""
    n += bool(ok)
w = csv.DictWriter(open(P, "w", newline="", encoding="utf-8"), fieldnames=cols); w.writeheader(); w.writerows(rows)
print(n, "BC districts with public and independent pupils")
