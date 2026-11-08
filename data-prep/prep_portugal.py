"""Turns Portugal's INE downloads into the small input build_latam.portugal() reads (data-prep/inputs/portugal/pt_ine.json).

Raw files (downloaded on GitHub's runner from INE's indicator API, www.ine.pt/ine/json_indicador/pindica.jsp):
- 0013420: beneficiaries of the social insertion income (rendimento social de inserção, RSI) per 1,000 people of
  working age, 2025 (Instituto de Informática da Segurança Social);
- 0013417: RSI beneficiaries (number), 2025;
- 0010284: children and young people receiving the family benefit (abono de família), 2022;
- 0012749: median gross declared income per taxpayer (€), 2024;
- 0008273: resident population by age group, 2023 (INE annual estimates).
Municipalities have 7-digit INE codes whose last four digits are the municipality's code (DTMN).
Usage: python3 data-prep/prep_portugal.py RAWDIR
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(d, v):
    f = sorted(glob.glob(os.path.join(d, f"pt_{v}_*.json")))[-1]
    x = json.load(open(f, encoding="utf-8"))[0]
    year = list(x["Dados"])[0]
    return year, [r for r in x["Dados"][year] if len(r.get("geocod", "")) == 7 and r.get("valor") not in (None, "")]


def main(d):
    out = {}
    for v, key in (("0013420", "rsi_per1000"), ("0013417", "rsi"), ("0010284", "abono_children"), ("0012749", "median_income")):
        y, rows = load(d, v)
        for r in rows:
            m = out.setdefault(r["geocod"][-4:], {"name": r["geodsg"]}); m[key] = float(r["valor"]); m[key + "_year"] = y
    y, rows = load(d, "0008273")
    for r in rows:
        if r.get("dim_3_t") != "HM": continue
        m = out.setdefault(r["geocod"][-4:], {"name": r["geodsg"]}); a = r["dim_4_t"]; v = float(r["valor"])
        if a == "Total": m["pop"] = v
        elif a in ("0 - 4 anos", "5 - 9 anos", "10 - 14 anos"): m["u18"] = m.get("u18", 0) + v; m["u20"] = m.get("u20", 0) + v
        elif a == "15 - 19 anos": m["u18"] = m.get("u18", 0) + 0.6 * v; m["u20"] = m.get("u20", 0) + v   # 15-17: three fifths
        m["pop_year"] = y
    json.dump(out, open(os.path.join(HERE, "inputs", "portugal", "pt_ine.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(out), "municipalities")


if __name__ == "__main__":
    main(sys.argv[1])
