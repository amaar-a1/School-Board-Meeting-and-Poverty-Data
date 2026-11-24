"""US school districts' enrollment for earlier years, for change over time: data-prep/inputs/us_enrollment_history.json,
{District ID: {year: pupils}}.

NCES Common Core of Data (CCD), district directory, fall enrollment 2018-2023, through the Urban Institute's Education
Data Portal (educationdata.urban.org/api/v1/school-districts/ccd/directory/YYYY/), downloaded on GitHub's runner (fetch
round 47: us_enr_YYYY.json, {leaid: enrollment}). build_national.py adds the "Enrollment by year" column for districts
whose site enrollment is NCES's own 2023 count (not a total of several districts or an earlier year's figure).
Usage: python3 data-prep/prep_us_enrollment_history.py RAWDIR
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(raw):
    out = {}
    for f in sorted(glob.glob(os.path.join(raw, "us_enr_20??.json"))):
        y = re.search(r"(20\d\d)\.json$", f).group(1)
        for leaid, n in json.load(open(f, encoding="utf-8")).items():
            if isinstance(n, int) and n >= 0: out.setdefault(leaid, {})[y] = n
    json.dump(out, open(os.path.join(HERE, "inputs", "us_enrollment_history.json"), "w"), separators=(",", ":"), sort_keys=True)
    print(len(out), "districts")


if __name__ == "__main__":
    main(*sys.argv[1:])
