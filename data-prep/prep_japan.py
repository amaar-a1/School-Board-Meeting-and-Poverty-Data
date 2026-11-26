"""Turns Japan's raw downloads into the small inputs build_latam.japan() reads (data-prep/inputs/japan/).

Raw files (downloaded on GitHub's runner from e-Stat):
- 統計でみる市区町村のすがた2026 (Statistics Bureau, Social and Demographic Statistics, municipal basic data), one
  Excel file per topic: A population (A1101 total, A1301 under 15; 2020 census), B area (B1101), E education
  (E2501 elementary and E3501 lower secondary pupils, 2024), F labour (F1101 labour force, F1107 unemployed; 2020).
- 被保護者調査 (Ministry of Health, Labour and Welfare, survey of welfare recipients), FY2024 final figures,
  table 8 (2-2): welfare recipients summed over the year's monthly reports, by prefecture (its other cities, 市部,
  and its towns and villages, 郡部) and by designated city and core city (listed separately; not in their prefecture's
  figures).
Usage: python3 data-prep/prep_japan.py RAWDIR [RAWDIR ...]
Writes: inputs/japan/jp_municipal.json, jp_welfare_2024.json
"""
import glob, json, os, re, sys
import openpyxl, xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "japan")
WANT = {"A1101": "pop", "A1301": "under15", "B1101": "area", "E2501": "elementary", "E3501": "lower_secondary", "F1101": "labour_force", "F1107": "unemployed"}


def find(dirs, pattern):
    return sorted(f for d in dirs for f in glob.glob(os.path.join(d, pattern)))


def main(dirs):
    os.makedirs(OUT, exist_ok=True)
    mun = {}
    for f in find(dirs, "jp_0000404635*.xls"):
        sh = xlrd.open_workbook(f).sheet_by_index(0)
        cols = {c: WANT[str(sh.cell_value(7, c)).strip()] for c in range(10, sh.ncols) if str(sh.cell_value(7, c)).strip() in WANT}
        if not cols: continue
        for r in range(10, sh.nrows):
            code = str(sh.cell_value(r, 1)).strip()
            if not re.fullmatch(r"\d{5}", code): continue
            m = mun.setdefault(code, {"name": str(sh.cell_value(r, 8)).replace("　", "").strip(), "en": str(sh.cell_value(r, 9)).strip()})
            for c, k in cols.items():
                v = sh.cell_value(r, c)
                m[k] = float(v) if isinstance(v, float) else None
    json.dump(mun, open(os.path.join(OUT, "jp_municipal.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(mun), "places")

    wb = openpyxl.load_workbook(find(dirs, "jp_w_000040417776.xlsx")[0], read_only=True)
    w = {"prefectures": {}, "cities": {}, "year": "FY2024", "note": "yearly sum of monthly counts; divide by 12 for the monthly average"}
    for row in wb.worksheets[0].iter_rows(values_only=True):
        kind, name, total, cities, towns = (row + (None,) * 5)[:5]
        num = lambda v: float(v) if isinstance(v, (int, float)) else None
        if kind == "都道府県": w["prefectures"][name] = {"cities": num(cities), "towns": num(towns), "total": num(total)}
        elif kind and ("指定都市" in kind or "中核市" in kind): w["cities"][name] = {"total": num(total), "kind": "designated city" if "指定都市" in kind else "core city"}
    json.dump(w, open(os.path.join(OUT, "jp_welfare_2024.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(w["prefectures"]), "prefectures;", len(w["cities"]), "designated and core cities")


def history(raw):
    """Pupils (E2501 elementary plus E3501 lower secondary) for every school year since 2000, from the same SSDS
    municipal series (e-Stat statsDataId 0000020205, fetch round 53), into jp_municipal.json's pupil_years. A place's
    series starts after its last change of more than a quarter in a year (a merger: the series is per current code).
    Usage: python3 data-prep/prep_japan.py --history RAWDIR"""
    by = {}
    for code in ("E2501", "E3501"):
        for x in json.load(open(os.path.join(raw, f"jp_ssds_{code}.json"))):
            y = x["time"][:4]
            if y >= "2000" and re.fullmatch(r"\d+", str(x["v"] or "")): by.setdefault(x["area"], {}).setdefault(y, {})[code] = int(x["v"])
    p = os.path.join(OUT, "jp_municipal.json"); mun = json.load(open(p, encoding="utf-8"))
    n = 0
    for code, m in mun.items():
        s = {y: v["E2501"] + v["E3501"] for y, v in by.get(code, {}).items() if len(v) == 2}
        ys = sorted(s); start = 0
        for k in range(1, len(ys)):
            if min(s[ys[k]], s[ys[k - 1]]) > 100 and abs(s[ys[k]] / s[ys[k - 1]] - 1) > 0.25: start = k
        s = {y: s[y] for y in ys[start:]}
        if len(s) > 1: m["pupil_years"] = s; n += 1
    json.dump(mun, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    print(n, "places with pupils by year")


if __name__ == "__main__" and sys.argv[1] == "--history":
    history(sys.argv[2])
elif __name__ == "__main__":
    main(sys.argv[1:])
