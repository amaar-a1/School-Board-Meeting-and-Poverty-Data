"""Shares of school-age children by region, for estimate_enrollment.py (data-prep/inputs/estimates/*.json).

- France, Italy, Croatia: Eurostat population on 1 January 2024 by 5-year age group for each NUTS 3 region
  (demo_r_pjangrp3), and Eurostat's LAU-NUTS 2024 correspondence (which NUTS 3 region each municipality is in). Single
  ages within a 5-year group are taken as evenly spread (ages 6-13 = four fifths of 5-9 and of 10-14).
- Philippines: the HDX population statistics (PSA projections, 2025) by province, else by region.
Usage: python3 data-prep/prep_enrollment_shares.py EUROSTAT.json LAU-NUTS.xlsx PHL_ADMPOP.xlsx
"""
import json, os, re, sys, unicodedata
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "estimates")
# ages covered, as weights on the 5-year groups Y_LT5, Y5-9, Y10-14, Y15-19
AGES = {"fr_3_10.json": ("FR", (2 / 5, 1, 1 / 5, 0), "3-10"), "it_6_13.json": ("IT", (0, 4 / 5, 4 / 5, 0), "6-13"),
        "hr_7_14.json": ("HR", (0, 3 / 5, 1, 0), "7-14")}


def eurostat(path):
    d = json.load(open(path, encoding="utf-8"))
    ids, size = d["id"], d["size"]
    cat = {k: {v: i for v, i in d["dimension"][k]["category"]["index"].items()} for k in ids}
    names = d["dimension"]["geo"]["category"]["label"]
    def val(geo, age):
        sel = {"freq": "A", "unit": "NR", "sex": "T", "age": age, "geo": geo, "time": "2024"}; i = 0
        for k, n in zip(ids, size): i = i * n + cat[k][sel[k]]
        return d["value"].get(str(i))
    return val, names


def main(es, lau, ph):
    val, names = eurostat(es)
    wb = openpyxl.load_workbook(lau, read_only=True)
    for fn, (cc, w, ages) in AGES.items():
        share, used = {}, {}
        for r in list(wb[cc].iter_rows(values_only=True))[1:]:
            nuts, code = r[0], str(r[1] or "").strip()
            if not nuts or not code: continue
            if nuts not in used:
                g = [val(nuts, a) for a in ("Y_LT5", "Y5-9", "Y10-14", "Y15-19")]; tot = val(nuts, "TOTAL")
                used[nuts] = sum(x * y for x, y in zip(w, g)) / tot if tot and None not in g else None
            if used[nuts]: share[code] = round(used[nuts], 5); used.setdefault("_n_" + nuts, 0)
        lau_nuts = {str(r[1]).strip(): r[0] for r in list(wb[cc].iter_rows(values_only=True))[1:] if r[0] and r[1]}
        json.dump({"ages": ages, "source": "Eurostat demo_r_pjangrp3 (2024) and LAU-NUTS 2024", "share": share,
                   "names": {c: names.get(lau_nuts[c], lau_nuts[c]) for c in share}}, open(os.path.join(OUT, fn), "w", encoding="utf-8"), ensure_ascii=False)
        print(fn, len(share), "municipalities")
    # Philippines: provinces (adm2), else regions (adm1); ages 5-17 = 5-9, 10-14 and three fifths of 15-19
    norm = lambda t: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower())
    wb = openpyxl.load_workbook(ph, read_only=True); out = {}
    for sheet, key in (("phl_admpop_adm1_2025", "ADM1_NAME"), ("phl_admpop_adm2_2025", "ADM2_NAME")):
        it = wb[sheet].iter_rows(values_only=True); h = next(it); ix = {k: i for i, k in enumerate(h)}
        for r in it:
            if not r[ix[key]]: continue
            g = lambda c: (r[ix["F_" + c]] or 0) + (r[ix["M_" + c]] or 0)
            out[norm(r[ix[key]])] = (g("05_09") + g("10_14") + 0.6 * g("15_19")) / r[ix["T_TL"]]
    json.dump({"ages": "5-17", "source": "HDX COD population statistics for the Philippines (PSA projections, 2025)", "share": {k: round(v, 5) for k, v in out.items()}},
              open(os.path.join(OUT, "ph_5_17.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("ph_5_17.json", len(out), "provinces and regions")


if __name__ == "__main__":
    main(*sys.argv[1:4])
