"""Turns the Latvia and Estonia downloads (made on GitHub's runner) into the small inputs build_latam.latvia() and
estonia() read.

Latvia (data-prep/inputs/latvia/):
- lau_LV.geojson: Eurostat GISCO LAU 2024 borders (43 state cities and municipalities);
- lv_data.json, per municipality (LAU code):
  pop, children (0-17): Official Statistics Portal IRD041, population at the start of 2026 by age;
  child_assist: children in households receiving the basic means-tested municipal benefits (guaranteed minimum income
    and housing benefit, set by national rules) during 2025 (PPS040, "Children", "basic benefits"); the wider "means-tested
    benefits" total also counts each council's own extra benefits, which differ a lot between councils;
  pupils, public: pupils in grades 1-12 on 1 October 2025 at every school, and at schools run by the municipality or a
    ministry (Ministry of Education and Science open data, data.gov.lv: "Izglītojamo skaits sadalījumā pa vispārējās
    izglītības programmām", Paklautiba); schools run by a company, association or person count as private.
Estonia (data-prep/inputs/estonia/):
- lau_EE.geojson: GISCO LAU 2024 borders (79 municipalities);
- ee_data.json, per municipality (EHAK code): pop, children (0-17) and age 7-18 from Statistics Estonia RV0240
  (1 January 2026); subsistence-benefit applications granted per 1,000 residents in 2025 (SK410, indicator 5).
Usage: python3 data-prep/prep_baltic.py RAWDIR [RAWDIR ...]
"""
import csv, glob, json, os, re, shutil, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "inputs")


def find(dirs, name):
    return sorted(f for d in dirs for f in glob.glob(os.path.join(d, "**", name), recursive=True))[-1]


def jsonstat(path):
    d = json.load(open(path, encoding="utf-8"))
    ids, size = d["id"], d["size"]
    cats = {k: list(d["dimension"][k]["category"]["index"]) for k in ids}
    labels = {k: d["dimension"][k]["category"]["label"] for k in ids}
    def val(**sel):
        i = 0
        for k, n in zip(ids, size):
            i = i * n + cats[k].index(sel[k]) if k in sel else i * n
        v = d["value"][i]
        return v
    return cats, labels, val


def key(s):
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())


