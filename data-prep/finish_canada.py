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
    # Recount from the monthly refresh (refresh_youtube.py) with canada_youtube.py's rules, except where a
    # Meetings figure was set by hand; also the latest meeting date and meetings per year.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from shared_titles import shared_titles
    from meeting_dates import summary as date_summary
    import canada_youtube as cyt
    fresh, dates = shared_titles(), {}
    handset = {r["District ID"] for r in csv.DictReader(open(hand, newline="", encoding="utf-8")) if r.get("Meetings")} if os.path.exists(hand) else set()
    for k, (n, url) in list(counts.items()):
        if url in fresh:
            kept = [t for t in fresh[url] if cyt.MEETING.search(t) and not cyt.NOT.search(t)]
            if k not in handset:
                counts[k] = (len({re.sub(r"\b(part|partie|pt)\s*\d+\b|\(\d\)|[-–|:]\s*$", "", t, flags=re.I).strip().lower() for t in kept}), url)
            dates[k] = date_summary(kept)
    rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
    # Enrolment from each province's figures (data-prep/canada_enrolment.py)
    enr = {}
    ef = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", "canada", "canada_enrolment.csv")
    if os.path.exists(ef):
        enr = {r["District ID"]: r for r in csv.DictReader(open(ef, newline="", encoding="utf-8"))}
    # Hand-entered figures for boards with no provincial file (secondary sources noted)
    xf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", "canada", "canada_enrolment_extra.csv")
    if os.path.exists(xf):
        for r in csv.DictReader(open(xf, newline="", encoding="utf-8")):
            enr.setdefault(r["District ID"], r)
    cols = ["District", "Province", "Board type", "Locale", "Enrollment", "Enrollment year", "Enrollment note", "Available Board Meetings", "Meetings source", "Latest meeting", "Meetings by year", "Children Ages 0-17",
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
            e = enr.get(r["District ID"], {})
            w.writerow({**{c: r.get(c, "") for c in cols}, "Province": NAMES[r["Province"]],
                        "Enrollment": e.get("Enrollment", ""), "Enrollment year": e.get("Enrollment year", ""),
                        "Enrollment note": "; ".join(x for x in [e.get("Enrollment note", ""),
                            "Lloydminster's division reports to both provinces; this is this province's count, which may overlap with the other side's"
                            if "Lloydminster" in r["District"] and e else ""] if x),
                        "Available Board Meetings": n, "Meetings source": url if n else "",
                        "Latest meeting": dates.get(r["District ID"], ("", ""))[0] if n else "", "Meetings by year": dates.get(r["District ID"], ("", ""))[1] if n else "",
                        # Ontario's border file (2015) lists old web addresses, many of them dead.
                        "Website": "" if r["Province"] == "ON" else r.get("Website", "")})
    print(len(rows), "boards;", sum(1 for r in rows if counts.get(r["District ID"], (0,))[0] > 0), "with meetings")


if __name__ == "__main__":
    main(*sys.argv[1:4])
