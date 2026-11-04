"""Enrolment for each Canadian school board, from each province's own published figures.

Usage: python3 data-prep/canada_enrolment.py RAW_DIR canada_build.csv OUT.csv
RAW_DIR holds the downloaded provincial files (see data-prep/canada.md). Writes District ID,
Enrollment, Enrollment year, Enrollment source for every board it can match.
"""
import csv, re, subprocess, sys, unicodedata
from pathlib import Path

import pandas as pd


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(the|school|division|district|board|no|public|regional|roman|catholic|separate|cdsb|dsb|of|de|du|des|la|le|css|cs|centre|services|scolaire)\b|\d+|[^a-z ]", " ", s)
    return " ".join(s.split())


def main(raw, build, dst):
    raw = Path(raw)
    boards = list(csv.DictReader(open(build, newline="", encoding="utf-8")))
    out, notes = {}, {}
    by_prov = lambda p: [b for b in boards if b["Province"] == p]

    def put(bid, n, year, src):
        if bid and n and n > 0:
            out[bid] = (int(round(n)), year, src)

    # British Columbia: DataBC "BC Schools - Student Headcount by Grade", public schools, district level
    f = raw / "bc_0.xlsx"
    if f.exists():
        bc = pd.read_excel(f, usecols=["SCHOOL_YEAR", "DATA_LEVEL", "PUBLIC_OR_INDEPENDENT", "DISTRICT_NUMBER", "GRADE", "TOTAL_STUDENTS", "FACILITY_TYPE"])
        y = bc.SCHOOL_YEAR.dropna().astype(str).max()
        d = bc[(bc.DATA_LEVEL == "District Level") & (bc.SCHOOL_YEAR.astype(str) == y) & (bc.FACILITY_TYPE == "All Facility Types")
               & (bc.PUBLIC_OR_INDEPENDENT == "Public School") & (bc.GRADE.astype(str) == "All Grades")]
        d = d.assign(n=pd.to_numeric(d.TOTAL_STUDENTS, errors="coerce"))   # small counts are masked as text
        for num, n in d.groupby("DISTRICT_NUMBER").n.sum().items():
            put(f"CA-BC-SD{int(num):02d}", n, y, "BC Ministry of Education, Student Headcount by Grade (DataBC)")
        # the francophone board (CSF, district 93) is in the same file
        csf = [b["District ID"] for b in by_prov("BC") if b["Board type"] == "Francophone"]
        if csf and "CA-BC-SD93" in out:
            out[csf[0]] = out.pop("CA-BC-SD93")
    # Alberta: Student enrolment by authority, 2024/2025 (Alberta Open Data)
    f = raw / "ab_2024_25_0.xlsx"
    if f.exists():
        cur = pd.read_excel(f, dtype={"School Authority Code": str})
        cur = cur[cur["School Authority Code"].notna()]
        y = "2024/2025"
        tot = {int(c): pd.to_numeric(t, errors="coerce") for c, t in zip(cur["School Authority Code"], cur["Total"]) if str(c).strip().isdigit()}
        for b in by_prov("AB"):
            m = re.match(r"CA-AB-(\d+)-", b["District ID"])
            if m and int(m.group(1)) in tot:
                put(b["District ID"], tot[int(m.group(1))], y, "Alberta Education and Childcare, authority enrolment 2024-2025 (Alberta Open Data)")
    # Manitoba: Enrolment Report, school division table (PDF)
    for yr in (2025, 2024):
        f = raw / f"mb_enrolment_{yr}.pdf"
        if not f.exists():
            continue
        txt = subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True).stdout
        part = txt[txt.rindex("Change in School Division Enrolment\u2014"):][:6000]   # the first is in the contents
        names = {norm(b["District"]): b["District ID"] for b in by_prov("MB")}
        for m in re.finditer(r"^\s{2,}([A-Z][A-Za-z.\- ']+?)(?:\s+\d)?\s{2,}([\d,]+)\s+([\d,]+)\s", part, re.M):
            bid = names.get(norm(m.group(1)))
            put(bid, int(m.group(3).replace(",", "")), f"October {yr}", "Manitoba Education, Enrolment Report")
        break
    # Quebec: MEQ, Évolution de l'effectif des CSS et des CS (September 2022)
    f = raw / "qc_evolution.pdf"
    if f.exists():
        txt = subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True).stdout
        for m in re.finditer(r"●\s*(\d{3}) - .+?\s{2,}([\d  ]+?)\s{2,}-?[\d,]+\s*$", txt, re.M):
            put(f"CA-QC-{m.group(1)}000", int(re.sub(r"\D", "", m.group(2))), "September 2022",
                "Quebec Ministry of Education, Évolution de l'effectif des centres de services scolaires et des commissions scolaires")
    # New Brunswick: enrolment by school by grade (GNB open data), summed by district
    f = raw / "nb_0.csv"
    if f.exists():
        nb = pd.read_csv(f)
        ycol, dcol = "School year / Année scolaire", "School District / District scolaire"
        y = sorted(nb[ycol].astype(str).unique(), key=lambda s: s[:4])[-1]
        code = {"ASD-E": "AnglophoneSchoolDistrictEast", "ASD-N": "AnglophoneSchoolDistrictNorth", "ASD-S": "AnglophoneSchoolDistrictSouth",
                "ASD-W": "AnglophoneSchoolDistrictWest", "DSF-NE": "DistrictscolairefrancophoneNordEst",
                "DSF-NO": "DistrictscolairefrancophoneNordOuest", "DSF-S": "DistrictscolairefrancophoneSud"}
        for dist, n in nb[nb[ycol].astype(str) == y].groupby(dcol)["Total / Total"].sum().items():
            put("CA-NB-" + code.get(dist, ""), n, y, "New Brunswick Department of Education, enrolment by school and grade (GNB open data)")
    # Nova Scotia: Public School Enrolment by RCE/CSAP and School (Nova Scotia Open Data)
    f = raw / "ns_enrolment.csv"
    if f.exists():
        ns = pd.read_csv(f)
        y = sorted(ns.SCHOOL_YEAR.astype(str).unique())[-1]
        names = {norm(b["District"]): b["District ID"] for b in by_prov("NS")}
        for reg, n in ns[ns.SCHOOL_YEAR.astype(str) == y].groupby("REG_CENTRE_NAME").ENROLMENT.sum().items():
            put(names.get(norm(reg)), n, y, "Nova Scotia Department of Education, Public School Enrolment by RCE/CSAP and School (Nova Scotia Open Data)")
    # Ontario: School Information and Student Demographics, school enrolment summed by board
    f = raw / "on_sif_2024_25.xlsx"
    if f.exists():
        on = pd.read_excel(f)
        bcol = next(c for c in on.columns if re.search(r"board number", str(c), re.I))
        ecol = next(c for c in on.columns if re.search(r"^enrol", str(c).strip(), re.I))
        on = on.assign(n=pd.to_numeric(on[ecol], errors="coerce"))
        # Ontario's border file numbers boards by SDSB_ID; the ministry by board number (B66052).
        nums = Path(__file__).with_name("inputs") / "canada" / "ontario_board_numbers.csv"
        to_id = {r["Board Number"]: f"CA-ON-{r['SDSB_ID']}" for r in csv.DictReader(open(nums))}
        ncol = next(c for c in on.columns if re.search(r"board name", str(c), re.I))
        tot = on.groupby([bcol, ncol]).n.sum().reset_index()
        print("Ontario boards in the file:", len(tot))
        for _, r in tot.iterrows():
            bid = to_id.get(str(r[bcol]).strip())
            if not bid:
                print("  Ontario board not in the border file (school authorities and provincial schools):", r[ncol])
            put(bid, r["n"], "2024-2025", "Ontario Ministry of Education, School Information and Student Demographics (Ontario Data Catalogue)")
    # Saskatchewan: Active List of Saskatchewan Schools/Programs, K-12 headcount, September 30, 2024
    # (publications.saskatchewan.ca). Schools listed as "<10" count as 5.
    f = Path(__file__).with_name("inputs") / "canada" / "enrolment" / "sk_active_schools_2024.pdf"
    if f.exists():
        txt = subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True).stdout
        tot, small = {}, {}
        for line in txt.splitlines():
            m = re.match(r"^\s*(?:\d+\s+)?(\S.*?)\s+(SD|RCSSD)\s+(\d+)\s{2,}.*?(<10|\d[\d,]*)\s*$", line)
            fr = re.match(r"^\s*(?:\d+\s+)?Conseil des écoles fransaskoises \d+\s{2,}.*?(<10|\d[\d,]*)\s*$", line)
            if m:
                key, v = (m.group(2), int(m.group(3))), m.group(4)
            elif fr:
                key, v = ("CEF", 0), fr.group(1)
            else:
                continue
            tot[key] = tot.get(key, 0) + (5 if v == "<10" else int(v.replace(",", "")))
            small[key] = small.get(key, 0) + (v == "<10")
        src = "Saskatchewan Ministry of Education, Active List of Saskatchewan Schools/Programs (K-12 headcount)"
        for b in by_prov("SK"):
            num = re.search(r"No\. (\d+)", b["District"])
            key = ("CEF", 0) if b["Board type"] == "Francophone" else (("RCSSD" if "Catholic" in b["Board type"] else "SD"), int(num.group(1))) if num else None
            if key in tot:
                put(b["District ID"], tot[key], "September 30, 2024", src)
                if small[key]:
                    notes[b["District ID"]] = f"{small[key]} small school(s) listed as fewer than 10 students are counted as 5 each"
    with open(dst, "w", newline="", encoding="utf-8") as fo:
        w = csv.writer(fo)
        w.writerow(["District ID", "Enrollment", "Enrollment year", "Enrollment source", "Enrollment note"])
        for bid, (n, y, s) in sorted(out.items()):
            w.writerow([bid, n, y, s, notes.get(bid, "")])
    got = {b["Province"] for b in boards if b["District ID"] in out}
    for p in sorted({b["Province"] for b in boards}):
        bs = by_prov(p)
        print(p, sum(b["District ID"] in out for b in bs), "of", len(bs), "| missing:", [b["District"][:40] for b in bs if b["District ID"] not in out][:8])


if __name__ == "__main__":
    main(*sys.argv[1:4])
