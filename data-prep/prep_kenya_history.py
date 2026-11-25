"""Kenya's 2020 county poverty figures, for change over time: adds child_years and pov_years to
data-prep/inputs/kenya/ken_data.json.

KNBS, "Poverty in Kenya - 2020 Report" (2020 Kenya Continuous Household Survey; uploaded by hand, as KNBS's site
refuses GitHub's runner), Table 5.3: by county, the overall poverty headcount rate of the whole population and of
children aged 0-17 (the site's measure, the same as Annex Table E.2 of the 2022 report). Both reports use the cost of
basic needs poverty line, updated for prices, and the 2022 report compares them directly.
Usage: python3 data-prep/prep_kenya_history.py REPORT.pdf
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
key = lambda s: re.sub(r"[^a-z]", "", s.lower().replace("city", ""))


def main(pdf):
    t = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout.split("\n")
    n = [i for i, l in enumerate(t) if "Table 5. 3: Child poverty estimates" in l][-1]
    rows = {}
    for l in t[n:n + 140]:
        if "Table 5. 4" in l: break
        m = re.match(r"^\s*([A-Z][A-Za-z'/\- ]*?[a-z])\s{2,}((?:[\d.,]+\s+){9}[\d.,]+)\s*$", l)
        if m and m.group(1) not in ("National", "Rural", "Urban"):
            v = m.group(2).split(); rows[key(m.group(1))] = (float(v[0]), float(v[8]))   # all ages; children 0-17
    p = os.path.join(HERE, "inputs", "kenya", "ken_data.json"); data = json.load(open(p, encoding="utf-8"))
    miss = []
    for x in data.values():
        r = rows.get(key(x["name"]))
        if not r: miss.append(x["name"]); continue
        x["pov_years"] = {"2020": r[0], "2022": x["poverty"]}; x["child_years"] = {"2020": r[1], "2022": x["child"]}
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(rows), "counties read;", len(data) - len(miss), "matched; missing", miss)


if __name__ == "__main__":
    main(sys.argv[1])
