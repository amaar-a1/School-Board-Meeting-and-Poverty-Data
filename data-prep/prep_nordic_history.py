"""Pupils for every year in the same Norwegian and Swedish series the site already uses, for change over time
(fetch round 53), into data-prep/inputs/nordic/no_pupils_history.json and se_pupils_history.json, {municipality code:
{year: pupils}}; build_nordic.py adds them as "Enrollment by year".

- Norway: Statistics Norway table 11980, pupils in compulsory school, all grades, municipal and private schools, 2015-2025.
- Sweden: Kolada N15835, the municipality's resident pupils in förskoleklass to year 9, 2015-2025 (2025 is the file the
  site already uses).
Usage: python3 data-prep/prep_nordic_history.py RAWDIR
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "nordic")


def main(raw):
    d = json.load(open(os.path.join(raw, "no_11980_all.json")))
    ids, size = d["id"], d["size"]; cat = {k: list(d["dimension"][k]["category"]["index"]) for k in ids}
    def val(**sel):
        i = 0
        for k, n in zip(ids, size): i = i * n + cat[k].index(sel[k])
        return d["value"][i]
    no = {}
    for r in cat["KOKkommuneregion0000"]:
        if not re.fullmatch(r"\d{4}", r): continue
        for t in cat["Tid"]:
            v = val(KOKkommuneregion0000=r, KOKeierfh0000="KP", KOKtrinn0000="0", ContentsCode=cat["ContentsCode"][0], Tid=t)
            if v: no.setdefault(r, {})[t] = int(v)
    json.dump(no, open(os.path.join(IN, "no_pupils_history.json"), "w"), separators=(",", ":"), sort_keys=True)
    se = {}
    files = glob.glob(os.path.join(raw, "se_N15835_20??.json")) + [os.path.join(IN, "se_pupils_N15835_2025.json")]
    for f in files:
        for v in json.load(open(f))["values"]:
            t = [x for x in v["values"] if x["gender"] == "T" and x["value"] is not None]
            if t and v["municipality"] != "0000": se.setdefault(v["municipality"], {})[str(v["period"])] = round(t[0]["value"])
    json.dump(se, open(os.path.join(IN, "se_pupils_history.json"), "w"), separators=(",", ":"), sort_keys=True)
    print("Norway", len(no), "municipalities; Sweden", len(se))


if __name__ == "__main__":
    main(sys.argv[1])
