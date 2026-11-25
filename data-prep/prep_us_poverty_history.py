"""US school districts' child poverty for earlier years, for change over time: data-prep/inputs/us_poverty_history.json,
{District ID: {year: percent of children 5-17 in poverty}}.

Census Bureau, Small Area Income and Poverty Estimates (SAIPE), school district files ussdYY.txt (fixed width: state
FIPS, district code, name, total population, relevant children 5-17, relevant children 5-17 in poverty), 2019-2023,
from https://www2.census.gov/programs-surveys/saipe/datasets/YYYY/YYYY-school-districts/, and the 2024 file the site
already uses (inputs/ussd24.csv). build_national.py adds them as the "Poverty by year" column, and each district's
total population from the same files (us_population_history.json) as "Population by year".
Usage: python3 data-prep/prep_us_poverty_history.py RAWDIR
"""
import csv, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(raw):
    out, pop = {}, {}
    for f in sorted(glob.glob(os.path.join(raw, "ussd??.txt"))):
        y = "20" + re.search(r"ussd(\d\d)\.txt$", f).group(1)
        for line in open(f, encoding="latin-1"):
            m = re.match(r"^(\d\d) (\d{5}) .*?\s(\d+)\s+(\d+)\s+(\d+)\s+ussd", line)
            if m and int(m.group(3)) > 0: pop.setdefault(m.group(1) + m.group(2), {})[y] = int(m.group(3))
            if m and int(m.group(4)) > 0:
                out.setdefault(m.group(1) + m.group(2), {})[y] = round(100 * int(m.group(5)) / int(m.group(4)), 1)
    for r in csv.DictReader(open(os.path.join(HERE, "inputs", "ussd24.csv"), encoding="latin-1")):
        if int(r["rpopall_24"] or 0) > 0: pop.setdefault(r["state"].zfill(2) + r["distid"].zfill(5), {})["2024"] = int(r["rpopall_24"])
        k = int(r["rpop5_17v_24"] or 0)
        if k > 0: out.setdefault(r["state"].zfill(2) + r["distid"].zfill(5), {})["2024"] = round(100 * int(r["saepov5_17rv_24"]) / k, 1)
    json.dump(out, open(os.path.join(HERE, "inputs", "us_poverty_history.json"), "w"), separators=(",", ":"))
    # The same files' total population (all ages) of each district, for the Population by year column.
    json.dump(pop, open(os.path.join(HERE, "inputs", "us_population_history.json"), "w"), separators=(",", ":"))
    print(len(out), "districts;", sum(1 for v in out.values() if len(v) >= 2), "with two or more years")


if __name__ == "__main__":
    main(*sys.argv[1:])
