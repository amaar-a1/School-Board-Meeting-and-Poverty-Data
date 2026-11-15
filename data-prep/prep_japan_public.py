"""Public-school enrollment for Japanese municipalities, from the School Basic Survey (学校基本調査).

Input: inputs/japan/estat_school_basic_2025_pupils_by_municipality.json, built from six e-Stat files: four of the
2025 survey (1 May 2025, released 26 December 2025) plus two for compulsory 9-year schools (義務教育学校): pupils
by municipality at elementary, lower-secondary and compulsory schools, all schools and private schools.
Public = all minus private, so national schools count as public. Secondary 6-year schools are not included.

The site's Enrollment is the 2024 figure, so the 2025 public share (public ÷ all pupils) is applied to it.
Designated cities are one district on the site; the survey lists their wards, which are summed (ward code
1xx goes to the largest city code ending in 0 that is not above it, e.g. Kawasaki's wards 131-137 to 130).
Tokyo's special wards are their own districts. Estimated enrollments get no public figure.
Adds or refreshes "Public school enrollment" in docs/data/japan.csv. Usage: python3 data-prep/prep_japan_public.py
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "docs", "data", "japan.csv")
rows = list(csv.DictReader(open(P, encoding="utf-8"))); cols = list(rows[0].keys())
codes = {r["District ID"][3:]: r for r in rows if r["District ID"].startswith("JP-")}
src = json.load(open(os.path.join(HERE, "inputs", "japan", "estat_school_basic_2025_pupils_by_municipality.json"), encoding="utf-8"))["municipalities"]

tot, priv, unmatched = {}, {}, []
for k, v in src.items():
    code = k
    if code not in codes and k[0:2] != "13" and 100 < int(k[2:]) < 200:   # a ward of a designated city
        cities = [c for c in codes if c[:2] == k[:2] and 100 <= int(c[2:]) <= int(k[2:]) and c.endswith("0")]
        code = max(cities) if cities else k
    if code not in codes: unmatched.append(v["name"]); continue
    tot[code] = tot.get(code, 0) + v.get("el_total", 0) + v.get("ls_total", 0) + v.get("cs_total", 0)
    priv[code] = priv.get(code, 0) + v.get("el_private", 0) + v.get("ls_private", 0) + v.get("cs_private", 0)

if "Public school enrollment" not in cols: cols.insert(cols.index("Enrollment year") + 1, "Public school enrollment")
n = full = 0
for r in rows:
    c, e = r["District ID"][3:], r.get("Enrollment")
    r["Public school enrollment"] = ""
    if e and not r.get("Enrollment estimated") and tot.get(c):
        r["Public school enrollment"] = round(int(e) * (tot[c] - priv[c]) / tot[c]); n += 1; full += priv[c] == 0
w = csv.DictWriter(open(P, "w", newline="", encoding="utf-8"), fieldnames=cols); w.writeheader(); w.writerows(rows)
print(n, "of", len(rows), "with a public figure;", full, "at 100%; survey entries not matched:", len(unmatched), unmatched[:10])
for r in rows:
    if r["Public school enrollment"] == "" and r.get("Enrollment") and not r.get("Enrollment estimated"): print("no survey match:", r["District"])
