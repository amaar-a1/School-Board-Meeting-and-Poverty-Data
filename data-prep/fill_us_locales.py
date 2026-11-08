"""Gives a locale to the US districts NCES leaves without one (school systems on military bases, districts with
no schools of their own, parts of towns that send their students elsewhere): the most common locale of the
other districts in the same county, or, failing that, in the same state. The note says it's an estimate.

build_national.py calls it after writing docs/data/national.csv; or run:
python3 data-prep/fill_us_locales.py docs/data/national.csv
"""
import csv, sys
from collections import Counter

NOTE = "Locale estimated: NCES gives none, so it's the most common locale of the other districts in {where}"


def apply(path):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    cols = list(rows[0].keys())
    by_county, by_state = {}, {}
    for r in rows:
        if r["Locale"] and NOTE.split(":")[0] not in r["Notes"]:
            by_county.setdefault((r["State"], r["County"]), Counter())[r["Locale"]] += 1
            by_state.setdefault(r["State"], Counter())[r["Locale"]] += 1
    done = 0
    for r in rows:
        if r["Locale"]: continue
        c = by_county.get((r["State"], r["County"]))
        where = f"{r['County']}" if c else f"the state"
        c = c or by_state.get(r["State"])
        if not c: continue
        r["Locale"] = c.most_common(1)[0][0]
        r["Notes"] = "; ".join(x for x in (r["Notes"].rstrip(". "), NOTE.format(where=where)) if x)
        done += 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    return done


if __name__ == "__main__":
    print(apply(sys.argv[1] if len(sys.argv) > 1 else "docs/data/national.csv"), "US districts given an estimated locale")
