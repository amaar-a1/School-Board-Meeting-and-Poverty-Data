"""Make docs/data/canada.csv from build_canada.py's canada.csv and canada_youtube.py's counts.

Usage: python3 data-prep/finish_canada.py canada.csv canada_youtube.csv docs/data/canada.csv
Hand-checked channel fixes in data-prep/inputs/canada_channels.csv are applied on top.
(canada_youtube.csv may be missing; boards then show 0 meetings.)
"""
import csv, os, re, sys

NAMES = {"AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba", "NB": "New Brunswick", "NL": "Newfoundland and Labrador",
         "NS": "Nova Scotia", "NT": "Northwest Territories", "NU": "Nunavut", "ON": "Ontario", "PE": "Prince Edward Island",
         "QC": "Quebec", "SK": "Saskatchewan", "YT": "Yukon"}


def main(src, yt, dst):
    counts = {}
    if os.path.exists(yt):
        for r in csv.DictReader(open(yt, newline="", encoding="utf-8")):
            if r["Board meetings on YouTube"] not in ("", None):
                counts[r["District ID"]] = (int(r["Board meetings on YouTube"]), r["Channel URL"])
    # Hand-checked channels (data-prep/inputs/canada_channels.csv): "none" = no channel; a Meetings
    # figure replaces the search's count.
    hand = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", "canada_channels.csv")
    if os.path.exists(hand):
        for r in csv.DictReader(open(hand, newline="", encoding="utf-8")):
            if r["Channel URL"] == "none":
                counts.pop(r["District ID"], None)
            elif r.get("Meetings"):
                counts[r["District ID"]] = (int(r["Meetings"]), r["Channel URL"])
    rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    cols = ["District", "Province", "Board type", "Locale", "Available Board Meetings", "Meetings source", "Children Ages 0-17",
            "Children Ages 0-17 in Low Income", "Percentage of Children Ages 0-17 in Low Income", "How poverty was calculated",
            "Website", "District ID"]
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            n, url = counts.get(r["District ID"], (0, ""))
            # Lloydminster's two boards serve the city on both sides of the Alberta-Saskatchewan
            # border; each province's border file has its own side, so each side is its own row.
            r["District"] = re.sub(r"l'Ontari$", "l'Ontario", r["District"])   # cut short in Ontario's file
            if "Lloydminster" in r["District"]:
                r["District"] = re.sub(r"^The ", "", r["District"]) + (" (Alberta side)" if r["Province"] == "AB" else " (Saskatchewan side)")
            w.writerow({**{c: r.get(c, "") for c in cols}, "Province": NAMES[r["Province"]],
                        "Available Board Meetings": n, "Meetings source": url if n else "",
                        # Ontario's border file (2015) lists old web addresses, many of them dead.
                        "Website": "" if r["Province"] == "ON" else r.get("Website", "")})
    print(len(rows), "boards;", sum(1 for r in rows if counts.get(r["District ID"], (0,))[0] > 0), "with meetings")


if __name__ == "__main__":
    main(*sys.argv[1:4])