def latvia(dirs):
    out = {}
    lau = json.load(open(find(dirs, "lau_LV.geojson"), encoding="utf-8"))
    shutil.copy(find(dirs, "lau_LV.geojson"), os.path.join(IN, "latvia", "lau_LV.geojson"))
    for f in lau["features"]:
        p = f["properties"]; out[p["GISCO_ID"].replace("_", "")] = {"name": p["LAU_NAME"], "area": p["AREA_KM2"]}
    # Varakļāni municipality joined Madona on 1 July 2025: one place, both borders, Madona's new code for 2026 figures.
    out["LV0038000"]["merged"] = ["LV0055000"]; out["LV0038000"]["area"] += out.pop("LV0055000")["area"]
    alias = {"LV0038001": "LV0038000"}
    cats, labels, val = jsonstat(find(dirs, "lv_ird041.json"))
    for c in cats["AREA"]:
        code = alias.get(c, c)
        if code in out and (c in alias or code not in alias.values()):
            out[code]["pop"] = val(AREA=c, AGE="TOTAL", ContentsCode=cats["ContentsCode"][0], SEX=cats["SEX"][0], TIME=cats["TIME"][0])
            out[code]["children"] = sum(val(AREA=c, AGE=f"Y{a}", ContentsCode=cats["ContentsCode"][0], SEX=cats["SEX"][0], TIME=cats["TIME"][0]) or 0 for a in range(18))
            out[code]["pop_year"] = cats["TIME"][0]
    cats, labels, val = jsonstat(find(dirs, "lv_pps040.json"))
    child = next(k for k, v in labels["RECIPIENT"].items() if v == "Children")
    means = next(k for k, v in labels["ASSISTANCE"].items() if v.strip(". …") == "basic benefits")
    year = cats["TIME"][-1]
    a = lambda c: val(ContentsCode=cats["ContentsCode"][0], RECIPIENT=child, ASSISTANCE=means, AREA=c, TIME=year) or 0
    for code in cats["AREA"]:
        if code in out:
            out[code]["child_assist"] = a(code)
            out[code]["assist_year"] = year
    # Madona during 2025: before the merger (with Varakļāni, still separate) and after it; the larger of the two
    # (a child helped in both halves of the year is counted once).
    out["LV0038000"]["child_assist"] = max(a("LV0038000") + a("LV0055000"), a("LV0038001"))
    names = {key(v["name"]): k for k, v in out.items()}
    num = lambda v: int(v) if str(v).strip().isdigit() else 0
    for r in csv.DictReader(open(find(dirs, "lv_pupils_by_school_20251001.csv"), encoding="utf-8-sig")):
        k = names.get(key(r["Pasvaldiba"])) or ("LV0038000" if key(r["Pasvaldiba"]) == key("Varakļānu novads") else None)
        assert k, r["Pasvaldiba"]
        n = num(r["Kopa_1_12_klase"])
        out[k]["pupils"] = out[k].get("pupils", 0) + n
        if r["Paklautiba"].strip() != "Juridiska vai fiziska persona": out[k]["public"] = out[k].get("public", 0) + n
    json.dump({"pupils_date": "1 October 2025", "data": out}, open(os.path.join(IN, "latvia", "lv_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("Latvia", len(out), "municipalities;", sum(1 for v in out.values() if "pupils" in v), "with pupils;", sum(1 for v in out.values() if v.get("child_assist") is not None), "with assistance")


def estonia(dirs):
    out = {}
    lau = json.load(open(find(dirs, "lau_EE.geojson"), encoding="utf-8"))
    shutil.copy(find(dirs, "lau_EE.geojson"), os.path.join(IN, "estonia", "lau_EE.geojson"))
    for f in lau["features"]:
        p = f["properties"]; out[str(int(p["GISCO_ID"][3:]))] = {"name": p["LAU_NAME"], "area": p["AREA_KM2"]}
    # Toila rural municipality joined Kohtla-Järve city in 2025 (Statistics Estonia's 2026 figures have Kohtla-Järve
    # under a new code and none for Toila): one place, both borders; its 2025 benefit figures are added up.
    out["321"]["merged"] = ["803"]; out["321"]["area"] += out["803"]["area"]; toila = out.pop("803")
    byname = {}
    for k, v in out.items():
        base = re.sub(r"\s+(vald|linn)$", "", v["name"])
        kind = "city" if v["name"].endswith("linn") else "rural municipality"
        byname[key(base + kind)] = k
        if v["name"] == "Tallinn": byname[key("Tallinn")] = k
    def match(label):
        lab = label.strip(". ")
        if lab in ("Tallinn",): return byname.get(key("Tallinn"))
        return byname.get(key(lab))
    cats, labels, val = jsonstat(find(dirs, "ee_rv0240.json"))
    for code, lab in labels["Elukoht"].items():
        k = match(lab)
        if not k: continue
        sel = dict(Sugu=cats["Sugu"][0], Elukoht=code, Aasta=cats["Aasta"][0])
        out[k]["pop"] = val(Vanus="000", **sel)
        out[k]["children"] = val(Vanus="0-17", **sel)
        out[k]["age7_18"] = sum(val(Vanus=str(a), **sel) or 0 for a in range(7, 19))
        out[k]["pop_year"] = cats["Aasta"][0]
    cats, labels, val = jsonstat(find(dirs, "ee_sk410.json"))
    year = cats["Aasta"][-1]
    apps = lambda code: val(Aasta=year, **{"Piirkond/Haldusüksus": code, "Näitaja": "2"}) or 0
    if "803" in labels["Piirkond/Haldusüksus"]:
        out["321"]["subsistence_per_1000"] = round(1000 * (apps("321") + apps("803")) / out["321"]["pop"], 1)
        out["321"]["subsistence_year"] = year
    county = ""
    for code, lab in labels["Piirkond/Haldusüksus"].items():
        if lab.endswith(" county"): county = lab
        k = match(lab)
        if k: out[k]["county"] = county
        if k and k != "321":
            out[k]["subsistence_per_1000"] = val(Aasta=year, **{"Piirkond/Haldusüksus": code, "Näitaja": "5"})
            out[k]["subsistence_year"] = year
    json.dump({"data": out}, open(os.path.join(IN, "estonia", "ee_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("Estonia", len(out), "municipalities;", sum(1 for v in out.values() if "pop" in v), "with population;", sum(1 for v in out.values() if v.get("subsistence_per_1000") is not None), "with benefits")


if __name__ == "__main__":
    dirs = sys.argv[1:]
    latvia(dirs); estonia(dirs)
