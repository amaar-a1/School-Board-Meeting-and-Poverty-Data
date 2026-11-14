"""Public-school pupils for Norway and Denmark (the map's share of pupils in public schools).

Norway: Statistics Norway table 11980, pupils in compulsory school (all grades), 2025, by municipality:
  "Kommunal" (municipal schools) against "Kommunal og privat" (all schools, the site's Enrollment figure).
  Input: inputs/nordic/no_pupils_K_KP.json.
Denmark: Statistics Denmark LABY23, pupils on 1 October 2025 by municipality and type of school: public basic
  schools (folkeskoler) plus "other schools" (mostly municipal special and youth schools) are public; private
  basic schools (friskoler) and boarding schools (efterskoler) are private. Input: inputs/nordic/dk_LABY23_by_type.csv.
Adds or refreshes "Public school enrollment" in docs/data/norway.csv and denmark.csv. Safe to re-run.
Usage: python3 data-prep/add_nordic_public.py
"""
import csv, json, os, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "nordic")
DOCS = os.path.join(HERE, "..", "docs", "data")
TR = str.maketrans({"ø": "o", "Ø": "o", "æ": "ae", "Æ": "ae", "å": "a", "Å": "a"})


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).translate(TR)).encode("ascii", "ignore").decode().lower()
    return " ".join(s.replace("-", " ").split())


def add(fname, public, key):
    p = os.path.join(DOCS, fname)
    rows = list(csv.DictReader(open(p, encoding="utf-8"))); cols = list(rows[0].keys())
    if "Public school enrollment" not in cols: cols.insert(cols.index("Enrollment year") + 1, "Public school enrollment")
    n = 0
    for r in rows:
        v = public.get(key(r)) if key(r) else None
        r["Public school enrollment"] = v if v is not None and r.get("Enrollment") else ""
        n += r["Public school enrollment"] != ""
    w = csv.DictWriter(open(p, "w", newline="", encoding="utf-8"), fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(fname, n, "of", len(rows), "with public pupils")


# Norway: json-stat2, dimensions region x ownership (K, KP) x grade x contents x year
d = json.load(open(os.path.join(IN, "no_pupils_K_KP.json"), encoding="utf-8"))
reg = d["dimension"]["KOKkommuneregion0000"]["category"]; own = d["dimension"]["KOKeierfh0000"]["category"]["index"]
size = d["size"]; vals = d["value"]
no = {}
for code, i in reg["index"].items():
    k = vals[i * size[1] + own["K"]]
    if k is not None:
        for part in reg["label"][code].replace(" - ", "/").split("/"): no.setdefault(norm(part), int(k))   # "Oslo - Oslove", Sámi names


def no_key(r):
    if r["District"] == "Våler (Viken)": return norm("Våler (Østfold)")   # Viken was split up in 2024
    for part in r["District"].replace(" - ", "/").split("/"):
        if norm(part) in no: return norm(part)
    return None


add("norway.csv", no, no_key)

# Denmark
dk = {}
for r in csv.DictReader(open(os.path.join(IN, "dk_LABY23_by_type.csv"), encoding="utf-8-sig"), delimiter=";"):
    if r["GRUNDSKOL"] in ("Public basic schools", "Other schools"):
        k = norm(r["KOMGRP"]); dk[k] = dk.get(k, 0) + int(r["INDHOLD"])
dk["kobenhavn"] = dk.get("copenhagen")
add("denmark.csv", dk, lambda r: norm(r["District"]))
