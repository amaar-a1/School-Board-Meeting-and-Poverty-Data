"""Turns the Kenya downloads (made on GitHub's runner) into the small inputs build_latam.kenya() reads (data-prep/inputs/kenya/).

- ken_geo.geojson: the 47 counties, from geoBoundaries gbOpen KEN ADM1 (simplified).
- ken_data.json, per county (code 001-047):
  child, child_pop: KNBS, The Kenya Poverty Report 2022 (2024), Annex Table E.2, overall poverty headcount rate of children
    aged 0-17 and their number ('000), 2022;
  poverty, pov_pop: the same report, Table 4.4, overall poverty headcount rate of individuals (all ages) and population ('000), 2022;
  pupils: KNBS, Statistical Abstract 2025, Tables 15.4a (primary, grades 1-6), 15.4b (junior school, grades 7-8) and 15.6
    (secondary), enrolment by county, 2024 (provisional); public and private schools together;
  pop, area: English Wikipedia, "Counties of Kenya" (2019 census population; area);
  meetings: the county assembly's YouTube channel (fetch/nyt.py, KE).
Usage: python3 data-prep/prep_kenya.py RAWDIR GEODIR
"""
import glob, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs", "kenya")
key = lambda s: re.sub(r"[^a-z]", "", s.lower().replace("city", ""))[:6]   # "Elgeyo/" (wrapped) and "Elgeyo-Marakwet" both give "elgeyo"


def find(raw, pat):
    return sorted(glob.glob(os.path.join(raw, "**", pat), recursive=True))[-1]


def text(pdf):
    return subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout


def rows_between(t, start, stop, ncol):
    """Rows of 'Name  n n n ...' between two headings; names may wrap onto the next line ("Elgeyo/Marak-" / "wet")."""
    out, on, carry = {}, False, ""
    for line in t.splitlines():
        if start in line: on = True; continue
        if on and stop and stop in line and not line.strip().startswith("Table 15.4a"): on = False
        if not on: continue
        m = re.match(r"\s*([A-Z][^\d]+?)\s{2,}([\d.,*\s]+)$", line)
        if m:
            nums = [float(x.replace(",", "")) for x in re.findall(r"[\d][\d,]*\.?\d*", m.group(2))]
            if len(nums) >= ncol: out[key(carry + m.group(1))] = nums; carry = ""
            continue
        m = re.match(r"\s*([A-Z][A-Za-z'/\-]+-)\s+[\d.]", line)   # a name broken with a hyphen
        if m: carry = ""
    return out


def main(raw, geo):
    pov = text(find(raw, "ke_poverty_2022.pdf"))
    abs_ = text(find(raw, "ke_abstract_2025.pdf"))
    t44 = rows_between(pov, "Table 4.4: Overall poverty rates (individuals) by residence and county, 2022", "Table 4.5", 6)
    # Annex E.2 runs over several pages, each headed "Annex Table E.2"; rows have 15 numbers
    e2 = {}
    for part in re.split(r"Annex Table E\.2", pov)[2:]:
        part = part.split("Annex Table F")[0]
        for line in part.splitlines():
            m = re.match(r"\s*([A-Z][A-Za-z'/\- ]+?)\s{2,}([\d.,\s]+)$", line)
            if m:
                nums = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*\.?\d*", m.group(2))]
                if len(nums) == 15: e2[key(m.group(1))] = nums
    pri = rows_between(abs_, "Table 15.4a: Primary School Enrolment by County", "Table 15.4b", 6)
    jun = rows_between(abs_, "Table 15.4b: Junior School Enrolment by County", "Table 15.5", 2)
    sec = rows_between(abs_, "Table 15.6: Secondary Schools Enrolment by County", "Table 15.7", 7)
    cl = lambda c: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>|\[\w+\]", "", c))).strip()
    s = open(find(raw, "w_ke.html"), encoding="utf-8").read()
    counties = []
    for tb in re.findall(r"<table.*?</table>", s, re.S):
        rows = [[cl(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)] for r in re.findall(r"<tr.*?</tr>", tb, re.S)]
        if rows and rows[0][:2] == ["Code", "County"]:
            prov = ""
            for r in rows[1:]:
                if not re.match(r"\d{1,3}$", r[0]): continue
                if not re.match(r"[\d,]+(\.\d+)?$", r[2]): prov = r[2]   # the former province, given on its first county only
                nums = [c for c in r[2:] if re.match(r"[\d,]+(\.\d+)?$", c)]   # area, 2009 pop, 2019 pop (the former province may be in between)
                counties.append({"code": f"{int(r[0]):03d}", "name": r[1].replace("–", "-"), "area": float(nums[0].replace(",", "")), "pop": int(nums[2].replace(",", "")), "province": prov})
    assert len(counties) == 47
    data, miss = {}, []
    for c in counties:
        k = key(c["name"])
        x = {"name": c["name"], "pop": c["pop"], "area": c["area"], "province": c["province"]}
        if k in e2: x["child"], x["child_pop"] = e2[k][12], round(e2[k][14] * 1000)
        if k in t44: x["poverty"], x["pov_pop"] = t44[k][0], round(t44[k][4] * 1000)
        p = [d[k][-1] if k in d else None for d in (pri, jun, sec)]
        if None not in p: x["pupils"] = round(sum(p))
        for f in ("child", "poverty", "pupils"):
            if f not in x: miss.append((c["name"], f))
        data[c["code"]] = x
    g = {key(f["properties"]["shapeName"]): f for f in json.load(open(os.path.join(geo, "geoBoundaries-KEN-ADM1_simplified.geojson"), encoding="utf-8"))["features"]}
    rnd = lambda c: [rnd(v) for v in c] if isinstance(c[0], list) else [round(c[0], 4), round(c[1], 4)]
    feats = [{"type": "Feature", "properties": {"id": f"KEN-{code}", "NAME": x["name"]}, "geometry": {"type": g[key(x["name"])]["geometry"]["type"], "coordinates": rnd(g[key(x["name"])]["geometry"]["coordinates"])}}
             for code, x in data.items() if key(x["name"]) in g]
    os.makedirs(OUT, exist_ok=True)
    json.dump(data, open(os.path.join(OUT, "ken_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"type": "FeatureCollection", "features": feats}, open(os.path.join(OUT, "ken_geo.geojson"), "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(len(data), "counties;", len(feats), "borders; missing", miss, "; pupils", sum(x.get("pupils", 0) for x in data.values()),
          "; child range", min(x["child"] for x in data.values() if "child" in x), max(x["child"] for x in data.values() if "child" in x))


if __name__ == "__main__":
    main(*sys.argv[1:])
