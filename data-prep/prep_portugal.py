"""Turns Portugal's INE downloads into the small input build_latam.portugal() reads (data-prep/inputs/portugal/pt_ine.json).

Raw files (downloaded on GitHub's runner from INE's indicator API, www.ine.pt/ine/json_indicador/pindica.jsp):
- 0013420: beneficiaries of the social insertion income (rendimento social de inserção, RSI) per 1,000 people of
  working age, 2025 (Instituto de Informática da Segurança Social);
- 0013417: RSI beneficiaries (number), 2025;
- 0010284: children and young people receiving the family benefit (abono de família), 2022;
- 0012749: median gross declared income per taxpayer (€), 2024;
- 0008273: resident population by age group, 2023 (INE annual estimates).
Municipalities have 7-digit INE codes whose last four digits are the municipality's code (DTMN).
- DGEEC, Regiões em Números 2024/2025 - Educação: ReNE2025_Vol_*_XLSX.zip, pupils by municipality (see pupils()).
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
    pupils(d, out)
    json.dump(out, open(os.path.join(HERE, "inputs", "portugal", "pt_ine.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(len(out), "municipalities")


# Pupils: DGEEC, Regiões em Números 2024/2025, one workbook per municipality in each region's volume (ReNE2025_Vol_*_XLSX.zip),
# sheets "Alunos PP" (public and private) and "Alunos P" (public). Kept: the latest school year's pre-school and basic
# education (1st, 2nd and 3rd cycles). Municipalities are matched by name within their region (Lagoa and Calheta are
# in two regions each).
VOL_REGION = {"Norte": "N", "Centro": "C", "OesteVT": "C", "GLisboa": "L", "PSetubal": "L", "Alentejo": "A", "Algarve": "F", "RAMadeira": "M", "RAAcores": "Z"}


def region_of(code):
    d = code[:2]
    if d in ("31", "32"): return "M"
    if d >= "41": return "Z"
    if d == "08": return "F"
    return None   # mainland: the name is enough (checked below)


def pupils(d, out):
    import io, re, unicodedata, zipfile
    import openpyxl
    norm = lambda t: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode().lower())
    by = {}
    for code, m in out.items():
        by.setdefault(norm(m["name"]), []).append(code)
    by.setdefault(norm("Praia da Vitória"), []).append("4302")   # INE: "Vila da Praia da Vitória"
    num = lambda v: int(v) if isinstance(v, (int, float)) else (int(str(v).replace(" ", "")) if str(v).replace(" ", "").isdigit() else 0)
    found = 0
    for z in sorted(glob.glob(os.path.join(d, "ReNE2025_Vol_*_XLSX.zip"))):
        reg = VOL_REGION[re.search(r"Vol_[IVX]+_([A-Za-z]+)_XLSX", z).group(1)]
        zf = zipfile.ZipFile(z)
        for f in zf.namelist():
            if not f.endswith(".xlsx") or os.path.basename(f).startswith("_"): continue
            wb = openpyxl.load_workbook(io.BytesIO(zf.read(f)), read_only=True, data_only=True)
            res = {}
            for sheet, key in (("Alunos PP", "all"), ("Alunos P", "public")):
                if sheet not in wb.sheetnames: continue
                rows = list(wb[sheet].iter_rows(values_only=True))
                yi = next(i for i, r in enumerate(rows) if r and any(isinstance(c, str) and re.fullmatch(r"\d{4}/\d{2}", c.strip()) for c in r))
                cols = [(j, str(c).strip()) for j, c in enumerate(rows[yi]) if c and re.fullmatch(r"\d{4}/\d{2}", str(c).strip())]
                j, year = cols[-1]
                name = str(rows[yi + 1][0]).strip()
                tot = 0
                for r in rows[yi + 1:]:
                    lab = next((str(c).strip() for c in r[:j] if isinstance(c, str) and c.strip()), "")   # labels are indented by level
                    if lab in ("Educação pré-escolar", "1.º Ciclo", "2.º Ciclo", "3.º Ciclo"): tot += num(r[j])
                res[key] = tot; res["year"] = year; res["name"] = name
            cands = [c for c in by.get(norm(res.get("name", "")), []) if region_of(c) in (None, reg) and (reg not in ("M", "Z", "F") or region_of(c) == reg)]
            if len(cands) == 1:
                out[cands[0]].update({"pupils": res.get("all"), "pupils_public": res.get("public"), "pupils_year": res.get("year")}); found += 1
            else:
                print("  not matched:", res.get("name"), reg, cands)
    print(found, "municipalities with pupils")


if __name__ == "__main__":
    main(sys.argv[1])
