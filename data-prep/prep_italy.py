"""Turns Italy's raw downloads into the small inputs build_latam.italy() reads (data-prep/inputs/italy/).

Raw files (downloaded on GitHub's runner; too big to keep here):
- Redditi_e_principali_variabili_IRPEF_su_base_comunale_CSV_2023.csv: Ministry of Economy and Finance, income
  tax returns by comune, tax year 2023 (www1.finanze.gov.it, "Analisi statistiche - dichiarazioni").
- Elenco-comuni-italiani.csv: ISTAT's list of comuni (codes, names, region, province, cadastral code).
- Ministry of Education open data (dati.istruzione.it), 2024-25: pupils by state school (ALUCORSOETASTA) and by
  publicly recognised private school (ALUCORSOINDCLAPAR), with the school directories (SCUANAGRAFESTAT,
  SCUANAGRAFEPAR) that give each school's comune by its cadastral code.

Usage: python3 data-prep/prep_italy.py RAWDIR [RAWDIR ...]   (files are looked for in each)
Writes: inputs/italy/it_comuni.json, it_income_2023.json, it_pupils_2024_25.json
"""
import csv, glob, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "italy")
GRADES = {"SCUOLA PRIMARIA", "SCUOLA SECONDARIA I GRADO"}   # the comune looks after these schools' buildings


def find(dirs, pattern):
    for d in dirs:
        got = sorted(glob.glob(os.path.join(d, pattern)))
        if got: return got[-1]
    raise SystemExit(f"not found: {pattern}")


def main(dirs):
    os.makedirs(OUT, exist_ok=True)
    rd = csv.reader(open(find(dirs, "it_comuni.csv"), encoding="latin-1"), delimiter=";"); next(rd)
    com = {}
    for r in rd:
        com[r[4]] = {"name": r[6], "other": r[7], "region": r[10], "province": r[11], "cat": r[19]}
    json.dump(com, open(os.path.join(OUT, "it_comuni.json"), "w", encoding="utf-8"), ensure_ascii=False)
    cat2istat = {v["cat"]: k for k, v in com.items()}

    rd = csv.reader(open(find(dirs, "it_irpef_*.csv"), encoding="latin-1"), delimiter=";"); h = next(rd)
    num = lambda v: int(v) if v.strip() else 0
    inc = {}
    for r in rd:
        n = num(r[7])
        if not n: continue
        cat2istat.setdefault(r[1], r[2])
        low = num(r[36]) + num(r[38])   # total income at or below zero, or up to 10,000 euros
        # The ministry leaves out small counts: where the 0-10,000 euro bracket itself is blank (4 tiny comuni),
        # there's no figure.
        inc[r[2]] = {"taxpayers": n, "under10k": low if r[38].strip() else None, "share": round(100 * low / n, 2) if r[38].strip() else None,
                     "mean_income": round(num(r[35]) / num(r[34])) if num(r[34]) else None, "year": r[0]}
    json.dump(inc, open(os.path.join(OUT, "it_income_2023.json"), "w", encoding="utf-8"))

    pupils = defaultdict(lambda: {"state": 0, "private": 0})
    for kind, alu, ana in (("state", "it_ALUCORSOETASTA*.csv", "it_SCUANAGRAFESTAT*.csv"), ("private", "it_ALUCORSOINDCLAPAR*.csv", "it_SCUANAGRAFEPAR*.csv")):
        where = {r["CODICESCUOLA"]: r["CODICECOMUNESCUOLA"] for r in csv.DictReader(open(find(dirs, ana), encoding="utf-8", errors="replace"))}
        miss = 0
        for r in csv.DictReader(open(find(dirs, alu), encoding="utf-8", errors="replace")):
            if r["ORDINESCUOLA"] not in GRADES: continue
            n = int(r["ALUNNI"]) if "ALUNNI" in r else int(r["ALUNNIMASCHI"] or 0) + int(r["ALUNNIFEMMINE"] or 0)
            code = cat2istat.get(where.get(r["CODICESCUOLA"], ""))
            if code: pupils[code][kind] += n
            else: miss += n
        print(kind, "pupils not placed in a comune:", miss)
    json.dump(pupils, open(os.path.join(OUT, "it_pupils_2024_25.json"), "w", encoding="utf-8"))
    print(len(com), "comuni;", len(inc), "with income;", len(pupils), "with pupils")


if __name__ == "__main__":
    main(sys.argv[1:])
