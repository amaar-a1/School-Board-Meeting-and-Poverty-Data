"""Make docs/data/canada.csv from build_canada.py's canada.csv and canada_youtube.py's counts.

Usage: python3 data-prep/finish_canada.py canada.csv canada_youtube.csv docs/data/canada.csv
(canada_youtube.csv may be missing; boards then show 0 meetings.)
"""
import csv, os, sys

NAMES = {"AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba", "NB": "New Brunswick", "NL": "Newfoundland and Labrador",
         "NS": "Nova Scotia", "NT": "Northwest Territories", "NU": "Nunavut", "ON": "Ontario", "PE": "Prince Edward Island",
         "QC": "Quebec", "SK": "Saskatchewan", "YT": "Yukon"}


def main(src, yt, dst):
    counts = {}
    if os.path.exists(yt):
        for r in csv.DictReader(open(yt, newline="", encoding="utf-8")):
            if r["Board meetings on YouTube"] not in ("", None):
                counts[r["District ID"]] = (int(r["Board meetings on YouTube"]), r["Channel URL"])
    rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    cols = ["District", "Province", "Board type", "Available Board Meetings", "Meetings source", "Children Ages 0-17",
            "Children Ages 0-17 in Low Income", "Percentage of Children Ages 0-17 in Low Income", "How poverty was calculated",
            "Website", "District ID"]
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            n, url = counts.get(r["District ID"], (0, ""))
            w.writerow({**{c: r.get(c, "") for c in cols}, "Province": NAMES[r["Province"]],
                        "Available Board Meetings": n, "Meetings source": url if n else ""})
    print(len(rows), "boards;", sum(1 for r in rows if counts.get(r["District ID"], (0,))[0] > 0), "with meetings")


if __name__ == "__main__":
    main(*sys.argv[1:4])
