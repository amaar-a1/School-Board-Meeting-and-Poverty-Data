"""Turns Belgium's raw downloads into the small input build_latam.belgium() reads (data-prep/inputs/belgium/be_data.json).

Raw files (Statbel open data, downloaded on GitHub's runner):
- TU_COM_REFNIS-20250101.xlsx: the municipality codes (REFNIS) with names in Dutch, French and German, and the
  arrondissement and province above each (kept in inputs/belgium/);
- TF_SOC_POP_STRUCT_2025 (summed to be_pop_age_16.json on the runner): population on 1 January 2025 by
  municipality and age;
- TF_PSNL_INC_TAX_MUNTY.xlsx: income tax statistics by municipality (the latest year, 2023, is before the 2025
  mergers, so merged municipalities' figures are added up with be_mergers_2025.json).
Usage: python3 data-prep/prep_belgium.py RAWDIR [RAWDIR ...]
"""
import datetime, glob, json, os, re, sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs", "belgium")


def find(dirs, pattern):
    return sorted(f for d in dirs for f in glob.glob(os.path.join(d, pattern)))[-1]


def main(dirs):
    merge = json.load(open(os.path.join(IN, "be_mergers_2025.json")))
    rows = list(openpyxl.load_workbook(os.path.join(IN, "be_TU_COM_REFNIS-20250101.xlsx"), read_only=True).worksheets[0].iter_rows(values_only=True))[1:]
    current = lambda r: (r[7].year if isinstance(r[7], datetime.datetime) else int(str(r[7])[-4:])) == 9999
    units = {str(r[1]): r for r in rows if current(r)}
    out = {}
    for code, r in units.items():
        if str(r[0]) != "4": continue
        arr = units.get(str(r[2])); prov = units.get(str(arr[2])) if arr else None
        reg = units.get(str(prov[2])) if prov and str(prov[2]) != "-" else (units.get(str(arr[2])) if arr else None)
        out[code] = {"nl": r[5], "fr": r[4], "de": r[3], "arrondissement": arr[5] if arr else "",
                     "province_nl": prov[5] if prov and str(prov[0]) == "2" else "", "province_fr": prov[4] if prov and str(prov[0]) == "2" else "",
                     "region_nl": (reg or prov or [None] * 6)[5] if reg or prov else ""}
    # Brussels has no province: its region stands in
    for code, m in out.items():
        if not m["province_nl"]: m["province_nl"] = m["province_fr"] = "Brussels"
    pop = json.load(open(find(dirs, "be_pop_age_*.json")))
    for code, p in pop.items():
        if code in out: out[code].update({"pop": p["total"], "u18": p["u18"], "pop_year": 2025})
    ws = openpyxl.load_workbook(find(dirs, "be_TF_PSNL_INC_TAX_MUNTY.xlsx"), read_only=True).worksheets[0]
    it = ws.iter_rows(values_only=True); h = next(it); ix = {c: i for i, c in enumerate(h)}
    data = [r for r in it if r[0]]
    year = max(int(r[ix["CD_YEAR"]]) for r in data)
    agg = {}
    for r in data:
        if int(r[ix["CD_YEAR"]]) != year: continue
        c = merge.get(str(r[ix["CD_MUNTY_REFNIS"]]), str(r[ix["CD_MUNTY_REFNIS"]]))
        a = agg.setdefault(c, [0, 0, 0, 0])
        n = lambda k: float(r[ix[k]]) if str(r[ix[k]] or "").replace(".", "", 1).isdigit() else 0.0   # some cells are text, "*" where Statbel suppresses a small count
        a[0] += n("MS_TOT_NET_TAXABLE_INC"); a[1] += n("MS_NBR_NON_ZERO_INC") + n("MS_NBR_ZERO_INC")
        a[2] += n("MS_TOT_RESIDENTS"); a[3] += n("MS_NBR_ZERO_INC")
    for c, a in agg.items():
        if c in out and a[1]:
            out[c].update({"income_per_return": round(a[0] / a[1]), "income_per_resident": round(a[0] / a[2]) if a[2] else None,
                           "zero_income_share": round(100 * a[3] / a[1], 1), "income_year": year})
    # Pupils, Wallonia (with the German-speaking municipalities): IWEPS WalStat on odwb.be, pupils enrolled in the
    # municipality's nursery (2432000) and primary (243300) schools, all networks ("Pas d'école ..." where there's none).
    for ds, key in (("2432000", "nursery"), ("243300", "primary")):
        files = [f for d in dirs for f in glob.glob(os.path.join(d, f"walstat_{ds}.json"))]
        if not files: continue
        for r in json.load(open(files[0])):
            if r.get("type_entite") != "Commune": continue
            c = merge.get(str(r["ins"]), str(r["ins"]))
            v = next((r[k] for k in r if k.startswith("nombre_d_eleves")), None)
            if c in out:
                out[c][key] = out[c].get(key, 0) + (int(v) if str(v).isdigit() else 0)
                out[c]["pupils_year"] = f"{r['periode']}-{str(int(r['periode']) + 1)[2:]}"
    # Pupils, Brussels: IBSA's origin-destination tables (both language communities' schools), 2023-24: the pupils at
    # schools in each Brussels municipality, wherever they live (each column's sum), nursery (6.3.2.2) and primary (6.3.2.3).
    files = [f for d in dirs for f in glob.glob(os.path.join(d, "bx_6.3_enseignement_origine-destination_*.xlsx"))]
    if files:
        norm = lambda t: re.sub(r"[^a-z]", "", str(t).lower().replace("é", "e").replace("è", "e"))
        bx = {norm(re.sub(r"\s*\(.*\)", "", m["fr"])): c for c, m in out.items() if c.startswith("21")}   # "Forest (Bruxelles-Capitale)"
        bx[norm("Bruxelles")] = "21004"
        wb = openpyxl.load_workbook(files[0], read_only=True)
        for sheet, key in (("6.3.2.2", "nursery"), ("6.3.2.3", "primary")):
            rows = list(wb[sheet].iter_rows(values_only=True))
            head = next(i for i, r in enumerate(rows) if r[0] and str(r[0]).startswith("Origine"))
            year = str(rows[2][0]).strip()
            for j, name in enumerate(rows[head]):
                c = bx.get(norm(name)) if j else None
                if not c: continue
                tot = sum(int(r[j]) for r in rows[head + 1:] if r[0] and isinstance(r[j], (int, float)) and not str(r[0]).startswith(("Région", "Total")))
                out[c][key] = tot; out[c]["pupils_year"] = year
    json.dump(out, open(os.path.join(IN, "be_data.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(out), "municipalities;", sum(1 for m in out.values() if m.get("pop")), "with population;", sum(1 for m in out.values() if m.get("income_per_return")), "with income;",
          sum(1 for m in out.values() if "primary" in m), "with pupils")


if __name__ == "__main__":
    main(sys.argv[1:])
