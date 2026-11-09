"""Turns Australia's raw downloads into the small input build_latam.australia() reads (data-prep/inputs/australia/au_data.json).

Raw files (downloaded on GitHub's runner):
- ABS 2021 Census General Community Profile for local government areas (LGA, ASGS 2021): G01 (population by age),
  G02 (medians), G04A (age by single year) and G15 (type of educational institution attending);
- DSS Benefit and Payment Recipient Demographics, quarterly (data.gov.au), sheet "LGA": recipients by payment.
Places: every LGA in the 2021 boundaries except the census's non-places (no usual address, migratory/offshore/shipping).
Usage: python3 data-prep/prep_australia.py CENSUSDIR DSS.xlsx
"""
import csv, glob, json, os, re, sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "australia")
# Working-age income support, the stand-in for poverty.
RENAMED = {"24700": "25250"}   # Merri-bek, called Moreland in the 2021 boundaries
SUPPORT = ("JobSeeker Payment", "Parenting Payment Single", "Parenting Payment Partnered", "Youth Allowance (other)", "Special Benefit")


def table(d, t):
    f = glob.glob(os.path.join(d, f"2021Census_{t}_AUST_LGA.csv"))[0]
    return {r["LGA_CODE_2021"].replace("LGA", ""): r for r in csv.DictReader(open(f, encoding="utf-8-sig"))}


def main(d, dss):
    g01, g02, g04, g15 = table(d, "G01"), table(d, "G02"), table(d, "G04A"), table(d, "G15")
    n = lambda r, k: int(float(r.get(k) or 0))
    out = {}
    for code, r in g01.items():
        if code[1:] in ("9499", "9799"): continue   # no usual address; migratory, offshore and shipping
        e = g15.get(code, {}); a = g04.get(code, {})
        out[code] = {"pop": n(r, "Tot_P_P"), "u18": sum(n(a, f"Age_yr_{i}_P") for i in range(18)),
                     "wa": sum(n(r, k) for k in ("Age_15_19_yr_P", "Age_20_24_yr_P", "Age_25_34_yr_P", "Age_35_44_yr_P", "Age_45_54_yr_P", "Age_55_64_yr_P")),
                     "pupils": n(e, "Primary_Tot_Primary_P") + n(e, "Secondary_Tot_Secondary_P"),
                     "pupils_public": n(e, "Primary_Government_P") + n(e, "Secondary_Government_P"),
                     "median_family_income": n(g02.get(code, {}), "Median_tot_fam_inc_weekly")}
    ws = openpyxl.load_workbook(dss, read_only=True)["LGA"]
    rows = list(ws.iter_rows(values_only=True))
    title = rows[0][0]; hi = next(i for i, r in enumerate(rows) if r and r[0] == "LGA"); h = rows[hi]
    period = re.search(r",\s*(\w+ \d{4})", title).group(1)
    got = 0
    for r in rows[hi + 1:]:
        if not r or not isinstance(r[0], (int, float)): continue
        c = str(int(r[0])); c = RENAMED.get(c, c)
        if c in out:
            v = {h[j]: (r[j] if isinstance(r[j], (int, float)) else 0) for j in range(2, len(h)) if h[j]}
            out[c]["support"] = sum(v.get(k, 0) for k in SUPPORT); out[c]["support_period"] = period
            out[c]["jobseeker"] = v.get("JobSeeker Payment", 0); got += 1
    json.dump(out, open(os.path.join(OUT, "au_data.json"), "w", encoding="utf-8"))
    print(len(out), "LGAs;", got, "with DSS figures;", "missing:", [c for c in out if "support" not in out[c]][:20], period)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
