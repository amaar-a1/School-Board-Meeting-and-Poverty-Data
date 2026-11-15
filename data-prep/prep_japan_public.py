"""Public-school share for Japanese municipalities with no private compulsory school.

MEXT's school code list (文部科学省 学校コード, 1 May 2026, provisional; csv of 25 August 2026) gives every school's
type, establisher (国 national, 公 public, 私 private), status and address. Kept here: elementary (B1), lower
secondary (C1), compulsory 9-year (C2) and secondary 6-year (D2) schools, still open (inputs/japan/
mext_school_codes_2026_compulsory.csv). Each school is placed in a municipality by its address (prefecture, then
an optional county 郡, then the municipality; designated cities whole, Tokyo's wards separately).

The list counts schools, not pupils, so only municipalities with no private compulsory school get a figure: 100%
public (national schools count as public). Municipalities with a private one are left blank.
Adds or refreshes "Public school enrollment" in docs/data/japan.csv. Usage: python3 data-prep/prep_japan_public.py
"""
import csv, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "docs", "data", "japan.csv")
rows = list(csv.DictReader(open(P, encoding="utf-8"))); cols = list(rows[0].keys())
by_pref = {}
for r in rows:
    m = re.search(r"\((.+?)\)\s*$", r["District"])
    if m: by_pref.setdefault(r["District ID"][3:5], {})[m.group(1)] = r["District ID"]
PREF = re.compile(r"^(北海道|東京都|京都府|大阪府|.{2,3}県)")


def place(pref, addr):
    names = by_pref.get(pref, {})
    rest = PREF.sub("", addr.strip(), count=1)
    # an optional county first: "余市郡余市町" (a county name can itself contain 市 or 町)
    for cand in [rest] + [rest[i + 1:] for i, ch in enumerate(rest[:10]) if ch == "郡"]:
        hits = [n for n in names if cand.startswith(n)]
        if hits: return names[max(hits, key=len)]
    return None


private, placed, missed, unplaced_private = set(), 0, [], []
for s in csv.DictReader(open(os.path.join(HERE, "inputs", "japan", "mext_school_codes_2026_compulsory.csv"), encoding="utf-8")):
    if s["本分校"].startswith("9") or s["属性情報廃止年月日"]: continue   # closed
    did = place(s["都道府県番号"][:2], s["学校所在地"])
    if not did:
        missed.append(s["学校所在地"][:20])
        if s["設置区分"].startswith("3"): unplaced_private.append(s["学校所在地"])
        continue
    placed += 1
    if s["設置区分"].startswith("3"): private.add(did)
if "Public school enrollment" not in cols: cols.insert(cols.index("Enrollment year") + 1, "Public school enrollment")
n = 0
for r in rows:
    r["Public school enrollment"] = r["Enrollment"] if r.get("Enrollment") and not r.get("Enrollment estimated") and r["District ID"] not in private else ""
    n += r["Public school enrollment"] != ""
w = csv.DictWriter(open(P, "w", newline="", encoding="utf-8"), fieldnames=cols); w.writeheader(); w.writerows(rows)
print(placed, "open schools placed;", len(missed), "not placed", missed[:8])
print("private schools not placed:", unplaced_private)
print(len(private), "municipalities with a private compulsory school;", n, "of", len(rows), "at 100% public")
