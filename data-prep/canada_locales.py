"""Gives Canada's province- and territory-wide boards a locale like the other boards': the locale where most
of the province's children live, from the other boards in that province (children aged 0-17). Where the
province-wide boards are the only ones (Prince Edward Island, Newfoundland and Labrador, the Yukon, Nunavut),
they're rural: all four are far below the urban density cutoffs.

finish_canada.py calls it on docs/data/canada.csv; or run: python3 data-prep/canada_locales.py docs/data/canada.csv
"""
import csv, sys

NOTE = "Serves the whole province or territory; its locale is where most of the province's children live (from the other boards there), or rural where it's the only board"


def apply(path):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    cols = list(rows[0].keys())
    wide = [r for r in rows if r["Locale"] in ("Province-wide", "")]
    kids = {}
    for r in rows:
        if r in wide: continue
        try: k = float(r["Children Ages 0-17"] or 0)
        except ValueError: k = 0
        kids.setdefault(r["Province"], {}).setdefault(r["Locale"], 0)
        kids[r["Province"]][r["Locale"]] += k
    for r in wide:
        by = kids.get(r["Province"])
        r["Locale"] = max(by, key=by.get) if by else "Rural"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    return {r["District"]: (r["Province"], r["Locale"]) for r in wide}


if __name__ == "__main__":
    for k, v in apply(sys.argv[1] if len(sys.argv) > 1 else "docs/data/canada.csv").items(): print(f"{k} ({v[0]}): {v[1]}")
