"""Public schools' share for US districts with no NCES pupil count of their own.

NCES counts pupils at each district's public schools, so a district that runs no schools (Maine's unorganized
territories, New Hampshire's and Vermont's tuition towns, which pay for their children to attend schools elsewhere,
public or private academies) has no count and no public share. For those, the Census Bureau's American Community
Survey gives how many children living there attend public and private school (kindergarten to grade 12, 2019-2023
average; table B14002), saved in inputs/us_acs_public_private.json. Written into "Public school enrollment" and
"Private school enrollment (within its borders)", with "Public share source" saying where it's from, so the map's
public-share colouring and tooltip show it. Districts with an NCES count keep theirs.

Run after build_national.py and estimate_enrollment.py (the daily US refresh runs it):
  python3 data-prep/fill_us_public.py [docs/data/national.csv]
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "inputs", "us_acs_public_private.json")
COL = "Public share source"
PRIV = "Private school enrollment (within its borders)"
TEXT = "2023 American Community Survey (2019–2023 average): children living there in public and private school, kindergarten to grade 12; it runs no schools NCES counts"


def num(v):
    try: return float(str(v).replace(",", ""))
    except (TypeError, ValueError): return None


def main(path=os.path.join(HERE, "..", "docs", "data", "national.csv")):
    if not os.path.exists(SRC):
        print("no ACS file; nothing filled"); return
    acs = json.load(open(SRC, encoding="utf-8"))["districts"]
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    cols = list(rows[0].keys())
    if COL not in cols: cols.insert(cols.index(PRIV) + 1, COL)
    n = 0
    for r in rows:
        if r.get(COL):   # filled before: filled again from the current file
            r["Public school enrollment"] = r[PRIV] = r[COL] = ""
        counted = num(r.get("Enrollment")) and not r.get("Enrollment estimated")
        a = acs.get(r["District ID"])
        if counted or not a or (a["public"] + a["private"]) <= 0:
            r.setdefault(COL, ""); continue
        r["Public school enrollment"], r[PRIV], r[COL] = a["public"], a["private"], TEXT
        n += 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(rows)
    print(n, "districts given a public share from the ACS")


if __name__ == "__main__":
    main(*sys.argv[1:2])
